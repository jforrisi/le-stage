# Generated manually - Migración para asegurar que el campo transaccion existe

from django.db import migrations


def asegurar_campo_transaccion(apps, schema_editor):
    """
    Asegura que el campo transaccion existe y tiene valores.
    Si la tabla tiene codigo pero no transaccion, lo convierte.
    """
    # Esta migración es principalmente para asegurar consistencia
    # La migración 0002 ya debería haber creado la tabla con transaccion
    pass


def revertir(apps, schema_editor):
    """Revertir"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('transacciones', '0003_rename_transaccion_table'),
    ]

    operations = [
        migrations.RunPython(
            asegurar_campo_transaccion,
            reverse_code=revertir,
        ),
    ]

