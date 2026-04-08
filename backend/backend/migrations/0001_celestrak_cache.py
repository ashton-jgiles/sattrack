# import migrations
from django.db import migrations

# create the migration class
class Migration(migrations.Migration):
    # create an empty list of dependencies
    dependencies = []

    # create the forward and reverse operation to create the celestrak cache table needed for caching satellites
    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS celestrak_cache (
                    url        VARCHAR(500) NOT NULL PRIMARY KEY,
                    data       LONGTEXT     NOT NULL,
                    cached_at  DATETIME     NOT NULL
                );
            """,
            reverse_sql="DROP TABLE IF EXISTS celestrak_cache;"
        )
    ]
    