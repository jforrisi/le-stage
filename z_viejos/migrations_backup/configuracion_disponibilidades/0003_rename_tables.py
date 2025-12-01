# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("disponibilidades", "0002_disponibilidad_fecha_ingreso_sistema_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE disponibilidades_disponibilidad RENAME TO config_disponibilidades;",
            reverse_sql="ALTER TABLE config_disponibilidades RENAME TO disponibilidades_disponibilidad;",
        ),
    ]
