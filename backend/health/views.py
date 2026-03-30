from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response


class HealthCheck(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_status = "ok"
        except Exception:
            return Response({"status": "error", "db": "unreachable"}, status=503)

        return Response({"status": "ok", "db": db_status})
