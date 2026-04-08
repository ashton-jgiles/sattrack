# rest api imports, and command and threading imports for updating trajectory asynchronously
import logging
import threading
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.management import call_command

logger = logging.getLogger('sattrack')

# module-level flag to prevent overlapping trajectory rebuilds within a single worker process
_trajectory_lock = threading.Lock()
_trajectory_running = False


# update trajectory endpoint — triggers a full trajectory rebuild in a background thread
# requires level 4 (administrator); only one rebuild can run at a time per worker process
class UpdateTrajectories(APIView):
    def post(self, request):
        if getattr(request.user, 'level_access', 0) < 4:
            return Response({'error': 'Insufficient permissions'}, status=403)

        global _trajectory_running
        with _trajectory_lock:
            if _trajectory_running:
                return Response({'error': 'Trajectory update already in progress'}, status=409)
            _trajectory_running = True

        def run_and_clear():
            global _trajectory_running
            try:
                call_command('update_trajectories')
            finally:
                _trajectory_running = False

        thread = threading.Thread(target=run_and_clear, daemon=True)
        thread.start()
        logger.info(f"[Settings] Trajectory update triggered by '{request.user.username}'")
        return Response({'message': 'Trajectory update started'})
