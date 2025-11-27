# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("articulos", "0010_iva_articulo_iva"),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE articulos_articulo RENAME TO config_articulos_maestro;",
            reverse_sql="ALTER TABLE config_articulos_maestro RENAME TO articulos_articulo;",
        ),
        migrations.RunSQL(
            "ALTER TABLE articulos_codigoproveedorcompra RENAME TO config_codigoproveedorcompra;",
            reverse_sql="ALTER TABLE config_codigoproveedorcompra RENAME TO articulos_codigoproveedorcompra;",
        ),
        migrations.RunSQL(
            "ALTER TABLE articulos_familia RENAME TO config_articulos_familia;",
            reverse_sql="ALTER TABLE config_articulos_familia RENAME TO articulos_familia;",
        ),
        migrations.RunSQL(
            "ALTER TABLE articulos_iva RENAME TO config_iva;",
            reverse_sql="ALTER TABLE config_iva RENAME TO articulos_iva;",
        ),
        migrations.RunSQL(
            "ALTER TABLE articulos_moneda RENAME TO config_moneda;",
            reverse_sql="ALTER TABLE config_moneda RENAME TO articulos_moneda;",
        ),
        migrations.RunSQL(
            "ALTER TABLE articulos_subfamilia RENAME TO config_articulos_subfamilia;",
            reverse_sql="ALTER TABLE config_articulos_subfamilia RENAME TO articulos_subfamilia;",
        ),
        migrations.RunSQL(
            "ALTER TABLE articulos_tipoarticulo RENAME TO config_articulos_tipoarticulo;",
            reverse_sql="ALTER TABLE config_articulos_tipoarticulo RENAME TO articulos_tipoarticulo;",
        ),
    ]
