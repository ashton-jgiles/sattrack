# static imports
import requests
from datetime import datetime, timedelta, timezone
from math import pi, sqrt, atan2, degrees
from sgp4.api import Satrec, jday

# config and helper imports
from config import (
    get_connection,
    CELESTRAK_ACTIVE_URL,
    CELESTRAK_URLS,
    ALL_NORAD_IDS,
    ORBIT_TYPE_MAP,
    NAME_MAP,
    HISTORY_DAYS,
    INTERVAL_HOURS,
)
from db_helpers import (
    ensure_dataset,
    get_satellite_id,
    record_exists
)

# SGP4 helpers
def ecef_to_geodetic(x, y, z):

    # constants
    a = 6378.137
    f = 1 / 298.257223563
    e2 = 2 * f - f ** 2
 
    lon = degrees(atan2(y, x))
    p = sqrt(x ** 2 + y ** 2)
 
    # initial estimate
    lat = degrees(atan2(z, p * (1 - e2)))
 
    # iterate for accuracy
    for _ in range(10):
        lat_rad = lat * pi / 180
        N = a / sqrt(1 - e2 * (lat_rad ** 2))
        lat = degrees(atan2(z + e2 * N * (lat * pi / 180), p))
 
    # computed values
    lat_rad = lat * pi / 180
    N = a / sqrt(1 - e2 * (lat_rad ** 2))
    alt = (p / max(abs(lat_rad), 1e-10)) - N
 
    # return the rounded values
    return round(lat, 6), round(lon, 6), round(alt, 4)
 
 
def compute_velocity(mean_motion_rad_per_sec):
    # gravity constant
    GM = 398600.4418 
    # compute the velocity
    n = mean_motion_rad_per_sec
    semi_major = (GM / (n ** 2)) ** (1 / 3)
    return round(sqrt(GM / semi_major), 4)
 
# fetch the satellites
def fetch_all_satellites():
    all_sats = []
    for url in CELESTRAK_URLS:
        print(f"[CelesTrak] Fetching {url}")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            all_sats.extend(response.json())
            print(f"[CelesTrak] Got {len(response.json())} satellites")
        except Exception as e:
            print(f"[CelesTrak] Failed to fetch {url}: {e}")
            continue
 
    # deduplicate by NORAD_CAT_ID
    seen = set()
    unique = []
    for sat in all_sats:
        nid = str(sat.get('NORAD_CAT_ID', ''))
        if nid and nid not in seen:
            seen.add(nid)
            unique.append(sat)
 
    print(f"[CelesTrak] Total unique satellites: {len(unique)}")
    return unique
 
# add the satellite
def insert_satellite(cursor, sat_data, dataset_id):
    norad_id = str(sat_data.get('NORAD_CAT_ID', ''))
 
    # return existing satellite_id if already inserted
    existing = get_satellite_id(cursor, norad_id)
    if existing:
        return existing
 
    # use our curated name if available otherwise use CelesTrak name
    name = NAME_MAP.get(norad_id, sat_data.get('OBJECT_NAME', 'Unknown'))
 
    cursor.execute(
        """
        INSERT INTO satellite (
            name,
            description,
            orbit_type,
            norad_id,
            object_id,
            classification,
            dataset_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            name,
            f"Imported from CelesTrak — {sat_data.get('OBJECT_TYPE', 'PAYLOAD')}",
            ORBIT_TYPE_MAP.get(norad_id, 'LEO'),
            norad_id,
            sat_data.get('OBJECT_ID', ''),
            sat_data.get('CLASSIFICATION_TYPE', 'U'),
            dataset_id,
        )
    )
    return cursor.lastrowid
 
# add the trajectory
def insert_trajectory(cursor, satellite_id, dataset_id, sat_record, timestamp):
    # skip if already exists
    if record_exists(cursor, 'trajectory', {
        'satellite_id': satellite_id,
        'dataset_id':   dataset_id,
        'timestamp':    timestamp.strftime('%Y-%m-%d %H:%M:%S'),
    }):
        return
 
    # compute position using SGP4
    jd, fr = jday(
        timestamp.year,
        timestamp.month,
        timestamp.day,
        timestamp.hour,
        timestamp.minute,
        timestamp.second,
    )
    e, r, v = sat_record.sgp4(jd, fr)
 
    # e != 0 means SGP4 error for this timestamp
    if e != 0:
        return
 
    lat, lon, alt = ecef_to_geodetic(r[0], r[1], r[2])
 
    # mean motion in radians per second for velocity calculation
    velocity = compute_velocity(sat_record.no_kozai)
 
    cursor.execute(
        """
        INSERT INTO trajectory (
            dataset_id,
            satellite_id,
            timestamp,
            velocity,
            inclination,
            eccentricity,
            ra_of_asc_node,
            arg_of_pericenter,
            mean_anomaly,
            mean_motion,
            bstar,
            altitude,
            latitude,
            longitude
        ) VALUES (
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        """,
        (
            dataset_id,
            satellite_id,
            timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            velocity,
            round(degrees(sat_record.inclo), 4),
            round(sat_record.ecco, 7),
            round(degrees(sat_record.nodeo), 4),
            round(degrees(sat_record.argpo), 4),
            round(degrees(sat_record.mo), 4),
            round(sat_record.no_kozai / (2 * pi) * 86400, 8),
            round(sat_record.bstar, 8),
            alt,
            lat,
            lon,
        )
    )
 
 # main running method
def run():
    print("\n[CelesTrak] Starting ingestion...")
 
    # fetch all satellites from CelesTrak
    all_satellites = fetch_all_satellites()
 
    # filter to our curated list
    target_sats = [
        sat for sat in all_satellites
        if str(sat.get('NORAD_CAT_ID', '')) in ALL_NORAD_IDS
    ]
    print(f"[CelesTrak] Matched {len(target_sats)} of {len(ALL_NORAD_IDS)} target satellites")
 
    if not target_sats:
        print("[CelesTrak] No target satellites found — check NORAD IDs in config.py")
        return
 
    # open DB connection
    conn = get_connection()
    cursor = conn.cursor()
 
    # ensure CelesTrak dataset record exists
    dataset_id = ensure_dataset(
        cursor,
        source = 'CelesTrak',
        name = 'CelesTrak Active Satellites',
        description = 'TLE orbital elements for active satellites',
        url = CELESTRAK_ACTIVE_URL,
        frequency = '6h',
    )
    conn.commit()
    print(f"[CelesTrak] Dataset ID: {dataset_id}")
 
    # build list of timestamps to back-compute
    now        = datetime.now(timezone.utc)
    timestamps = [
        now - timedelta(hours=h)
        for h in range(0, HISTORY_DAYS * 24, INTERVAL_HOURS)
    ]
    print(f"[CelesTrak] Computing {len(timestamps)} trajectory snapshots per satellite")
 
    # process each satellite
    for sat_data in target_sats:
        norad_id = str(sat_data.get('NORAD_CAT_ID', ''))
        name = NAME_MAP.get(norad_id, sat_data.get('OBJECT_NAME', 'Unknown'))
 
        print(f"[CelesTrak] Processing {name} ({norad_id})")
 
        # insert satellite record
        satellite_id = insert_satellite(cursor, sat_data, dataset_id)
        conn.commit()
 
        # get TLE lines
        tle_line1 = sat_data.get('TLE_LINE1', '')
        tle_line2 = sat_data.get('TLE_LINE2', '')
 
        if not tle_line1 or not tle_line2:
            print(f"[CelesTrak] No TLE data for {name} — skipping trajectory")
            continue
 
        # build SGP4 satellite record
        sat_record = Satrec.twoline2rv(tle_line1, tle_line2)
 
        # insert trajectory for each timestamp
        inserted = 0
        for timestamp in timestamps:
            insert_trajectory(
                cursor,
                satellite_id,
                dataset_id,
                sat_record,
                timestamp.replace(tzinfo=None),
            )
            inserted += 1
 
            # commit every 50 rows to avoid large transactions
            if inserted % 50 == 0:
                conn.commit()
 
        conn.commit()
        print(f"[CelesTrak] Done {name} — {len(timestamps)} trajectory snapshots")
 
    cursor.close()
    conn.close()
    print("[CelesTrak] Ingestion complete")
 
 
if __name__ == "__main__":
    run()