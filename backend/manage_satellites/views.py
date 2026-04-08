# connection and api imports
import logging
from django.db import connection, transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from backend.throttles import CelesTrakThrottle
from manage_satellites.services import (
    RateLimitedError,
    SUBCLASS_ALLOWED_COLUMNS,
    fetch_celestrak_cached,
    derive_orbit_type,
    start_trajectory_thread,
)

logger = logging.getLogger('sattrack')

# maps display subclass name to table name — defined once and shared across views
SUBCLASS_TABLE_MAP = {
    'Earth Science':   'earth_science',
    'Oceanic Science': 'oceanic_science',
    'Weather':         'weather',
    'Navigation':      'navigation',
    'Internet':        'internet',
    'Research':        'research',
}


# returns all soft-deleted satellites — requires level 3+
class GetDeletedSatellites(APIView):
    def get(self, request):
        if getattr(request.user, 'level_access', 0) < 3:
            return Response({'error': 'Insufficient permissions'}, status=403)

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
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response(data)


# restores a soft-deleted satellite by clearing deleted_at — requires level 3+
class RecoverSatellite(APIView):
    def post(self, request, satellite_id):
        if getattr(request.user, 'level_access', 0) < 3:
            return Response({'error': 'Insufficient permissions'}, status=403)

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

        logger.info(f"[Satellite] Satellite {satellite_id} recovered by '{request.user.username}'")
        return Response({'message': 'Satellite recovered successfully'})


# soft-deletes a satellite by setting deleted_at to the current timestamp — requires level 3+
class DeleteSatellite(APIView):
    def delete(self, request, satellite_id):
        if getattr(request.user, 'level_access', 0) < 3:
            return Response({'error': 'Insufficient permissions'}, status=403)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT satellite_id FROM satellite WHERE satellite_id = %s AND deleted_at IS NULL",
                [satellite_id]
            )
            if not cursor.fetchone():
                return Response({'error': 'Satellite not found'}, status=404)

            cursor.execute(
                "UPDATE satellite SET deleted_at = NOW() WHERE satellite_id = %s",
                [satellite_id]
            )

        logger.info(f"[Satellite] Satellite {satellite_id} soft-deleted by '{request.user.username}'")
        return Response({'message': 'Satellite deleted successfully'})


# updates core satellite fields, communication frequency, and the matching subclass table row — requires level 3+
class ModifySatellite(APIView):
    def post(self, request):
        if getattr(request.user, 'level_access', 0) < 3:
            return Response({'error': 'Insufficient permissions'}, status=403)

        satellite = request.data.get('satellite', {})
        communication = request.data.get('communication', {})
        type_data = request.data.get('type_data', {})

        satellite_id = satellite.get('satellite_id')
        if not satellite_id:
            return Response({'error': 'satellite_id is required'}, status=400)

        with connection.cursor() as cursor:
            # update core satellite fields
            cursor.execute("""
                UPDATE satellite
                SET description = %s, classification = %s
                WHERE satellite_id = %s
            """, (
                satellite.get('description'),
                satellite.get('classification'),
                satellite_id,
            ))

            # update communication frequency if provided
            if communication.get('communication_frequency'):
                cursor.execute("""
                    UPDATE communicates_with
                    SET communication_frequency = %s
                    WHERE satellite_id = %s
                """, (
                    communication.get('communication_frequency'),
                    satellite_id,
                ))

            # update the matching subclass table row
            subclass_tables = list(SUBCLASS_TABLE_MAP.values())
            for table in subclass_tables:
                cursor.execute(
                    f"SELECT satellite_id FROM {table} WHERE satellite_id = %s",
                    (satellite_id,)
                )
                if cursor.fetchone():
                    # filter user-supplied keys through the whitelist to prevent column-name injection
                    allowed_cols = SUBCLASS_ALLOWED_COLUMNS.get(table, frozenset())
                    safe_type_data = {k: v for k, v in type_data.items() if k in allowed_cols}
                    if safe_type_data:
                        set_clause = ", ".join([f"`{k}` = %s" for k in safe_type_data.keys()])
                        values = list(safe_type_data.values()) + [satellite_id]
                        cursor.execute(
                            f"UPDATE {table} SET {set_clause} WHERE satellite_id = %s",
                            values
                        )
                    break

        logger.info(f"[Satellite] Satellite {satellite_id} modified by '{request.user.username}'")
        return Response({'message': 'Satellite updated successfully'})


# returns CelesTrak satellites for a dataset that are not already in the database — requires level 3+
class NewSatellitesFromDataset(APIView):
    throttle_classes = [CelesTrakThrottle]

    def get(self, request, dataset_id):
        if getattr(request.user, 'level_access', 0) < 3:
            return Response({'error': 'Insufficient permissions'}, status=403)

        search = request.GET.get('search', '').strip()

        # validate page and limit before using them — non-integer values would otherwise 500
        try:
            page = max(1, int(request.GET.get('page', 1)))
            limit = max(1, int(request.GET.get('limit', 50)))
        except (TypeError, ValueError):
            return Response({'error': 'page and limit must be integers'}, status=400)

        offset = (page - 1) * limit

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT source_url FROM dataset WHERE dataset_id = %s",
                [dataset_id]
            )
            row = cursor.fetchone()
            if not row:
                return Response({'error': 'Dataset not found'}, status=404)
            url = row[0]

            cursor.execute("SELECT norad_id FROM satellite")
            existing_norad_ids = {str(r[0]) for r in cursor.fetchall()}

        try:
            all_sats = fetch_celestrak_cached(url)
        except RateLimitedError:
            return Response(
                {'error': 'CelesTrak rate limit reached. Please try again later.'},
                status=429
            )
        except Exception as e:
            return Response({'error': f'Failed to fetch CelesTrak data: {str(e)}'}, status=502)

        # filter out satellites already in the database
        new_sats = [
            sat for sat in all_sats
            if str(sat.get('NORAD_CAT_ID', '')) not in existing_norad_ids
        ]

        # apply optional name/NORAD search
        if search:
            search_lower = search.lower()
            new_sats = [
                sat for sat in new_sats
                if search_lower in sat.get('OBJECT_NAME', '').lower()
                or search_lower in str(sat.get('NORAD_CAT_ID', ''))
            ]

        total = len(new_sats)
        pages = max(1, (total + limit - 1) // limit)
        results = new_sats[offset: offset + limit]

        formatted = [
            {
                'name': sat.get('OBJECT_NAME'),
                'norad_id': str(sat.get('NORAD_CAT_ID')),
                'object_id': sat.get('OBJECT_ID'),
                'classification': sat.get('CLASSIFICATION_TYPE', 'U'),
                'orbit_type': derive_orbit_type(sat.get('MEAN_MOTION', 0), sat.get('INCLINATION', 0)),
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


# inserts a new satellite and all associated records — requires level 3+
class CreateSatellite(APIView):
    def post(self, request):
        if getattr(request.user, 'level_access', 0) < 3:
            return Response({'error': 'Insufficient permissions'}, status=403)

        satellite = request.data.get('satellite', {})
        owner = request.data.get('owner', {})
        launch = request.data.get('launch', {})
        communication = request.data.get('communication', {})
        type_data = request.data.get('type', {})

        # validate required top-level fields
        if not satellite.get('norad_id'):
            return Response({'error': 'norad_id is required'}, status=400)
        if not satellite.get('name'):
            return Response({'error': 'name is required'}, status=400)
        if not type_data.get('subclass'):
            return Response({'error': 'satellite type is required'}, status=400)
        if satellite.get('orbit_type') not in ('LEO', 'MEO', 'GEO', 'HEO'):
            return Response({'error': 'orbit_type must be one of: LEO, MEO, GEO, HEO'}, status=400)
        if satellite.get('classification', 'U') not in ('U', 'C', 'S'):
            return Response({'error': 'classification must be one of: U, C, S'}, status=400)

        # validate the subclass before starting the transaction so we can return 400 cleanly
        subclass = type_data.get('subclass')
        table = SUBCLASS_TABLE_MAP.get(subclass)
        if not table:
            return Response({'error': f'Unknown satellite subclass: {subclass}'}, status=400)

        with transaction.atomic(), connection.cursor() as cursor:

            # check for duplicate norad_id before inserting anything
            cursor.execute(
                "SELECT satellite_id FROM satellite WHERE norad_id = %s",
                [satellite.get('norad_id')]
            )
            if cursor.fetchone():
                return Response({'error': 'A satellite with this NORAD ID already exists'}, status=409)

            # 1. owner — use existing or create new
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
                if not owner_id:
                    return Response({'error': 'owner_id is required when not creating a new owner'}, status=400)
                cursor.execute(
                    "SELECT owner_id FROM satellite_owner WHERE owner_id = %s",
                    [owner_id]
                )
                if not cursor.fetchone():
                    return Response({'error': 'Owner not found'}, status=400)

            # 2. satellite
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

            # 3. launch vehicle — use existing or create new
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

            # 4. launch site — use existing or create new
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

            # 7. communication station — use existing or create new
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

            # 9. subclass type table (table already validated before transaction)
            allowed_cols = SUBCLASS_ALLOWED_COLUMNS.get(table, frozenset())
            fields = {k: v for k, v in type_data.items() if k != 'subclass' and k in allowed_cols}
            if fields:
                cols = ', '.join(f'`{k}`' for k in fields.keys())
                placeholders = ', '.join(['%s'] * len(fields))
                cursor.execute(
                    f"INSERT INTO {table} (satellite_id, {cols}) VALUES (%s, {placeholders})",
                    [satellite_id] + list(fields.values())
                )

        logger.info(f"[Satellite] Satellite '{satellite.get('name')}' (NORAD {satellite.get('norad_id')}) created by '{request.user.username}'")

        # generate trajectory in the background so the response is not blocked
        start_trajectory_thread(satellite_id, satellite.get('dataset_id'), satellite)

        return Response({
            'message': 'Satellite created successfully',
            'satellite_id': satellite_id,
        }, status=201)
