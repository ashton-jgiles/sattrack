# connection and api imports and requests
import logging
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import date
import requests
import re

logger = logging.getLogger('sattrack')

# global statuses and base url
VALID_STATUSES = {'pending', 'approved', 'rejected'}
CLOSED_STATUSES = {'approved', 'rejected'}
CELESTRAK_BASE = 'https://celestrak.org/NORAD/elements/gp.php'

# get review datasets returns all non-deleted datasets for the reviews page
class GetReviewDatasets(APIView):
    def get(self, request):
        # get closed datasets
        show_closed = request.GET.get('closed', 'false').lower() == 'true'

        # use parameterized IN so status values are never interpolated directly into SQL
        status_values = ['approved', 'rejected'] if show_closed else ['pending']
        placeholders = ', '.join(['%s'] * len(status_values))

        with connection.cursor() as cursor:
            # get dataset info from the dataset table and join satellites
            cursor.execute(f"""
                SELECT
                    d.dataset_id,
                    d.dataset_name,
                    d.description,
                    d.review_status,
                    d.review_comment,
                    d.creation_date,
                    d.last_pulled,
                    COUNT(s.satellite_id) AS satellite_count
                FROM dataset d
                LEFT JOIN satellite s
                    ON s.dataset_id = d.dataset_id AND s.deleted_at IS NULL
                WHERE d.deleted_at IS NULL
                AND d.review_status IN ({placeholders})
                GROUP BY d.dataset_id
                ORDER BY d.creation_date DESC
            """, status_values)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        # create the response data
        data = [dict(zip(columns, row)) for row in rows]

        # return the response data
        return Response(data)


# review dataset updates review_status and review_comment for a dataset
class ReviewDataset(APIView):
    def post(self, request, dataset_id):
        # create status and comment from the request
        review_status = request.data.get('review_status')
        review_comment = request.data.get('review_comment', '')

        # check the status is not in closed if so return error response
        if review_status not in CLOSED_STATUSES:
            return Response({'error': 'review_status must be approved or rejected'}, status=400)

        with connection.cursor() as cursor:
            # fetch current dataset and its review status
            cursor.execute(
                "SELECT dataset_id, review_status FROM dataset WHERE dataset_id = %s AND deleted_at IS NULL",
                [dataset_id]
            )
            row = cursor.fetchone()
            # check the dataset exists
            if not row:
                return Response({'error': 'Dataset not found'}, status=404)
            # only allow reviewing datasets that are still pending
            if row[1] != 'pending':
                return Response({'error': 'Only pending datasets can be reviewed'}, status=400)

            # update the dataset table review status
            cursor.execute("UPDATE dataset SET review_status = %s, review_comment = %s WHERE dataset_id = %s", [review_status, review_comment, dataset_id])

        logger.info(f"[Dataset] Dataset {dataset_id} {review_status}")
        # return success reponse
        return Response({'message': f'Dataset {review_status} successfully'})


# modify dataset class which updates description, pull_frequency, and review_status
class ModifyDataset(APIView):
    def post(self, request, dataset_id):
        # get values from the request
        description = request.data.get('description')
        pull_frequency = request.data.get('pull_frequency')
        review_status = request.data.get('review_status')

        # check the review status is not in valid
        if review_status not in VALID_STATUSES:
            return Response({'error': 'Invalid review_status'}, status=400)

        with connection.cursor() as cursor:
            # get the dataset and ensure its not deleted
            cursor.execute("SELECT dataset_id FROM dataset WHERE dataset_id = %s AND deleted_at IS NULL", [dataset_id])
            # check the dataset exists
            if not cursor.fetchone():
                return Response({'error': 'Dataset not found'}, status=404)

            # update the dataset table
            cursor.execute("""
                UPDATE dataset
                SET description = %s, pull_frequency = %s, review_status = %s
                WHERE dataset_id = %s
            """, [description, pull_frequency, review_status, dataset_id])

        logger.info(f"[Dataset] Dataset {dataset_id} modified")
        # return success response
        return Response({'message': 'Dataset updated successfully'})

# delete dataset class which soft deletes a dataset and cascades to its satellites
class DeleteDataset(APIView):
    def delete(self, request, dataset_id):
        with connection.cursor() as cursor:
            # select the dataset ensuring its not already deleted
            cursor.execute("SELECT dataset_id FROM dataset WHERE dataset_id = %s AND deleted_at IS NULL", [dataset_id])
            # check to make sure the dataset exists
            if not cursor.fetchone():
                return Response({'error': 'Dataset not found'}, status=404)

            # get the current time
            cursor.execute("SELECT NOW()")
            deleted_at = cursor.fetchone()[0]

            # update dataset table and satellite table with deleted at columns
            cursor.execute("UPDATE dataset SET deleted_at = %s WHERE dataset_id = %s", [deleted_at, dataset_id])
            cursor.execute("UPDATE satellite SET deleted_at = %s WHERE dataset_id = %s AND deleted_at IS NULL", [deleted_at, dataset_id])

        logger.info(f"[Dataset] Dataset {dataset_id} soft-deleted")
        # return success response
        return Response({'message': 'Dataset deleted successfully'})

# sources endpoint which scrapes the CelesTrak current data page and returns groups not yet in the database
class DatasetSources(APIView):
    def get(self, request):
        # try get new datasets from celestrak
        try:
            response = requests.get('https://celestrak.org/NORAD/elements/', timeout=30)
            response.raise_for_status()
            groups = re.findall(r'GROUP=([^&"\']+)', response.text)
            groups = list(dict.fromkeys(groups))
        except Exception as e:
            logger.info(f"[Dataset] Failed to fetch CelesTrak group list: {e}")
            return Response({'error': f'Failed to fetch CelesTrak groups: {str(e)}'}, status=502)

        with connection.cursor() as cursor:
            # get current dataset urls
            cursor.execute("SELECT source_url FROM dataset WHERE deleted_at IS NULL")
            existing_urls = {row[0] for row in cursor.fetchall()}

            # get not deleted datasets
            cursor.execute("""
                SELECT source_url, dataset_name, description, pull_frequency
                FROM dataset WHERE deleted_at IS NOT NULL
            """)
            deleted_datasets = {
                row[0]: {
                    'dataset_name': row[1],
                    'description': row[2],
                    'pull_frequency': row[3],
                }
                for row in cursor.fetchall()
            }

        # create an available list
        available = []
        for group in groups:
            url = f"{CELESTRAK_BASE}?GROUP={group}&FORMAT=json"
            if url in existing_urls:
                continue
            entry = {'group': group, 'source_url': url}
            if url in deleted_datasets:
                entry['previously_deleted'] = True
                entry.update(deleted_datasets[url])
            available.append(entry)

        return Response(available)

# add dataset class which validates a CelesTrak group and inserts a new dataset row
class AddDataset(APIView):
    def post(self, request):
        # get fields from the request
        group = request.data.get('group', '').strip()
        dataset_name = request.data.get('dataset_name', '').strip()
        description = request.data.get('description', '')
        pull_frequency = request.data.get('pull_frequency', '')

        # check the required fields exist
        if not group:
            return Response({'error': 'group is required'}, status=400)
        if not dataset_name:
            return Response({'error': 'dataset_name is required'}, status=400)

        # create the source url
        source_url = f"{CELESTRAK_BASE}?GROUP={group}&FORMAT=json"

        with connection.cursor() as cursor:
            # restore a soft-deleted dataset — no CelesTrak validation needed
            cursor.execute(
                "SELECT dataset_id, deleted_at FROM dataset WHERE source_url = %s AND deleted_at IS NOT NULL",
                [source_url]
            )
            existing = cursor.fetchone()
            # if existing update the dataset table and satellite table
            if existing:
                dataset_id, dataset_deleted_at = existing
                cursor.execute(
                    "UPDATE dataset SET deleted_at = NULL, dataset_name = %s, description = %s, pull_frequency = %s WHERE dataset_id = %s",
                    [dataset_name, description, pull_frequency, dataset_id]
                )
                cursor.execute(
                    "UPDATE satellite SET deleted_at = NULL WHERE dataset_id = %s AND deleted_at = %s",
                    [dataset_id, dataset_deleted_at]
                )
                return Response({'message': 'Dataset restored successfully', 'dataset_id': dataset_id}, status=200)

            # reject if an active dataset with this url already exists
            cursor.execute(
                "SELECT dataset_id FROM dataset WHERE source_url = %s AND deleted_at IS NULL",
                [source_url]
            )
            if cursor.fetchone():
                return Response({'error': 'A dataset for this group already exists'}, status=400)

        # new dataset validate the group against CelesTrak
        try:
            response = requests.get(source_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list) or len(data) == 0:
                return Response({'error': 'Invalid or empty CelesTrak group'}, status=400)
        except ValueError:
            # CelesTrak rate limited — check DB cache as fallback
            logger.info(f"[Dataset] CelesTrak rate limited while validating group '{group}', checking cache")
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
            logger.info(f"[Dataset] Failed to validate CelesTrak group '{group}': {e}")
            return Response({'error': f'Failed to validate CelesTrak group: {str(e)}'}, status=502)

        # insert the new dataset into the dataset table
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

        logger.info(f"[Dataset] New dataset '{dataset_name}' created (id={dataset_id}, group={group})")
        # return success response
        return Response({'message': 'Dataset created successfully', 'dataset_id': dataset_id}, status=201)
