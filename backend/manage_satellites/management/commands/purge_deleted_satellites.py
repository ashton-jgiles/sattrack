from django.core.management.base import BaseCommand
from django.db import connection, transaction

RETENTION_DAYS = 30


class Command(BaseCommand):
    help = 'Hard-deletes satellites soft-deleted more than 30 days ago'

    def handle(self, *args, **options):
        self.stdout.write(f'[Purge] Retention window: {RETENTION_DAYS} days')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT satellite_id, name
                FROM satellite
                WHERE deleted_at IS NOT NULL
                AND deleted_at < NOW() - INTERVAL %s DAY
            """, [RETENTION_DAYS])
            candidates = cursor.fetchall()

        if not candidates:
            self.stdout.write('[Purge] No satellites past retention window.')
            return

        self.stdout.write(f'[Purge] {len(candidates)} satellite(s) to purge.')

        for satellite_id, name in candidates:
            try:
                with transaction.atomic(), connection.cursor() as cursor:
                    cursor.execute("DELETE FROM trajectory WHERE satellite_id = %s", [satellite_id])
                    cursor.execute("DELETE FROM communicates_with WHERE satellite_id = %s", [satellite_id])
                    cursor.execute("DELETE FROM deploys_payload WHERE satellite_id = %s", [satellite_id])
                    for table in ['earth_science', 'oceanic_science', 'weather', 'navigation', 'internet', 'research']:
                        cursor.execute(f"DELETE FROM {table} WHERE satellite_id = %s", [satellite_id])
                    cursor.execute("DELETE FROM satellite WHERE satellite_id = %s", [satellite_id])
                self.stdout.write(f'[Purge] Deleted: {name} (id={satellite_id})')
            except Exception as e:
                self.stderr.write(f'[Purge] Failed to delete {name} (id={satellite_id}): {e}')

        self.stdout.write('[Purge] Done.')
