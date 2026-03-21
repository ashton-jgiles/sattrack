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