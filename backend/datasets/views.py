# connection and api imports
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

# total datasets class which return the total number of datasets in the dataset table
class TotalDatasets(APIView):
    # set auth and perm classes
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        with connection.cursor() as cursor:
            # get the total number of datasets that are approved
            cursor.execute("SELECT COUNT(dataset_id) AS total FROM dataset WHERE deleted_at IS NULL AND review_status = 'approved'")
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

        # check to make sure datasets exists
        if not row:
            return Response({'error': 'Total Datasets not computed'}, status=404)
        
        # create the return data
        data = dict(zip(columns, row))

        # return the data as a response
        return Response(data)

# dataset view class which returns as json all datasets in the dataset table
class DatasetView(APIView):
    def get(self, request):
        # get the level and branch query based on access — level 3+ sees all non-deleted datasets
        level = getattr(request.user, 'level_access', 1)

        with connection.cursor() as cursor:
            # get the non deleted datasets
            if level >= 3:
                cursor.execute("SELECT * FROM dataset WHERE deleted_at IS NULL")
            else:
                cursor.execute("SELECT * FROM dataset WHERE deleted_at IS NULL AND review_status = 'approved'")
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # return the response data
        return Response(data)

# satellites in dataset view returns all satellites belonging to a given dataset
class SatellitesInDataset(APIView):
    def get(self, request, dataset_id):
        # get the access level from the request
        level = getattr(request.user, 'level_access', 1)

        with connection.cursor() as cursor:
            if level < 3:
                # select the needed satellite data from the associated dataset
                cursor.execute("""
                    SELECT s.satellite_id, s.name, s.orbit_type, s.norad_id, s.object_id, s.classification
                    FROM satellite s
                    INNER JOIN dataset d ON s.dataset_id = d.dataset_id
                    WHERE s.dataset_id = %s AND s.deleted_at IS NULL
                      AND d.deleted_at IS NULL AND d.review_status = 'approved'
                """, [dataset_id])
            else:
                cursor.execute("""
                    SELECT satellite_id, name, orbit_type, norad_id, object_id, classification
                    FROM satellite
                    WHERE dataset_id = %s AND deleted_at IS NULL
                """, [dataset_id])
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # return the response data
        return Response(data)
    