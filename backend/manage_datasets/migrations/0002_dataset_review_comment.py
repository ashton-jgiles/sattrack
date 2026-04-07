from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manage_datasets', '0001_dataset_soft_delete'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE dataset ADD COLUMN review_comment TEXT NULL DEFAULT NULL;",
            reverse_sql="ALTER TABLE dataset DROP COLUMN review_comment;"
        )
    ]
