# connection and api imports
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response

VALID_STATUSES = {'pending', 'approved', 'rejected'}

# modify dataset class which updates description, pull_frequency, and review_status
class ModifyDataset(APIView):
    def post(self, request, dataset_id):
        description = request.data.get('description')
        pull_frequency = request.data.get('pull_frequency')
        review_status = request.data.get('review_status')

        if review_status not in VALID_STATUSES:
            return Response({'error': 'Invalid review_status'}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT dataset_id FROM dataset WHERE dataset_id = %s",
                [dataset_id]
            )
            if not cursor.fetchone():
                return Response({'error': 'Dataset not found'}, status=404)

            cursor.execute("""
                UPDATE dataset
                SET description = %s, pull_frequency = %s, review_status = %s
                WHERE dataset_id = %s
            """, [description, pull_frequency, review_status, dataset_id])

        return Response({'message': 'Dataset updated successfully'})

# delete dataset class which removes a dataset from the database
class DeleteDataset(APIView):
    def delete(self, request, dataset_id):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT dataset_id FROM dataset WHERE dataset_id = %s",
                [dataset_id]
            )
            if not cursor.fetchone():
                return Response({'error': 'Dataset not found'}, status=404)

            cursor.execute(
                "DELETE FROM dataset WHERE dataset_id = %s",
                [dataset_id]
            )

        return Response({'message': 'Dataset deleted successfully'})
