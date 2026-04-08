# connection and api imports
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response

# all owners gets all the satellite owners table
class AllOwners(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            # get all the satellite owners
            cursor.execute("SELECT * FROM satellite_owner ORDER BY owner_name")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        # return the owner data
        return Response(data)

# all vehicles gets all vehicles from the launch vehicle table
class AllVehicles(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            # get all the launch vehicles
            cursor.execute("SELECT * FROM launch_vehicle ORDER BY vehicle_name")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        # return the launch vehicle data
        return Response(data)

# all launch sites dets all launch sites from the launch sites table
class AllLaunchSites(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            # get all the launch sites
            cursor.execute("SELECT * FROM launch_site ORDER BY site_name")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        # return the launch site data
        return Response(data)

# all communication stations get all comm stations from the communication station table
class AllCommunicationStations(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            # get all the communication station data
            cursor.execute("SELECT * FROM communication_station ORDER BY name")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        # return the communication station data
        return Response(data)
    