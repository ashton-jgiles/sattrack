from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response

class TotalDatasets(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(dataset_id) AS total FROM dataset")
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        if not row:
            return Response({'error': 'Total Datasets not computed'}, status=404)
        
        return Response(dict(zip(columns, row)));