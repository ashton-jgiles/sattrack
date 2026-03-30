# rest api imports
from rest_framework.views import APIView
from rest_framework.response import Response

# update trajectory endpoint to create background thread to update all trajectory
class UpdateTrajectories(APIView):
    def post(self, request):
        from django.core.management import call_command
        import threading
        thread = threading.Thread(
            target=call_command,
            args=('update_trajectories',),
            daemon=True
        )
        thread.start()
        return Response({'message': 'Trajectory update started'})