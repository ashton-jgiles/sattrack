# connection and api imports and rate limiting imports
from django.db import connection, transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from backend.throttles import CelesTrakThrottle
import logging

# imports for creating trajectory after adding new satellite and caching celestrak data
import threading
import json
from datetime import datetime, timedelta, timezone
from math import pi, degrees
from sgp4.api import jday
import requests
from manage_satellites.trajectory import (
    build_sat_record, ecef_to_geodetic, 
    compute_velocity, build_timestamps,
    HISTORY_DAYS, INTERVAL_MINUTES
)

# cache retention hours
CACHE_TTL_HOURS = 2
# create the cache dictionary
celestrak_cache = {}

# create the logger
logger = logging.getLogger('sattrack')

# if we hit the cesltrak rate limt we will continually run this exception
class RateLimitedError(Exception):
    pass

# get stale cache method will return the caeche of data from the database if our celestrak cache in memory has expired
def get_stale_cache(url):
    # try select the data from the database cache from the celestrak url we are using
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT data FROM celestrak_cache WHERE url = %s",
                (url,)
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
    # if no data just pass
    except Exception:
        pass
    # return none
    return None

# if our memory cache is still valid
def fetch_celestrak_cached(url):
    # get the current time
    now = datetime.now()

    # Layer 1: Memory cache
    if url in celestrak_cache:
        data, timestamp = celestrak_cache[url]
        if now - timestamp < timedelta(hours=CACHE_TTL_HOURS):
            logger.info(f"[Cache HIT - Memory] {url}")
            return data

    # Layer 2: DB cache
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
            celestrak_cache[url] = (data, cached_at)
            return data

    # Layer 3: Fetch from CelesTrak
    logger.info(f"[Cache MISS] Fetching from CelesTrak: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except ValueError:
        # CelesTrak returned non-JSON — rate limited
        raise RateLimitedError("CelesTrak rate limited")
    except Exception as e:
        raise Exception(f"CelesTrak fetch failed: {str(e)}")

    # Save to both caches
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

# generate trajectory async function to generate trajectory for a new satellite in the background
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
            logger.info(f"[Trajectory] SGP4 error for NORAD {norad_id}: {e}")
            return

        # Build timestamps
        now_utc = datetime.now(timezone.utc)
        start = now_utc - timedelta(days=HISTORY_DAYS)
        timestamps = [
            start + timedelta(minutes=m)
            for m in range(0, HISTORY_DAYS * 24 * 60, INTERVAL_MINUTES)
        ]

        # Insert trajectory rows
        inserted = 0
        with connection.cursor() as cursor:
            for ts in timestamps:
                ts_naive = ts.replace(tzinfo=None)
                jd, fr = jday(
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
        logger.info(f"[Trajectory] Unexpected error for NORAD {norad_id}: {e}")

# compute the orbit type from celestrak data
def derive_orbit_type(mean_motion, inclination):
    # Mean motion in revs/day
    # GEO: ~1 rev/day, MEO: 2-6, LEO: 11-16, HEO: highly elliptical
    if mean_motion < 1.5:
        return 'GEO'
    elif mean_motion < 6:
        return 'MEO'
    elif inclination > 60 and mean_motion < 3:
        return 'HEO'
    else:
        return 'LEO'

# returns all soft-deleted satellites
class GetDeletedSatellites(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    s.satellite_id, s.name, s.orbit_type, s.norad_id, s.object_id,
                    s.deleted_at,
                    CASE
                        WHEN es.satellite_id IS NOT NULL THEN 'Earth Science'
                        WHEN os.satellite_id IS NOT NULL THEN 'Oceanic Science'
                        WHEN w.satellite_id  IS NOT NULL THEN 'Weather'
                        WHEN n.satellite_id  IS NOT NULL THEN 'Navigation'
                        WHEN i.satellite_id  IS NOT NULL THEN 'Internet'
                        WHEN r.satellite_id  IS NOT NULL THEN 'Research'
                        ELSE 'Unknown'
                    END AS satellite_type
                FROM satellite s
                    LEFT JOIN earth_science  es ON s.satellite_id = es.satellite_id
                    LEFT JOIN oceanic_science os ON s.satellite_id = os.satellite_id
                    LEFT JOIN weather         w  ON s.satellite_id = w.satellite_id
                    LEFT JOIN navigation      n  ON s.satellite_id = n.satellite_id
                    LEFT JOIN internet        i  ON s.satellite_id = i.satellite_id
                    LEFT JOIN research        r  ON s.satellite_id = r.satellite_id
                WHERE s.deleted_at IS NOT NULL
                ORDER BY s.deleted_at DESC
            """)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
        return Response([dict(zip(columns, row)) for row in rows])


# restores a soft-deleted satellite by clearing deleted_at
class RecoverSatellite(APIView):
    def post(self, request, satellite_id):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT satellite_id FROM satellite WHERE satellite_id = %s AND deleted_at IS NOT NULL",
                [satellite_id]
            )
            if not cursor.fetchone():
                return Response({'error': 'Deleted satellite not found'}, status=404)

            cursor.execute(
                "UPDATE satellite SET deleted_at = NULL WHERE satellite_id = %s",
                [satellite_id]
            )
        return Response({'message': 'Satellite recovered successfully'})


# delete satellite data which takes a satellite id and removes all associated data from the database
class DeleteSatellite(APIView):
    def delete(self, request, satellite_id):
        with connection.cursor() as cursor:
            # check satellite exists and is not already deleted
            cursor.execute(
                "SELECT satellite_id FROM satellite WHERE satellite_id = %s AND deleted_at IS NULL",
                [satellite_id]
            )

            if not cursor.fetchone():
                return Response({'error': 'Satellite not found'}, status=404)

            cursor.execute(
                "UPDATE satellite SET deleted_at = NOW() WHERE satellite_id = %s",
                (satellite_id,)
            )

        return Response({'message': 'Satellite deleted successfully'})

# modify satellite class which updates all associated satellite data in the database
class ModifySatellite(APIView):
    def post(self, request):
        satellite = request.data.get('satellite', {})
        communication = request.data.get('communication', {})
        type_data = request.data.get('type_data', {})

        satellite_id = satellite.get('satellite_id')
        if not satellite_id:
            return Response({'error': 'satellite_id is required'}, status=400)

        with connection.cursor() as cursor:

            # Update satellite table 
            cursor.execute("""
                UPDATE satellite
                SET description = %s, classification = %s
                WHERE satellite_id = %s
            """, (
                satellite.get('description'),
                satellite.get('classification'),
                satellite_id,
            ))

            # Update communicates_with table 
            if communication.get('communication_frequency'):
                cursor.execute("""
                    UPDATE communicates_with
                    SET communication_frequency = %s
                    WHERE satellite_id = %s
                """, (
                    communication.get('communication_frequency'),
                    satellite_id,
                ))

            # Update subclass type table 
            subclass_tables = [
                'earth_science', 'oceanic_science', 'weather',
                'navigation', 'internet', 'research'
            ]

            for table in subclass_tables:
                cursor.execute(
                    f"SELECT satellite_id FROM {table} WHERE satellite_id = %s",
                    (satellite_id,)
                )
                if cursor.fetchone():
                    # Build dynamic UPDATE from type_data keys
                    if type_data:
                        set_clause = ", ".join([f"{k} = %s" for k in type_data.keys()])
                        values = list(type_data.values()) + [satellite_id]
                        cursor.execute(
                            f"UPDATE {table} SET {set_clause} WHERE satellite_id = %s",
                            values
                        )
                    break

        return Response({'message': 'Satellite updated successfully'})   

# new satellite from dataset takes a dataset id and return the satellites from celetrak that arent already in our database
class NewSatellitesFromDataset(APIView):
    # apply rate limit
    throttle_classes = [CelesTrakThrottle]

    # get method taking the dataset id and computing values for pages and search for our frontend later
    def get(self, request, dataset_id):
        search = request.GET.get('search', '').strip()
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 50))
        offset = (page - 1) * limit

        with connection.cursor() as cursor:
            # get the dataset source url
            cursor.execute("SELECT source_url FROM dataset WHERE dataset_id = %s", [dataset_id])
            row = cursor.fetchone()
            if not row:
                return Response({'error': 'Dataset not found'}, status=404)
            url = row[0]

            # get all existing NORAD ids in the database
            cursor.execute("SELECT norad_id FROM satellite")
            existing_norad_ids = {str(row[0]) for row in cursor.fetchall()}

        # fetch data from celestrak
        try:
            all_sats = fetch_celestrak_cached(url)
        except RateLimitedError :
            stale = get_stale_cache(url)
            if stale:
                all_sats = stale
            else:
                return Response(
                    {'error': 'CelesTrak rate limit reached. Please try again later.'},
                    status=429
                )
        except Exception as e:
            return Response({'error': f'Failed to fetch CelesTrak data: {str(e)}'}, status=502)
        
        # filter out satellites already in database
        new_sats = [
            sat for sat in all_sats
            if str(sat.get('NORAD_CAT_ID', '')) not in existing_norad_ids
        ]

        # apply search filter
        if search:
            search_lower = search.lower()
            new_sats = [
                sat for sat in new_sats
                if search_lower in sat.get('OBJECT_NAME', '').lower()
                or search_lower in str(sat.get('NORAD_CAT_ID', ''))
            ]
        
        # paginate the results
        total = len(new_sats)
        pages = max(1, (total + limit - 1) // limit)
        results = new_sats[offset: offset + limit]

        # format the response
        formatted = [
            {
                'name': sat.get('OBJECT_NAME'),
                'norad_id': str(sat.get('NORAD_CAT_ID')),
                'object_id': sat.get('OBJECT_ID'),
                'classification': sat.get('CLASSIFICATION_TYPE', 'U'),
                'orbit_type':  derive_orbit_type(sat.get('MEAN_MOTION', 0), sat.get('INCLINATION', 0)),
                'inclination': sat.get('INCLINATION'),
                'eccentricity': sat.get('ECCENTRICITY'),
                'mean_motion': sat.get('MEAN_MOTION'),
                'epoch': sat.get('EPOCH'),
                'ra_of_asc_node': sat.get('RA_OF_ASC_NODE'),
                'arg_of_pericenter': sat.get('ARG_OF_PERICENTER'),
                'mean_anomaly': sat.get('MEAN_ANOMALY'),
                'bstar': sat.get('BSTAR'),
            }
            for sat in results
        ]

        return Response({
            'results': formatted,
            'total': total,
            'page': page,
            'pages': pages,
            'limit': limit,
        })

# create satellite takes all the data from our frontend as a payload and adds new rows to all associated tables in the database
class CreateSatellite(APIView):
    def post(self, request):
        satellite = request.data.get('satellite', {})
        owner = request.data.get('owner', {})
        launch = request.data.get('launch', {})
        communication = request.data.get('communication', {})
        type_data = request.data.get('type', {})

        # Validate required fields
        if not satellite.get('norad_id'):
            return Response({'error': 'norad_id is required'}, status=400)
        if not satellite.get('name'):
            return Response({'error': 'name is required'}, status=400)
        if not type_data.get('subclass'):
            return Response({'error': 'satellite type is required'}, status=400)

        with transaction.atomic(), connection.cursor() as cursor:

            # 1. Owner — use existing or create new
            if owner.get('isNew'):
                cursor.execute("""
                    INSERT INTO satellite_owner 
                        (owner_name, owner_phone, owner_address, country, operator, owner_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    owner.get('owner_name'),
                    owner.get('owner_phone'),
                    owner.get('owner_address'),
                    owner.get('country'),
                    owner.get('operator'),
                    owner.get('owner_type'),
                ))
                owner_id = cursor.lastrowid
            else:
                owner_id = owner.get('owner_id')

            # 2. Insert satellite 
            cursor.execute("""
                INSERT INTO satellite 
                    (name, description, orbit_type, norad_id, object_id, classification, dataset_id, owner_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                satellite.get('name'),
                satellite.get('description', ''),
                satellite.get('orbit_type'),
                satellite.get('norad_id'),
                satellite.get('object_id'),
                satellite.get('classification', 'U'),
                satellite.get('dataset_id'),
                owner_id,
            ))
            satellite_id = cursor.lastrowid

            # 3. Launch vehicle — use existing or create
            if launch.get('vehicleIsNew'):
                cursor.execute("""
                    INSERT INTO launch_vehicle 
                        (vehicle_name, manufacturer, reusable, payload_capacity, country)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    launch.get('vehicle_name'),
                    launch.get('manufacturer'),
                    launch.get('reusable', 0),
                    launch.get('payload_capacity'),
                    launch.get('vehicle_country'),
                ))
                vehicle_id = cursor.lastrowid
            else:
                vehicle_id = launch.get('vehicle_id')

            # 4. Launch site — use existing or create 
            if launch.get('siteIsNew'):
                cursor.execute("""
                    INSERT INTO launch_site (site_name, location, climate, country)
                    VALUES (%s, %s, %s, %s)
                """, (
                    launch.get('site_name'),
                    launch.get('site_location'),
                    launch.get('site_climate'),
                    launch.get('site_country'),
                ))
            site_name = launch.get('site_name')

            # 5. deploys_payload
            deploy_date = launch.get('deploy_date_time')
            cursor.execute("""
                INSERT INTO deploys_payload (vehicle_id, satellite_id, deploy_date_time)
                VALUES (%s, %s, %s)
            """, (vehicle_id, satellite_id, deploy_date))

            # 6. launched_from — ignore if this vehicle/site/date combo already exists
            cursor.execute("""
                INSERT IGNORE INTO launched_from (vehicle_id, site_name, launch_date)
                VALUES (%s, %s, %s)
            """, (vehicle_id, site_name, deploy_date))

            # 7. Communication station — use existing or create
            if communication.get('stationIsNew'):
                cursor.execute("""
                    INSERT INTO communication_station (name, location)
                    VALUES (%s, %s)
                """, (
                    communication.get('station_name'),
                    communication.get('station_location'),
                ))
            station_location = communication.get('station_location')

            # 8. communicates_with
            cursor.execute("""
                INSERT INTO communicates_with (satellite_id, location, communication_frequency)
                VALUES (%s, %s, %s)
            """, (
                satellite_id,
                station_location,
                communication.get('communication_frequency'),
            ))

            # 9. Subclass type table
            subclass = type_data.get('subclass')
            subclass_table_map = {
                'Earth Science':   'earth_science',
                'Oceanic Science': 'oceanic_science',
                'Weather':         'weather',
                'Navigation':      'navigation',
                'Internet':        'internet',
                'Research':        'research',
            }
            table = subclass_table_map.get(subclass)

            if table:
                # Remove subclass key — only insert actual fields
                fields = {k: v for k, v in type_data.items() if k != 'subclass'}
                if fields:
                    cols = ', '.join(fields.keys())
                    placeholders = ', '.join(['%s'] * len(fields))
                    values = list(fields.values())
                    cursor.execute(
                        f"INSERT INTO {table} (satellite_id, {cols}) VALUES (%s, {placeholders})",
                        [satellite_id] + values
                    )

        # create a thread to generate the trajectory for this new satellite in the background
        thread = threading.Thread(
            target=generate_trajectory_async,
            args=(satellite_id, satellite.get('dataset_id'), satellite),
            daemon=True
        )
        # start the thread
        thread.start()

        return Response({
            'message': 'Satellite created successfully',
            'satellite_id': satellite_id,
        }, status=201)
    