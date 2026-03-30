from django.db import migrations

class Migration(migrations.Migration):

    dependencies = []

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