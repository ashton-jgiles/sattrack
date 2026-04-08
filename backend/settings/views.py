# rest api imports, and command and threading imports for updating trajectory asynchronously
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.management import call_command
import threading

# update trajectory endpoint to create background thread to update all trajectory
class UpdateTrajectories(APIView):
    def post(self, request):
        # create the thread
        thread = threading.Thread(
            # call the command
            target=call_command,
            args=('update_trajectories',),
            daemon=True
        )
        # start the start
        thread.start()
        # return the success response
        return Response({'message': 'Trajectory update started'})
    