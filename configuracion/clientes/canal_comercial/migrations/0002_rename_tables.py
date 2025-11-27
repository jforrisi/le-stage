# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("canal_comercial", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE canal_comercial_canalcomercial RENAME TO config_cliente_canalcomercial;",
            reverse_sql="ALTER TABLE config_cliente_canalcomercial RENAME TO canal_comercial_canalcomercial;",
        ),
    ]
