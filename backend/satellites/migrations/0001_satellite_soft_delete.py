from django.db import migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE satellite ADD COLUMN deleted_at DATETIME NULL DEFAULT NULL;",
            reverse_sql="ALTER TABLE satellite DROP COLUMN deleted_at;"
        )
    ]
