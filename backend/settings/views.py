# rest api imports, and command and threading imports for updating trajectory asynchronously
import logging
import threading
from datetime import datetime, timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.management import call_command

logger = logging.getLogger('sattrack')

# module-level state shared across requests within a single worker process.
# _trajectory_running prevents overlapping rebuilds.
# _last_trajectory_update records when the last successful rebuild finished
# so the admin page can display "last updated X minutes ago" without a DB query.
_trajectory_lock = threading.Lock()
_trajectory_running = False
_last_trajectory_update = None   # datetime (UTC) of last completed rebuild
_last_trajectory_error = None    # error message if the last rebuild failed


# returns the current trajectory update status — no auth required so the admin
# page can poll it freely, but the information is harmless
class TrajectoryStatus(APIView):
    def get(self, request):
        with _trajectory_lock:
            running = _trajectory_running
            last_update = _last_trajectory_update
            last_error = _last_trajectory_error

        return Response({
            'running': running,
            'last_updated_at': last_update.isoformat() if last_update else None,
            'last_error': last_error,
        })


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
            global _trajectory_running, _last_trajectory_update, _last_trajectory_error
            try:
                call_command('update_trajectories')
                with _trajectory_lock:
                    _last_trajectory_update = datetime.now(timezone.utc)
                    _last_trajectory_error = None
            except Exception as e:
                logger.error(f"[Settings] Trajectory update failed: {e}")
                with _trajectory_lock:
                    _last_trajectory_error = str(e)
            finally:
                with _trajectory_lock:
                    _trajectory_running = False

        thread = threading.Thread(target=run_and_clear, daemon=True)
        thread.start()
        logger.info(f"[Settings] Trajectory update triggered by '{request.user.username}'")
        return Response({'message': 'Trajectory update started'})
