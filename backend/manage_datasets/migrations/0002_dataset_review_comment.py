# import migrations
from django.db import migrations

# create the migration class
class Migration(migrations.Migration):
    # create list of dependencies
    dependencies = [
        ('manage_datasets', '0001_dataset_soft_delete'),
    ]

    # create the migration operation
    operations = [
        # create change and reverse so migration can be reversed at the review_comment column to the dataset table and its associated reverse operation
        migrations.RunSQL(
            sql="ALTER TABLE dataset ADD COLUMN review_comment TEXT NULL DEFAULT NULL;",
            reverse_sql="ALTER TABLE dataset DROP COLUMN review_comment;"
        )
    ]
