# connection and api imports
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response

# health check class to check the health of the backend
class HealthCheck(APIView):
    # empty perm and auth classes
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        # try to seelct 1 from the database to check its connectivity
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_status = "ok"
        except Exception:
            # return an error response if the db connection is not working
            return Response({"status": "error", "db": "unreachable"}, status=503)

        # return success if db connection is working
        return Response({"status": "ok", "db": db_status})
