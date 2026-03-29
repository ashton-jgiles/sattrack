from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import time

celestrak_cache = {}
CACHE_TTL = 300  # 5 minutes

def fetch_celestrak_cached(url):
    now = time.time()
    if url in celestrak_cache:
        data, timestamp = celestrak_cache[url]
        if now - timestamp < CACHE_TTL:
            return data
    
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    celestrak_cache[url] = (data, now)
    return data

def derive_orbit_type(mean_motion, inclination):
    # Mean motion in revs/day
    # GEO: ~1 rev/day, MEO: 2-6, LEO: 11-16, HEO: highly elliptical
    if mean_motion < 1.5:
        return 'GEO'
    elif mean_motion < 6:
        return 'MEO'
    elif inclination > 60 and mean_motion < 3:
        return 'HEO'
    else:
        return 'LEO'
     
class DeleteSatellite(APIView):
    def delete(self, request, satellite_id):
        with connection.cursor() as cursor:
            # check satellite exists
            cursor.execute("SELECT satellite_id FROM satellite WHERE satellite_id = %s", [satellite_id])

            if not cursor.fetchone():
                return Response({'error': 'Satellite not found'}, status=404)
            
            # Delete in order — child tables first
            cursor.execute("DELETE FROM trajectory WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM communicates_with WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM deploys_payload WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM earth_science WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM oceanic_science WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM weather WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM navigation WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM internet WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM research WHERE satellite_id = %s", (satellite_id,))
            cursor.execute("DELETE FROM satellite WHERE satellite_id = %s", (satellite_id,))

        return Response({'message': 'Satellite deleted successfully'})

class ModifySatellite(APIView):
    def post(self, request):
        satellite     = request.data.get('satellite', {})
        communication = request.data.get('communication', {})
        type_data     = request.data.get('type_data', {})

        satellite_id = satellite.get('satellite_id')
        if not satellite_id:
            return Response({'error': 'satellite_id is required'}, status=400)

        with connection.cursor() as cursor:

            # Update satellite table 
            cursor.execute("""
                UPDATE satellite
                SET description = %s, classification = %s
                WHERE satellite_id = %s
            """, (
                satellite.get('description'),
                satellite.get('classification'),
                satellite_id,
            ))

            # Update communicates_with table 
            if communication.get('communication_frequency'):
                cursor.execute("""
                    UPDATE communicates_with
                    SET communication_frequency = %s
                    WHERE satellite_id = %s
                """, (
                    communication.get('communication_frequency'),
                    satellite_id,
                ))

            # Update subclass type table 
            subclass_tables = [
                'earth_science', 'oceanic_science', 'weather',
                'navigation', 'internet', 'research'
            ]

            for table in subclass_tables:
                cursor.execute(
                    f"SELECT satellite_id FROM {table} WHERE satellite_id = %s",
                    (satellite_id,)
                )
                if cursor.fetchone():
                    # Build dynamic UPDATE from type_data keys
                    if type_data:
                        set_clause = ", ".join([f"{k} = %s" for k in type_data.keys()])
                        values = list(type_data.values()) + [satellite_id]
                        cursor.execute(
                            f"UPDATE {table} SET {set_clause} WHERE satellite_id = %s",
                            values
                        )
                    break

        return Response({'message': 'Satellite updated successfully'})   
    
class NewSatellitesFromDataset(APIView):
    def get(self, request, dataset_id):
        search = request.GET.get('search', '').strip()
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 50))
        offset = (page - 1) * limit

        with connection.cursor() as cursor:
            # get the dataset source url
            cursor.execute("SELECT source_url FROM dataset WHERE dataset_id = %s", [dataset_id])
            row = cursor.fetchone()
            if not row:
                return Response({'error': 'Dataset not found'}, status=404)
            url = row[0]

            # get all existing NORAD ids in the database
            cursor.execute("SELECT norad_id FROM satellite")
            existing_norad_ids = {str(row[0]) for row in cursor.fetchall()}

        # fetch data from celestrak
        try:
            all_sats = fetch_celestrak_cached(url)
        except Exception as e:
            return Response({'error': f'Failed to fetch CelesTrak data: {str(e)}'}, status=502)
        
        # filter out satellites already in database
        new_sats = [
            sat for sat in all_sats
            if str(sat.get('NORAD_CAT_ID', '')) not in existing_norad_ids
        ]

        # apply search filter
        if search:
            search_lower = search.lower()
            new_sats = [
                sat for sat in new_sats
                if search_lower in sat.get('OBJECT_NAME', '').lower()
                or search_lower in str(sat.get('NORAD_CAT_ID', ''))
            ]
        
        # paginate the results
        total = len(new_sats)
        pages = max(1, (total + limit - 1) // limit)
        results = new_sats[offset: offset + limit]

        # format the response
        formatted = [
            {
                'name': sat.get('OBJECT_NAME'),
                'norad_id': str(sat.get('NORAD_CAT_ID')),
                'object_id': sat.get('OBJECT_ID'),
                'classification': sat.get('CLASSIFICATION_TYPE', 'U'),
                'inclination': sat.get('INCLINATION'),
                'eccentricity': sat.get('ECCENTRICITY'),
                'mean_motion': sat.get('MEAN_MOTION'),
                'epoch': sat.get('EPOCH'),
                'orbit_type':  derive_orbit_type(sat.get('MEAN_MOTION', 0), sat.get('INCLINATION', 0)),
            }
            for sat in results
        ]

        return Response({
            'results': formatted,
            'total': total,
            'page': page,
            'pages': pages,
            'limit': limit,
        })
    