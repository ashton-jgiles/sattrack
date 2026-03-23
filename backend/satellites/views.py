from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response

class SatelliteView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM satellite")
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
            cursor.execute("SELECT satellite_id, dataset_id, timestamp, latitude, longitude, altitude FROM trajectory")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response(data)