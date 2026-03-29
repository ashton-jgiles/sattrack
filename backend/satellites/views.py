from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response

class SatelliteView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    s.*,
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
                    LEFT JOIN weather w  ON s.satellite_id = w.satellite_id
                    LEFT JOIN navigation n  ON s.satellite_id = n.satellite_id
                    LEFT JOIN internet i  ON s.satellite_id = i.satellite_id
                    LEFT JOIN research r  ON s.satellite_id = r.satellite_id
            """)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return Response(data)
    
class SpecificSatelliteView(APIView):
    def get(self, request, satellite_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM satellite WHERE satellite_id = %s", [satellite_id])
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        if not row:
            return Response({'error': 'Satellite not found'}, status=404)
        
        return Response(dict(zip(columns, row)))

class TotalSatellites(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(satellite_id) AS total FROM satellite")
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        if not row:
            return Response({'error': 'Total Satellites not computed'}, status=404)
        
        return Response(dict(zip(columns, row)));

class TotalEarthSatellites(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(satellite_id) AS total FROM earth_science")
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        if not row:
            return Response({'error': 'Total Earth Satellites not computed'}, status=404)
        
        return Response(dict(zip(columns, row)));

class TotalOceanicSatellites(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(satellite_id) AS total FROM oceanic_science")
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        if not row:
            return Response({'error': 'Total Oceanic Satellites not computed'}, status=404)
        
        return Response(dict(zip(columns, row)));

class TotalNavigationSatellites(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(satellite_id) AS total FROM navigation")
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        if not row:
            return Response({'error': 'Total Naviation Satellites not computed'}, status=404)
        
        return Response(dict(zip(columns, row)));

class TotalInternetSatellites(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(satellite_id) AS total FROM internet")
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        if not row:
            return Response({'error': 'Total Internet Satellites not computed'}, status=404)
        
        return Response(dict(zip(columns, row)));

class TotalWeatherSatellites(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(satellite_id) AS total FROM weather")
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        if not row:
            return Response({'error': 'Total Weather Satellites not computed'}, status=404)
        
        return Response(dict(zip(columns, row)));

class TotalResearchSatellites(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(satellite_id) AS total FROM research")
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        if not row:
            return Response({'error': 'Total Research Satellites not computed'}, status=404)
        
        return Response(dict(zip(columns, row)));

class AllTrajectory(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT satellite_id, dataset_id, timestamp, latitude, longitude, altitude FROM trajectory WHERE timestamp >= NOW() - INTERVAL 2 DAY ORDER BY satellite_id, timestamp ASC")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response(data)

class RecentDeployments(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
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
                    INNER JOIN deploys_payload dp ON s.satellite_id = dp.satellite_id
                    LEFT JOIN earth_science  es ON s.satellite_id = es.satellite_id
                    LEFT JOIN oceanic_science os ON s.satellite_id = os.satellite_id
                    LEFT JOIN weather         w  ON s.satellite_id = w.satellite_id
                    LEFT JOIN navigation      n  ON s.satellite_id = n.satellite_id
                    LEFT JOIN internet        i  ON s.satellite_id = i.satellite_id
                    LEFT JOIN research        r  ON s.satellite_id = r.satellite_id
                WHERE dp.deploy_date_time >= NOW() - INTERVAL 5 year
                ORDER BY dp.deploy_date_time
            """)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response(data)
    
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
            WHERE s.satellite_id = %s
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
        
class DeleteSatellite(APIView):
    def delete(self, request, satellite_id):
        with connection.cursor() as cursor:
            # check satellite exists
            cursor.execute("SELECT satellite_id FROM satellite WHERE satellite_id = %s", [satellite_id])

            if not cursor.fetchone():
                return Response({'error': 'Satellite not found'}, status=404)
            
            # Delete in order — child tables first
            cursor.execute("DELETE FROM trajectory WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM communicates_with WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM deploys_payload WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM earth_science WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM oceanic_science WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM weather WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM navigation WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM internet WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM research WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM satellite WHERE satellite_id = %s", (satellite_id,))

        return Response({'message': 'Satellite deleted successfully'})

class ModifySatellite(APIView):
    def post(self, request):
        satellite     = request.data.get('satellite', {})
        communication = request.data.get('communication', {})
        type_data     = request.data.get('type_data', {})

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
    