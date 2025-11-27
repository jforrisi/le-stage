# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("transacciones", "0002_restructure_transaccion"),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE config_transaccion RENAME TO config_transacciones;",
            reverse_sql="ALTER TABLE config_transacciones RENAME TO config_transaccion;",
        ),
    ]
