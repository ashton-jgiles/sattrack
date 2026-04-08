# connection and api imports and rate limiting imports
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from backend.throttles import PositionsThrottle

# satllite view to list all satellites and their subclass type
class SatelliteView(APIView):
    def get(self, request):
        level = getattr(request.user, 'level_access', 1)
        status_filter = "!= 'rejected'" if level >= 3 else "= 'approved'"

        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    s.*,
                    d.review_status,
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
                    INNER JOIN dataset d ON s.dataset_id = d.dataset_id AND d.deleted_at IS NULL AND d.review_status {status_filter}
                    LEFT JOIN earth_science  es ON s.satellite_id = es.satellite_id
                    LEFT JOIN oceanic_science os ON s.satellite_id = os.satellite_id
                    LEFT JOIN weather w  ON s.satellite_id = w.satellite_id
                    LEFT JOIN navigation n  ON s.satellite_id = n.satellite_id
                    LEFT JOIN internet i  ON s.satellite_id = i.satellite_id
                    LEFT JOIN research r  ON s.satellite_id = r.satellite_id
                WHERE s.deleted_at IS NULL
            """)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response(data)
    
# specific satellite gets a satellite by its id and return it
class SpecificSatelliteView(APIView):
    def get(self, request, satellite_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM satellite WHERE satellite_id = %s AND deleted_at IS NULL", [satellite_id])
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        if not row:
            return Response({'error': 'Satellite not found'}, status=404)
        
        return Response(dict(zip(columns, row)))

# satellite type counts returns total satellite count and a breakdown by subtype in a single query
class SatelliteTypeCounts(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        level = getattr(request.user, 'level_access', 1)
        status_filter = "!= 'rejected'" if level >= 3 else "= 'approved'"

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
                    INNER JOIN dataset d ON s.dataset_id = d.dataset_id AND d.deleted_at IS NULL AND d.review_status {status_filter}
                    LEFT JOIN earth_science  es ON s.satellite_id = es.satellite_id
                    LEFT JOIN oceanic_science os ON s.satellite_id = os.satellite_id
                    LEFT JOIN weather         w  ON s.satellite_id = w.satellite_id
                    LEFT JOIN navigation      n  ON s.satellite_id = n.satellite_id
                    LEFT JOIN internet        i  ON s.satellite_id = i.satellite_id
                    LEFT JOIN research        r  ON s.satellite_id = r.satellite_id
                WHERE s.deleted_at IS NULL
            """)
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        return Response(dict(zip(columns, row)))

# all trajectory returns paginated trajectory rows, scoped to a satellite batch per page
class AllTrajectory(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PositionsThrottle]

    PAGE_SIZE_DEFAULT = 100
    PAGE_SIZE_MAX = 200

    def get(self, request):
        page = max(1, int(request.GET.get('page', 1)))
        page_size = min(
            self.PAGE_SIZE_MAX,
            max(1, int(request.GET.get('page_size', self.PAGE_SIZE_DEFAULT)))
        )
        offset = (page - 1) * page_size

        level = getattr(request.user, 'level_access', 1)
        status_filter = "IN ('approved', 'pending')" if level >= 3 else "= 'approved'"

        with connection.cursor() as cursor:
            # total active satellites in visible datasets for pagination metadata
            cursor.execute(f"""
                SELECT COUNT(*) FROM satellite s
                INNER JOIN dataset d ON s.dataset_id = d.dataset_id AND d.deleted_at IS NULL AND d.review_status {status_filter}
                WHERE s.deleted_at IS NULL
            """)
            total_satellites = cursor.fetchone()[0]

            # satellite IDs for this page, with review status to identify pending
            cursor.execute(f"""
                SELECT s.satellite_id, d.review_status FROM satellite s
                INNER JOIN dataset d ON s.dataset_id = d.dataset_id AND d.deleted_at IS NULL AND d.review_status {status_filter}
                WHERE s.deleted_at IS NULL ORDER BY s.satellite_id LIMIT %s OFFSET %s
            """, [page_size, offset])
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

            placeholders = ','.join(['%s'] * len(sat_ids))
            cursor.execute(f"""
                SELECT t.satellite_id, t.dataset_id, t.timestamp,
                       t.latitude, t.longitude, t.altitude, t.velocity
                FROM trajectory t
                INNER JOIN (
                    SELECT satellite_id, MAX(timestamp) AS max_ts
                    FROM trajectory
                    WHERE satellite_id IN ({placeholders})
                    GROUP BY satellite_id
                ) latest ON t.satellite_id = latest.satellite_id
                WHERE t.satellite_id IN ({placeholders})
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

# recent deployments gets all satelites deployed in the last 5 years
class RecentDeployments(APIView):
    def get(self, request):
        level = getattr(request.user, 'level_access', 1)
        dataset_join = "" if level >= 3 else "INNER JOIN dataset d ON s.dataset_id = d.dataset_id AND d.deleted_at IS NULL AND d.review_status = 'approved'"

        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    s.*,
                    dp.deploy_date_time,
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
                    {dataset_join}
                    INNER JOIN deploys_payload dp ON s.satellite_id = dp.satellite_id
                    LEFT JOIN earth_science  es ON s.satellite_id = es.satellite_id
                    LEFT JOIN oceanic_science os ON s.satellite_id = os.satellite_id
                    LEFT JOIN weather         w  ON s.satellite_id = w.satellite_id
                    LEFT JOIN navigation      n  ON s.satellite_id = n.satellite_id
                    LEFT JOIN internet        i  ON s.satellite_id = i.satellite_id
                    LEFT JOIN research        r  ON s.satellite_id = r.satellite_id
                WHERE s.deleted_at IS NULL
                  AND dp.deploy_date_time >= NOW() - INTERVAL 5 year
                ORDER BY dp.deploy_date_time
            """)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response(data)

# specific satellite view gets all associated data with a satellite id
class SpecificSatelliteAllData(APIView):
    def get(self, request, satellite_id):
        with connection.cursor() as cursor:
            cursor.execute(""" 
            SELECT 
                s.*,
                so.*,
                dp.deploy_date_time,
                lv.*,
                ls.site_name,
                ls.location,
                ls.climate,
                ls.country AS site_country,
                es.*,
                os.*,
                n.*,
                i.*,
                r.*,
                w.*,
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
                INNER JOIN satellite_owner so ON s.owner_id = so.owner_id 
                INNER JOIN deploys_payload dp ON s.satellite_id = dp.satellite_id 
                INNER JOIN launch_vehicle lv ON dp.vehicle_id = lv.vehicle_id 
                INNER JOIN launched_from lf ON lf.launch_date = dp.deploy_date_time 
                INNER JOIN launch_site ls ON lf.site_name = ls.site_name
                INNER JOIN communicates_with cw ON s.satellite_id = cw.satellite_id
                INNER JOIN communication_station cs ON cw.location = cs.location 
                LEFT JOIN earth_science es ON s.satellite_id = es.satellite_id 
                LEFT JOIN oceanic_science os ON s.satellite_id = os.satellite_id 
                LEFT JOIN navigation n ON s.satellite_id = n.satellite_id 
                LEFT JOIN internet i ON s.satellite_id = i.satellite_id 
                LEFT JOIN research r ON s.satellite_id = r.satellite_id 
                LEFT JOIN weather w ON s.satellite_id = w.satellite_id 
            WHERE s.satellite_id = %s AND s.deleted_at IS NULL
        """, [satellite_id])
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        if not row:
            return Response({'error': 'Satellite data not found'}, status=404)
        
        # strip nulls from non matching subclasses
        flat = {k: v for k, v in zip(columns, row) if v is not None}

        # Satellite fields 
        satellite = {k: flat[k] for k in [
            'satellite_id', 'name', 'description', 'orbit_type',
            'norad_id', 'object_id', 'classification', 'last_contact_time',
            'dataset_id', 'username', 'satellite_type',
        ] if k in flat}

        # Owner fields 
        owner = {k: flat[k] for k in [
            'owner_id', 'owner_name', 'owner_phone', 'owner_address',
            'country', 'operator', 'owner_type',
        ] if k in flat}

        # Launch fields 
        launch = {k: flat[k] for k in [
            'deploy_date_time', 'vehicle_id', 'vehicle_name', 'manufacturer',
            'reusable', 'payload_capacity',
        ] if k in flat}

        # Launch site fields 
        launch_site = {k: flat[k] for k in [
            'site_name', 'location', 'climate', 'site_country',
        ] if k in flat}

        # communication station fields
        communication = {k: flat[k] for k in [
           'communication_frequency', 'station_location', 'station_name' 
        ] if k in flat}

        # Subclass fields — only non-null ones remain 
        known_keys = (
            set(satellite) | set(owner) | set(launch) |
            set(launch_site) | set(communication) | {'owner_id', 'vehicle_id', 'communication_frequency', 
    'station_location', 'station_name'}
        )
        type_data = {k: v for k, v in flat.items() if k not in known_keys}

        return Response({
            'satellite':   satellite,
            'owner':       owner,
            'launch':      launch,
            'launch_site': launch_site,
            'communication': communication,
            'type_data':   type_data,
        })
       