# db, http, and threading imports
import json
import logging
import threading
import requests
from datetime import datetime, timedelta, timezone
from math import pi, degrees

from django.db import connection
from sgp4.api import jday
from manage_satellites.trajectory import (
    build_sat_record, ecef_to_geodetic,
    compute_velocity, HISTORY_DAYS, INTERVAL_MINUTES,
)

logger = logging.getLogger('sattrack')

# in-memory cache TTL in hours
CACHE_TTL_HOURS = 2

# module-level memory cache: url -> (data, datetime)
# _cache_lock guards all reads and writes to celestrak_cache across threads
celestrak_cache = {}
_cache_lock = threading.Lock()

# allowed column names per subclass table — used to validate user-supplied field keys
# before they are used as column names in dynamic SQL (prevents column-name injection)
SUBCLASS_ALLOWED_COLUMNS = {
    'earth_science':   frozenset(['instrument', 'data_measured', 'wavelength_band', 'resolution_m', 'data_archive_url', 'mission_status']),
    'oceanic_science': frozenset(['instrument', 'data_measured', 'wavelength_band', 'resolution_m', 'data_archive_url', 'mission_status']),
    'weather':         frozenset(['instrument', 'data_measured', 'coverage_region', 'imaging_channels', 'repeat_cycle_min', 'data_archive_url', 'mission_status']),
    'navigation':      frozenset(['constellation', 'signal_type', 'accuracy_m', 'orbital_slot', 'clock_type']),
    'internet':        frozenset(['coverage', 'frequency_band', 'service_type', 'throughput_gbps', 'altitude_km']),
    'research':        frozenset(['instrument', 'data_measured', 'research_field', 'wavelength_band', 'data_archive_url', 'mission_status']),
}


class RateLimitedError(Exception):
    pass


def fetch_celestrak_cached(url):
    # use UTC consistently so cache TTL comparisons are correct regardless of server timezone
    now = datetime.utcnow()

    # Layer 1: memory cache — lock protects the shared dict from concurrent reads/writes
    with _cache_lock:
        if url in celestrak_cache:
            data, timestamp = celestrak_cache[url]
            if now - timestamp < timedelta(hours=CACHE_TTL_HOURS):
                logger.info(f"[Cache HIT - Memory] {url}")
                return data

    # Layer 2: DB cache (within TTL)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT data, cached_at FROM celestrak_cache WHERE url = %s",
            (url,)
        )
        row = cursor.fetchone()

    if row:
        data_json, cached_at = row
        if now - cached_at < timedelta(hours=CACHE_TTL_HOURS):
            logger.info(f"[Cache HIT - DB] {url}")
            data = json.loads(data_json)
            with _cache_lock:
                celestrak_cache[url] = (data, cached_at)
            return data

    # Layer 3: fetch from CelesTrak
    logger.info(f"[Cache MISS] Fetching from CelesTrak: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except ValueError:
        # CelesTrak returned non-JSON — rate limited; fall back to stale DB cache
        logger.info(f"[Cache STALE] CelesTrak rate limited, using stale DB cache for {url}")
        if row:
            return json.loads(row[0])
        raise RateLimitedError("CelesTrak rate limited")
    except Exception as e:
        raise Exception(f"CelesTrak fetch failed: {str(e)}")

    # persist to both caches
    with _cache_lock:
        celestrak_cache[url] = (data, now)
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO celestrak_cache (url, data, cached_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                data = VALUES(data),
                cached_at = VALUES(cached_at)
        """, (url, json.dumps(data), now))

    return data


# compute the orbit type of a new satellite
def derive_orbit_type(mean_motion, inclination):
    if mean_motion < 1.5:
        return 'GEO'
    elif mean_motion < 6:
        return 'MEO'
    elif inclination > 60 and mean_motion < 3:
        return 'HEO'
    else:
        return 'LEO'


# generate trajectory function
def generate_trajectory_async(satellite_id, dataset_id, tle_data):
    norad_id = tle_data.get('norad_id')
    logger.info(f"[Trajectory] Generating for NORAD {norad_id}...")

    try:
        sat_data = {
            'NORAD_CAT_ID': norad_id,
            'OBJECT_NAME': tle_data.get('name'),
            'OBJECT_ID': tle_data.get('object_id'),
            'INCLINATION': tle_data.get('inclination'),
            'ECCENTRICITY': tle_data.get('eccentricity'),
            'MEAN_MOTION': tle_data.get('mean_motion'),
            'EPOCH': tle_data.get('epoch'),
            'RA_OF_ASC_NODE': tle_data.get('ra_of_asc_node'),
            'ARG_OF_PERICENTER': tle_data.get('arg_of_pericenter'),
            'MEAN_ANOMALY': tle_data.get('mean_anomaly'),
            'BSTAR': tle_data.get('bstar'),
            'CLASSIFICATION_TYPE': tle_data.get('classification', 'U'),
            'EPHEMERIS_TYPE': 0,
            'ELEMENT_SET_NO': 999,
            'MEAN_MOTION_DOT': 0,
            'MEAN_MOTION_DDOT': 0,
            'REV_AT_EPOCH': 0,
        }

        try:
            sat_record = build_sat_record(sat_data)
        except Exception as e:
            logger.warning(f"[Trajectory] SGP4 build error for NORAD {norad_id}: {e}")
            return

        # build the full set of timestamps to compute
        now_utc = datetime.now(timezone.utc)
        start = now_utc - timedelta(days=HISTORY_DAYS)
        timestamps = [
            start + timedelta(minutes=m)
            for m in range(0, HISTORY_DAYS * 24 * 60, INTERVAL_MINUTES)
        ]

        # insert trajectory rows in batches
        inserted = 0
        with connection.cursor() as cursor:
            for ts in timestamps:
                ts_naive = ts.replace(tzinfo=None)
                jd, fr = jday(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)
                e, r, v = sat_record.sgp4(jd, fr)
                if e != 0:
                    continue

                lat, lon, alt = ecef_to_geodetic(r[0], r[1], r[2])
                velocity = compute_velocity(sat_record.no_kozai)

                cursor.execute("""
                    INSERT INTO trajectory (
                        dataset_id, satellite_id, timestamp, velocity,
                        inclination, eccentricity, ra_of_asc_node,
                        arg_of_pericenter, mean_anomaly, mean_motion,
                        bstar, altitude, latitude, longitude
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    dataset_id, satellite_id,
                    ts_naive.strftime('%Y-%m-%d %H:%M:%S'),
                    velocity,
                    round(degrees(sat_record.inclo), 4),
                    round(sat_record.ecco, 7),
                    round(degrees(sat_record.nodeo), 4),
                    round(degrees(sat_record.argpo), 4),
                    round(degrees(sat_record.mo), 4),
                    round(sat_record.no_kozai / (2 * pi) * 86400, 8),
                    round(sat_record.bstar, 8),
                    alt, lat, lon,
                ))
                inserted += 1
                if inserted % 50 == 0:
                    connection.commit()

            connection.commit()
        logger.info(f"[Trajectory] Done NORAD {norad_id} — {inserted} snapshots inserted")

    except Exception as e:
        logger.error(f"[Trajectory] Unexpected error for NORAD {norad_id}: {e}")
    finally:
        connection.close()


# start thread method to start our trajectory update
def start_trajectory_thread(satellite_id, dataset_id, tle_data):
    thread = threading.Thread(
        target=generate_trajectory_async,
        args=(satellite_id, dataset_id, tle_data),
        daemon=True,
    )
    thread.start()
