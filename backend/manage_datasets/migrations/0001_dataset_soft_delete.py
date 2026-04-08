# import migrations
from django.db import migrations

# create the migration class
class Migration(migrations.Migration):
    # create empty list of dependencies
    dependencies = []

    # create the migration operation
    operations = [
        # create change and reverse so migration can be reversed at the deleted_at column to the dataset table and its associated reverse operation
        migrations.RunSQL(
            sql="ALTER TABLE dataset ADD COLUMN deleted_at DATETIME NULL DEFAULT NULL;",
            reverse_sql="ALTER TABLE dataset DROP COLUMN deleted_at;"
        )
    ]
