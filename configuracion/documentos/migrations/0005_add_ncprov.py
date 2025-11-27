# Generated manually

from django.db import migrations


def agregar_ncprov(apps, schema_editor):
    """Agregar documento ncprov (Nota de Crédito Proveedor)"""
    Documento = apps.get_model('documentos', 'Documento')
    
    # Verificar si ya existe usando raw SQL para evitar problemas con el nombre de tabla
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM config_documentos_maestro WHERE codigo = %s", ['ncprov'])
        existe = cursor.fetchone()[0] > 0
        
        if not existe:
            cursor.execute(
                "INSERT INTO config_documentos_maestro (codigo, nombre, descripcion, activo) VALUES (%s, %s, %s, %s)",
                ['ncprov', 'Nota de Crédito Proveedor', 'Nota de crédito relacionada con factura proveedor', 'SI']
            )


def eliminar_ncprov(apps, schema_editor):
    """Eliminar documento ncprov"""
    Documento = apps.get_model('documentos', 'Documento')
    Documento.objects.filter(codigo='ncprov').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('documentos', '0004_add_devmovprov'),
    ]

    operations = [
        migrations.RunPython(agregar_ncprov, eliminar_ncprov),
    ]

