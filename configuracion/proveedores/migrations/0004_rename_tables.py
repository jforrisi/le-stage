# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("proveedores", "0003_alter_proveedor_codigo_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE proveedores_proveedor RENAME TO config_proveedores_maestro;",
            reverse_sql="ALTER TABLE config_proveedores_maestro RENAME TO proveedores_proveedor;",
        ),
    ]
