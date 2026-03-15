# static imports
import requests
from datetime import datetime, timedelta, timezone
from math import pi, sqrt, atan2, degrees, sin, cos
from sgp4.api import Satrec, jday
from sgp4.omm import initialize

# config and helper imports
from config import (
    get_connection,
    CELESTRAK_SOURCES,
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

# build record function
def build_sat_record(satellite_data):
    # create the sat
    satellite_record = Satrec()
    # intitalize the recrod
    initialize(satellite_record, satellite_data)
    # return the record
    return satellite_record

# SGP4 helper
def ecef_to_geodetic(x, y, z):
    a = 6378.137
    f = 1 / 298.257223563
    e2 = 2 * f - f ** 2

    lon = degrees(atan2(y, x))
    p = sqrt(x ** 2 + y ** 2)

    lat = degrees(atan2(z, p * (1 - e2)))

    for _ in range(10):
        lat_rad = lat * pi / 180
        N = a / sqrt(1 - e2 * sin(lat_rad) ** 2)
        lat = degrees(atan2(z + e2 * N * sin(lat_rad), p))

    lat_rad = lat * pi / 180
    N = a / sqrt(1 - e2 * sin(lat_rad) ** 2)

    if abs(lat) > 89.9:
        alt = abs(z) / sin(lat_rad) - N * (1 - e2)
    else:
        alt = p / cos(lat_rad) - N

    return round(lat, 6), round(lon, 6), round(alt, 4)
 
# compute the velocity of the satellite
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
    norad_to_url = {}

    # go through each soruce 
    for source in CELESTRAK_SOURCES:
        print(f"[CelesTrak] Fetching {source['source']}...")
        # get the data from the source
        try:
            response = requests.get(source['url'], timeout=30)
            response.raise_for_status()
            sats = response.json()
            print(f"[CelesTrak] Got {len(sats)} satellites from {source['source']}")

            # map the orad id to the url
            for sat in sats:
                nid = str(sat.get('NORAD_CAT_ID', ''))
                # map norad_id to source url on first encounter
                if nid not in norad_to_url:
                    norad_to_url[nid] = source['url']

            all_sats.extend(sats)
        # if we cant fetch our data
        except Exception as e:
            print(f"[CelesTrak] Failed to fetch {source['source']}: {e}")
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
    return unique, norad_to_url
 
# add the satellite
def insert_satellite(cursor, sat_data, dataset_id):
    norad_id = str(sat_data.get('NORAD_CAT_ID', ''))
 
    # return existing satellite_id if already inserted
    existing = get_satellite_id(cursor, norad_id)

    # if the satellite exists return
    if existing:
        return existing
 
    # use our curated name if available otherwise use CelesTrak name
    name = NAME_MAP.get(norad_id, sat_data.get('OBJECT_NAME', 'Unknown'))
 
    # insert the satellite into the table
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
            f"",
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
 
    # insert the trajectory row
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
 
def run():
    print("\n[CelesTrak] Starting ingestion...")

    # fetch and deduplicate as before
    all_satellites, norad_to_url = fetch_all_satellites()

    # get the target satellites
    target_sats = [
        sat for sat in all_satellites
        if str(sat.get('NORAD_CAT_ID', '')) in ALL_NORAD_IDS
    ]
    print(f"[CelesTrak] Matched {len(target_sats)} of {len(ALL_NORAD_IDS)} target satellites")

    # if we dont find a target satellite
    if not target_sats:
        print("[CelesTrak] No target satellites found — check NORAD IDs in config.py")
        return

    # get the connection and cursor
    conn = get_connection()
    cursor = conn.cursor()

    # create one dataset record per source
    dataset_map = {}

    # iterate through each source
    for source in CELESTRAK_SOURCES:
        # ensure there is a dataset
        dataset_id = ensure_dataset(
            cursor,
            source = source['source'],
            name = source['name'],
            description = source['description'],
            url = source['url'],
            frequency = source['frequency'],
        )
        # map the source url to the id
        dataset_map[source['url']] = dataset_id
        print(f"[CelesTrak] Dataset '{source['source']}' ID: {dataset_id}")

    conn.commit()

    # build list of timestamps
    now = datetime.now(timezone.utc)
    timestamps = [
        now - timedelta(hours=h)
        for h in range(0, HISTORY_DAYS * 24, INTERVAL_HOURS)
    ]
    print(f"[CelesTrak] Computing {len(timestamps)} trajectory snapshots per satellite")

    # process each satellite
    for sat_data in target_sats:
        norad_id = str(sat_data.get('NORAD_CAT_ID', ''))
        name = NAME_MAP.get(norad_id, sat_data.get('OBJECT_NAME', 'Unknown'))

        # get correct dataset_id for this satellite
        url = norad_to_url.get(norad_id, CELESTRAK_SOURCES[0]['url'])
        dataset_id = dataset_map[url]

        print(f"[CelesTrak] Processing {name} ({norad_id}) → dataset {dataset_id}")

        satellite_id = insert_satellite(cursor, sat_data, dataset_id)
        conn.commit()

        try:
            sat_record = build_sat_record(sat_data)
        except Exception as e:
            print(f"[CelesTrak] Could not build SGP4 record for {name}: {e}")
            continue

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
            if inserted % 50 == 0:
                conn.commit()

        conn.commit()
        print(f"[CelesTrak] Done {name} — {len(timestamps)} trajectory snapshots")

    cursor.close()
    conn.close()
    print("[CelesTrak] Ingestion complete")
 
 
if __name__ == "__main__":
    run()