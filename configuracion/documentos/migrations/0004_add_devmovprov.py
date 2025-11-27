# Generated manually

from django.db import migrations


def agregar_devmovprov(apps, schema_editor):
    """Agregar documento devmovprov (Devolución Movimiento Proveedor)"""
    Documento = apps.get_model('documentos', 'Documento')
    
    # Verificar si ya existe usando raw SQL para evitar problemas con el nombre de tabla
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM config_documentos_maestro WHERE codigo = %s", ['devmovprov'])
        existe = cursor.fetchone()[0] > 0
        
        if not existe:
            cursor.execute(
                "INSERT INTO config_documentos_maestro (codigo, nombre, descripcion, activo) VALUES (%s, %s, %s, %s)",
                ['devmovprov', 'Devolución Movimiento Proveedor', 'Devolución compra sin documento', 'SI']
            )


def eliminar_devmovprov(apps, schema_editor):
    """Eliminar documento devmovprov"""
    Documento = apps.get_model('documentos', 'Documento')
    Documento.objects.filter(codigo='devmovprov').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('documentos', '0003_rename_tables'),
    ]

    operations = [
        migrations.RunPython(agregar_devmovprov, eliminar_devmovprov),
    ]

