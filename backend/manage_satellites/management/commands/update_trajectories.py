# imports
import json
import requests
from datetime import datetime, timedelta, timezone
from math import pi, degrees
from django.db import connection
from django.core.management.base import BaseCommand
from sgp4.api import jday
from manage_satellites.trajectory import (
    build_sat_record, ecef_to_geodetic,
    compute_velocity, build_timestamps,
    HISTORY_DAYS, INTERVAL_MINUTES
)

# cache storage time in hours
CACHE_TTL_HOURS = 2


# command class which updates the trajectories of existing satellites
class Command(BaseCommand):
    help = 'Update trajectory data for all satellites using celestrak_cache or fetching fresh data'

    def handle(self, *args, **options):
        start_time = datetime.now()
        self.stdout.write('[Trajectory] Starting update...')

        # Step 1: Get all dataset URLs we need
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT source_url FROM dataset WHERE source_url IS NOT NULL")
            all_urls = [row[0] for row in cursor.fetchall()]
        self.stdout.write(f'[Trajectory] Found {len(all_urls)} dataset URLs')

        # Step 2: Get existing cache entries
        with connection.cursor() as cursor:
            cursor.execute("SELECT url, data, cached_at FROM celestrak_cache")
            cached = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
        self.stdout.write(f'[Trajectory] {len(cached)} URLs already in cache')

        # Step 3: Build satellite TLE map
        sat_map = {}
        now = datetime.now()

        for url in all_urls:
            if url in cached:
                data_json, cached_at = cached[url]
                if now - cached_at < timedelta(hours=CACHE_TTL_HOURS):
                    self.stdout.write(f'[Trajectory] Cache HIT: {url}')
                    sats = json.loads(data_json)
                else:
                    self.stdout.write(f'[Trajectory] Cache STALE — refetching: {url}')
                    sats = self.fetch_and_cache(url)
            else:
                self.stdout.write(f'[Trajectory] Cache MISS — fetching: {url}')
                sats = self.fetch_and_cache(url)

            for sat in sats:
                nid = str(sat.get('NORAD_CAT_ID', ''))
                if nid not in sat_map:
                    sat_map[nid] = sat

        self.stdout.write(f'[Trajectory] Loaded TLE data for {len(sat_map)} satellites')

        if not sat_map:
            self.stdout.write('[Trajectory] No TLE data available — aborting')
            return

        # Step 4: Get all satellites from DB
        with connection.cursor() as cursor:
            cursor.execute("SELECT satellite_id, norad_id, dataset_id FROM satellite")
            satellites = cursor.fetchall()
        self.stdout.write(f'[Trajectory] Found {len(satellites)} satellites in DB')

        # Step 5: Clear old trajectory data
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM trajectory")
        connection.commit()
        self.stdout.write('[Trajectory] Cleared old trajectory data')

        # Step 6: Build timestamps
        now_utc = datetime.now(timezone.utc)
        start   = now_utc - timedelta(days=HISTORY_DAYS)
        timestamps = [
            start + timedelta(minutes=m)
            for m in range(0, HISTORY_DAYS * 24 * 60, INTERVAL_MINUTES)
        ]
        self.stdout.write(f'[Trajectory] Generating {len(timestamps)} snapshots per satellite')

        # Step 7: Process each satellite
        skipped = 0
        failed = 0
        total = 0

        for satellite_id, norad_id, dataset_id in satellites:
            norad_id = str(norad_id)
            sat_data = sat_map.get(norad_id)

            if not sat_data:
                self.stdout.write(f'[Trajectory] NORAD {norad_id} not found in any dataset — skipping')
                skipped += 1
                continue

            try:
                sat_record = build_sat_record(sat_data)
            except Exception as e:
                self.stdout.write(f'[Trajectory] SGP4 build error for NORAD {norad_id}: {e}')
                failed += 1
                continue

            inserted = 0
            with connection.cursor() as cursor:
                for ts in timestamps:
                    ts_naive = ts.replace(tzinfo=None)
                    jd, fr   = jday(
                        ts.year, ts.month, ts.day,
                        ts.hour, ts.minute, ts.second
                    )
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
                        dataset_id,
                        satellite_id,
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

            total += inserted
            self.stdout.write(f'[Trajectory] Done NORAD {norad_id} — {inserted} snapshots')

        # Summary 
        elapsed = (datetime.now() - start_time).seconds
        self.stdout.write('')
        self.stdout.write('========================================')
        self.stdout.write(f'  Trajectory update complete')
        self.stdout.write(f'  Total snapshots inserted : {total}')
        self.stdout.write(f'  Satellites skipped       : {skipped}')
        self.stdout.write(f'  Satellites failed        : {failed}')
        self.stdout.write(f'  Total time               : {elapsed}s')
        self.stdout.write('========================================')

    def fetch_and_cache(self, url):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO celestrak_cache (url, data, cached_at)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        data      = VALUES(data),
                        cached_at = VALUES(cached_at)
                """, (url, json.dumps(data), datetime.now()))
                connection.commit()

            self.stdout.write(f'[Trajectory] Fetched and cached: {url}')
            return data

        except Exception as e:
            self.stdout.write(f'[Trajectory] Failed to fetch {url}: {e}')
            return []