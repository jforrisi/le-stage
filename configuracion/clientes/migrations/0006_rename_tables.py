# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("clientes", "0005_formapago"),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE clientes_cliente RENAME TO config_cliente_maestro;",
            reverse_sql="ALTER TABLE config_cliente_maestro RENAME TO clientes_cliente;",
        ),
        migrations.RunSQL(
            "ALTER TABLE clientes_formapago RENAME TO config_formapago;",
            reverse_sql="ALTER TABLE config_formapago RENAME TO clientes_formapago;",
        ),
    ]
