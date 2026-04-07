# connection and api imports
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date
import requests
import re

VALID_STATUSES = {'pending', 'approved', 'rejected'}
CELESTRAK_BASE = 'https://celestrak.org/NORAD/elements/gp.php'

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
                "SELECT dataset_id FROM dataset WHERE dataset_id = %s AND deleted_at IS NULL",
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

# delete dataset class which soft deletes a dataset and cascades to its satellites
class DeleteDataset(APIView):
    def delete(self, request, dataset_id):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT dataset_id FROM dataset WHERE dataset_id = %s AND deleted_at IS NULL",
                [dataset_id]
            )
            if not cursor.fetchone():
                return Response({'error': 'Dataset not found'}, status=404)

            cursor.execute(
                "UPDATE dataset SET deleted_at = NOW() WHERE dataset_id = %s",
                [dataset_id]
            )
            cursor.execute(
                "UPDATE satellite SET deleted_at = NOW() WHERE dataset_id = %s AND deleted_at IS NULL",
                [dataset_id]
            )

        return Response({'message': 'Dataset deleted successfully'})

# sources endpoint which scrapes the CelesTrak current data page and returns groups not yet in the database
class DatasetSources(APIView):
    def get(self, request):
        try:
            response = requests.get('https://celestrak.org/NORAD/elements/', timeout=30)
            response.raise_for_status()
            groups = re.findall(r'GROUP=([^&"\']+)', response.text)
            groups = list(dict.fromkeys(groups))
        except Exception as e:
            return Response({'error': f'Failed to fetch CelesTrak groups: {str(e)}'}, status=502)

        with connection.cursor() as cursor:
            cursor.execute("SELECT source_url FROM dataset WHERE deleted_at IS NULL")
            existing_urls = {row[0] for row in cursor.fetchall()}

        available = [
            {
                'group': group,
                'source_url': f"{CELESTRAK_BASE}?GROUP={group}&FORMAT=json",
            }
            for group in groups
            if f"{CELESTRAK_BASE}?GROUP={group}&FORMAT=json" not in existing_urls
        ]

        return Response(available)

# add dataset class which validates a CelesTrak group and inserts a new dataset row
class AddDataset(APIView):
    def post(self, request):
        group = request.data.get('group', '').strip()
        dataset_name = request.data.get('dataset_name', '').strip()
        description = request.data.get('description', '')
        pull_frequency = request.data.get('pull_frequency', '')

        if not group:
            return Response({'error': 'group is required'}, status=400)
        if not dataset_name:
            return Response({'error': 'dataset_name is required'}, status=400)

        source_url = f"{CELESTRAK_BASE}?GROUP={group}&FORMAT=json"

        # validate the group by hitting CelesTrak
        try:
            response = requests.get(source_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list) or len(data) == 0:
                return Response({'error': 'Invalid or empty CelesTrak group'}, status=400)
        except ValueError:
            # CelesTrak rate limited — check DB cache as fallback
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM celestrak_cache WHERE url = %s",
                    [source_url]
                )
                if not cursor.fetchone():
                    return Response(
                        {'error': 'Could not validate group. CelesTrak rate limited and no cache available. Try again later.'},
                        status=429
                    )
        except Exception as e:
            return Response({'error': f'Failed to validate CelesTrak group: {str(e)}'}, status=502)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO dataset (
                    dataset_name, description, creation_date,
                    source, source_url, pull_frequency, review_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [
                dataset_name,
                description,
                date.today(),
                f"CelesTrak {group.title()}",
                source_url,
                pull_frequency,
                'pending'
            ])
            dataset_id = cursor.lastrowid

        return Response({'message': 'Dataset created successfully', 'dataset_id': dataset_id}, status=201)
