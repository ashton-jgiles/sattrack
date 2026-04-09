# connection and api imports and rate limiting imports
from django.db import connection
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from backend.throttles import PositionsThrottle

# Subtype detection fragments shared across multiple views.
# Defined once here to avoid copy-pasting the same SQL in every query.
SUBTYPE_CASE = """
    CASE
        WHEN es.satellite_id IS NOT NULL THEN 'Earth Science'
        WHEN os.satellite_id IS NOT NULL THEN 'Oceanic Science'
        WHEN w.satellite_id  IS NOT NULL THEN 'Weather'
        WHEN n.satellite_id  IS NOT NULL THEN 'Navigation'
        WHEN i.satellite_id  IS NOT NULL THEN 'Internet'
        WHEN r.satellite_id  IS NOT NULL THEN 'Research'
        ELSE 'Unknown'
    END AS satellite_type"""

SUBTYPE_JOINS = """
    LEFT JOIN earth_science  es ON s.satellite_id = es.satellite_id
    LEFT JOIN oceanic_science os ON s.satellite_id = os.satellite_id
    LEFT JOIN weather        w  ON s.satellite_id = w.satellite_id
    LEFT JOIN navigation     n  ON s.satellite_id = n.satellite_id
    LEFT JOIN internet       i  ON s.satellite_id = i.satellite_id
    LEFT JOIN research       r  ON s.satellite_id = r.satellite_id"""


# satellite view to list all satellites and their subclass type
class SatelliteView(APIView):
    def get(self, request):
        # get the level access of the user
        level = getattr(request.user, 'level_access', 1)
        # level 3 can see pending; everyone else only sees approved
        visible_statuses = ['pending', 'approved'] if level >= 3 else ['approved']
        placeholders = ', '.join(['%s'] * len(visible_statuses))

        with connection.cursor() as cursor:
            # get the all satellites and their type and the dataset review status
            cursor.execute(f"""
                SELECT
                    s.*,
                    d.review_status,
                    {SUBTYPE_CASE}
                FROM satellite s
                    INNER JOIN dataset d ON s.dataset_id = d.dataset_id AND d.deleted_at IS NULL AND d.review_status IN ({placeholders})
                    {SUBTYPE_JOINS}
                WHERE s.deleted_at IS NULL
            """, visible_statuses)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # return the data
        return Response(data)


# specific satellite gets a satellite by its id and returns it
class SpecificSatelliteView(APIView):
    def get(self, request, satellite_id):
        with connection.cursor() as cursor:
            # get the satellite by its id
            cursor.execute("SELECT * FROM satellite WHERE satellite_id = %s AND deleted_at IS NULL", [satellite_id])
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        # check satellite exists
        if not row:
            return Response({'error': 'Satellite not found'}, status=404)

        # return the data
        return Response(dict(zip(columns, row)))


# satellite type counts returns total satellite count and a breakdown by subtype in a single query
class SatelliteTypeCounts(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        level = getattr(request.user, 'level_access', 1)
        visible_statuses = ['pending', 'approved'] if level >= 3 else ['approved']
        placeholders = ', '.join(['%s'] * len(visible_statuses))

        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    COUNT(s.satellite_id)  AS total,
                    COUNT(es.satellite_id) AS earth_science,
                    COUNT(os.satellite_id) AS oceanic_science,
                    COUNT(w.satellite_id)  AS weather,
                    COUNT(n.satellite_id)  AS navigation,
                    COUNT(i.satellite_id)  AS internet,
                    COUNT(r.satellite_id)  AS research
                FROM satellite s
                    INNER JOIN dataset d ON s.dataset_id = d.dataset_id AND d.deleted_at IS NULL AND d.review_status IN ({placeholders})
                    {SUBTYPE_JOINS}
                WHERE s.deleted_at IS NULL
            """, visible_statuses)
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        return Response(dict(zip(columns, row)))


# all trajectory returns paginated trajectory rows, scoped to a satellite batch per page
class AllTrajectory(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PositionsThrottle]

    # page size limits sourced from settings to keep them in one place
    PAGE_SIZE_DEFAULT = settings.TRAJECTORY_PAGE_SIZE_DEFAULT
    PAGE_SIZE_MAX = settings.TRAJECTORY_PAGE_SIZE_MAX

    def get(self, request):
        # validate page and page_size before using them — non-integer values would otherwise 500
        try:
            page = max(1, int(request.GET.get('page', 1)))
            page_size = min(
                self.PAGE_SIZE_MAX,
                max(1, int(request.GET.get('page_size', self.PAGE_SIZE_DEFAULT)))
            )
        except (TypeError, ValueError):
            return Response({'error': 'page and page_size must be integers'}, status=400)

        offset = (page - 1) * page_size

        level = getattr(request.user, 'level_access', 1)
        visible_statuses = ['approved', 'pending'] if level >= 3 else ['approved']
        placeholders = ', '.join(['%s'] * len(visible_statuses))

        with connection.cursor() as cursor:
            # total active satellites in visible datasets for pagination metadata
            cursor.execute(f"""
                SELECT COUNT(*) FROM satellite s
                INNER JOIN dataset d ON s.dataset_id = d.dataset_id AND d.deleted_at IS NULL AND d.review_status IN ({placeholders})
                WHERE s.deleted_at IS NULL
            """, visible_statuses)
            total_satellites = cursor.fetchone()[0]

            # satellite IDs for this page, with review status to identify pending
            cursor.execute(f"""
                SELECT s.satellite_id, d.review_status FROM satellite s
                INNER JOIN dataset d ON s.dataset_id = d.dataset_id AND d.deleted_at IS NULL AND d.review_status IN ({placeholders})
                WHERE s.deleted_at IS NULL ORDER BY s.satellite_id LIMIT %s OFFSET %s
            """, visible_statuses + [page_size, offset])
            sat_rows = cursor.fetchall()
            sat_ids = [row[0] for row in sat_rows]
            pending_satellite_ids = [row[0] for row in sat_rows if row[1] == 'pending']

            if not sat_ids:
                total_pages = max(1, -(-total_satellites // page_size))
                return Response({
                    'results': [],
                    'pending_satellite_ids': [],
                    'page': page,
                    'page_size': page_size,
                    'total_satellites': total_satellites,
                    'total_pages': total_pages,
                })

            id_placeholders = ','.join(['%s'] * len(sat_ids))
            cursor.execute(f"""
                SELECT
                    t.satellite_id,
                    t.dataset_id,
                    t.timestamp,
                    t.latitude,
                    t.longitude,
                    t.altitude,
                    t.velocity
                FROM trajectory t
                INNER JOIN (
                    SELECT satellite_id, MAX(timestamp) AS max_ts
                    FROM trajectory
                    WHERE satellite_id IN ({id_placeholders})
                    GROUP BY satellite_id
                ) latest ON t.satellite_id = latest.satellite_id
                WHERE t.satellite_id IN ({id_placeholders})
                  AND t.timestamp >= latest.max_ts - INTERVAL 2 DAY
                ORDER BY t.satellite_id, t.timestamp ASC
            """, sat_ids + sat_ids)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        total_pages = max(1, -(-total_satellites // page_size))

        return Response({
            'results': results,
            'pending_satellite_ids': pending_satellite_ids,
            'page': page,
            'page_size': page_size,
            'total_satellites': total_satellites,
            'total_pages': total_pages,
        })


# recent deployments gets all satellites deployed in the last 5 years
class RecentDeployments(APIView):
    def get(self, request):
        level = getattr(request.user, 'level_access', 1)

        with connection.cursor() as cursor:
            # level 3+ can see satellites from any dataset; others restricted to approved datasets only
            if level >= 3:
                cursor.execute(f"""
                    SELECT s.*, dp.deploy_date_time, {SUBTYPE_CASE}
                    FROM satellite s
                        INNER JOIN deploys_payload dp ON s.satellite_id = dp.satellite_id
                        {SUBTYPE_JOINS}
                    WHERE s.deleted_at IS NULL
                      AND dp.deploy_date_time >= NOW() - INTERVAL 5 YEAR
                    ORDER BY dp.deploy_date_time
                """)
            else:
                cursor.execute(f"""
                    SELECT s.*, dp.deploy_date_time, {SUBTYPE_CASE}
                    FROM satellite s
                        INNER JOIN dataset d ON s.dataset_id = d.dataset_id AND d.deleted_at IS NULL AND d.review_status = 'approved'
                        INNER JOIN deploys_payload dp ON s.satellite_id = dp.satellite_id
                        {SUBTYPE_JOINS}
                    WHERE s.deleted_at IS NULL
                      AND dp.deploy_date_time >= NOW() - INTERVAL 5 YEAR
                    ORDER BY dp.deploy_date_time
                """)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response(data)


# specific satellite all data — returns the full profile for one satellite
class SpecificSatelliteAllData(APIView):
    def get(self, request, satellite_id):
        with connection.cursor() as cursor:
            # Explicit column list instead of SELECT * on joined tables.
            # Wildcard selects from multiple tables produce duplicate column names
            # (e.g. `country` appears in both satellite_owner and launch_vehicle),
            # which silently overwrites earlier values in the resulting dict.
            # Each column is named explicitly so the dict is always correct.
            cursor.execute("""
            SELECT
                -- core satellite fields
                s.satellite_id, s.name, s.description, s.orbit_type,
                s.norad_id, s.object_id, s.classification, s.last_contact_time,
                s.dataset_id, s.username,
                -- owner fields
                so.owner_id, so.owner_name, so.owner_phone, so.owner_address,
                so.country, so.operator, so.owner_type,
                -- launch fields
                dp.deploy_date_time,
                lv.vehicle_id, lv.vehicle_name, lv.manufacturer, lv.reusable, lv.payload_capacity,
                -- launch site fields
                ls.site_name, ls.location, ls.climate, ls.country AS site_country,
                -- subclass fields (only one set will be non-null)
                es.instrument, es.data_measured, es.wavelength_band, es.resolution_m,
                es.data_archive_url, es.mission_status,
                os.instrument AS os_instrument, os.data_measured AS os_data_measured,
                os.wavelength_band AS os_wavelength_band, os.resolution_m AS os_resolution_m,
                os.data_archive_url AS os_data_archive_url, os.mission_status AS os_mission_status,
                n.constellation, n.signal_type, n.accuracy_m, n.orbital_slot, n.clock_type,
                i.coverage, i.frequency_band, i.service_type, i.throughput_gbps, i.altitude_km,
                r.instrument AS r_instrument, r.data_measured AS r_data_measured,
                r.research_field, r.wavelength_band AS r_wavelength_band,
                r.data_archive_url AS r_data_archive_url, r.mission_status AS r_mission_status,
                w.instrument AS w_instrument, w.data_measured AS w_data_measured,
                w.coverage_region, w.imaging_channels, w.repeat_cycle_min,
                w.data_archive_url AS w_data_archive_url, w.mission_status AS w_mission_status,
                -- communication fields
                cw.communication_frequency,
                cw.location AS station_location,
                cs.name AS station_name,
                CASE
                    WHEN es.satellite_id IS NOT NULL THEN 'Earth Science'
                    WHEN os.satellite_id IS NOT NULL THEN 'Oceanic Science'
                    WHEN w.satellite_id  IS NOT NULL THEN 'Weather'
                    WHEN n.satellite_id  IS NOT NULL THEN 'Navigation'
                    WHEN i.satellite_id  IS NOT NULL THEN 'Internet'
                    WHEN r.satellite_id  IS NOT NULL THEN 'Research'
                END AS satellite_type
            FROM satellite s
                INNER JOIN satellite_owner      so ON s.owner_id      = so.owner_id
                INNER JOIN deploys_payload      dp ON s.satellite_id  = dp.satellite_id
                INNER JOIN launch_vehicle       lv ON dp.vehicle_id   = lv.vehicle_id
                INNER JOIN launched_from        lf ON lf.launch_date  = dp.deploy_date_time
                INNER JOIN launch_site          ls ON lf.site_name    = ls.site_name
                INNER JOIN communicates_with    cw ON s.satellite_id  = cw.satellite_id
                INNER JOIN communication_station cs ON cw.location    = cs.location
                LEFT JOIN earth_science  es ON s.satellite_id = es.satellite_id
                LEFT JOIN oceanic_science os ON s.satellite_id = os.satellite_id
                LEFT JOIN navigation      n  ON s.satellite_id = n.satellite_id
                LEFT JOIN internet        i  ON s.satellite_id = i.satellite_id
                LEFT JOIN research        r  ON s.satellite_id = r.satellite_id
                LEFT JOIN weather         w  ON s.satellite_id = w.satellite_id
            WHERE s.satellite_id = %s AND s.deleted_at IS NULL
            """, [satellite_id])
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        if not row:
            return Response({'error': 'Satellite data not found'}, status=404)

        # build flat dict, skipping NULL values (only one subclass table has real data)
        flat = {k: v for k, v in zip(columns, row) if v is not None}

        # satellite core fields
        satellite = {k: flat[k] for k in [
            'satellite_id', 'name', 'description', 'orbit_type',
            'norad_id', 'object_id', 'classification', 'last_contact_time',
            'dataset_id', 'username', 'satellite_type',
        ] if k in flat}

        # owner fields
        owner = {k: flat[k] for k in [
            'owner_id', 'owner_name', 'owner_phone', 'owner_address',
            'country', 'operator', 'owner_type',
        ] if k in flat}

        # launch fields
        launch = {k: flat[k] for k in [
            'deploy_date_time', 'vehicle_id', 'vehicle_name', 'manufacturer',
            'reusable', 'payload_capacity',
        ] if k in flat}

        # launch site fields
        launch_site = {k: flat[k] for k in [
            'site_name', 'location', 'climate', 'site_country',
        ] if k in flat}

        # communication fields
        communication = {k: flat[k] for k in [
            'communication_frequency', 'station_location', 'station_name',
        ] if k in flat}

        # subclass-specific fields: everything not already placed in a structured dict above.
        # Because all columns are now explicitly named, only genuine subclass columns remain.
        known_keys = set(satellite) | set(owner) | set(launch) | set(launch_site) | set(communication)
        type_data = {k: v for k, v in flat.items() if k not in known_keys}

        # strip the os_/r_/w_ prefixes added to disambiguate shared column names
        prefix_map = {
            'os_instrument': 'instrument', 'os_data_measured': 'data_measured',
            'os_wavelength_band': 'wavelength_band', 'os_resolution_m': 'resolution_m',
            'os_data_archive_url': 'data_archive_url', 'os_mission_status': 'mission_status',
            'r_instrument': 'instrument', 'r_data_measured': 'data_measured',
            'r_wavelength_band': 'wavelength_band', 'r_data_archive_url': 'data_archive_url',
            'r_mission_status': 'mission_status',
            'w_instrument': 'instrument', 'w_data_measured': 'data_measured',
            'w_data_archive_url': 'data_archive_url', 'w_mission_status': 'mission_status',
        }
        type_data = {prefix_map.get(k, k): v for k, v in type_data.items()}

        return Response({
            'satellite':     satellite,
            'owner':         owner,
            'launch':        launch,
            'launch_site':   launch_site,
            'communication': communication,
            'type_data':     type_data,
        })
