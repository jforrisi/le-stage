# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("documentos", "0002_auto_20251119_1451"),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE documentos_documento RENAME TO config_documentos_maestro;",
            reverse_sql="ALTER TABLE config_documentos_maestro RENAME TO documentos_documento;",
        ),
    ]
