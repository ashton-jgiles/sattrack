# connection and api imports
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response

# all owners gets all the satellite owners table
class AllOwners(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM satellite_owner ORDER BY owner_name")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(data)

# all vehicles gets all vehicles from the launch vehicle table
class AllVehicles(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM launch_vehicle ORDER BY vehicle_name")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(data)

# all launch sites dets all launch sites from the launch sites table
class AllLaunchSites(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM launch_site ORDER BY site_name")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(data)

# all communication stations get all comm stations from the communication station table
class AllCommunicationStations(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM communication_station ORDER BY name")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(data)