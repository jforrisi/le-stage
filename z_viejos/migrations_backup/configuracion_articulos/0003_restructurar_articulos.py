# Generated migration to restructure Articulo model

from django.db import migrations, models
import django.db.models.deletion


def poblar_tipos_articulo(apps, schema_editor):
    """Poblar tipos de artículo iniciales"""
    TipoArticulo = apps.get_model('articulos', 'TipoArticulo')
    
    tipos = [
        {'codigo': 'SER', 'nombre': 'Servicios', 'stockeable': 'NO', 'se_compra': 'SI'},
        {'codigo': 'INS', 'nombre': 'Insumos', 'stockeable': 'SI', 'se_compra': 'SI'},
        {'codigo': 'PPR', 'nombre': 'Productos en Proceso', 'stockeable': 'SI', 'se_compra': 'NO'},
        {'codigo': 'PTE', 'nombre': 'Producto Terminado', 'stockeable': 'SI', 'se_compra': 'NO'},
        {'codigo': 'PRE', 'nombre': 'Productos para Reventa', 'stockeable': 'SI', 'se_compra': 'SI'},
        {'codigo': 'MAQ', 'nombre': 'Maquinaria', 'stockeable': 'SI', 'se_compra': 'SI'},
        {'codigo': 'INM', 'nombre': 'Inmuebles', 'stockeable': 'SI', 'se_compra': 'SI'},
        {'codigo': 'OBU', 'nombre': 'Otros Bienes de Uso', 'stockeable': 'SI', 'se_compra': 'SI'},
        {'codigo': 'MAN', 'nombre': 'Mantenimiento', 'stockeable': 'SI', 'se_compra': 'SI'},
        {'codigo': 'PTR', 'nombre': 'Presupuesto de Trabajo', 'stockeable': 'NO', 'se_compra': 'NO'},
    ]
    
    for tipo_data in tipos:
        TipoArticulo.objects.get_or_create(
            codigo=tipo_data['codigo'],
            defaults={
                'nombre': tipo_data['nombre'],
                'stockeable': tipo_data['stockeable'],
                'se_compra': tipo_data['se_compra'],
            }
        )


def revertir_migracion(apps, schema_editor):
    """Revertir la migración"""
    TipoArticulo = apps.get_model('articulos', 'TipoArticulo')
    TipoArticulo.objects.filter(codigo__in=['SER', 'INS', 'PPR', 'PTE', 'PRE', 'MAQ', 'INM', 'OBU', 'MAN', 'PTR']).delete()


def migrar_datos_articulos(apps, schema_editor):
    """Migrar datos existentes de Articulo"""
    Articulo = apps.get_model('articulos', 'Articulo')
    TipoArticulo = apps.get_model('articulos', 'TipoArticulo')
    
    # Obtener un tipo por defecto o crear uno temporal
    tipo_default = None
    try:
        tipo_default = TipoArticulo.objects.first()
    except:
        pass
    
    # Si hay artículos existentes, migrar sus datos
    for articulo in Articulo.objects.all():
        if articulo.ardescri and not articulo.nombre:
            articulo.nombre = articulo.ardescri
        if not articulo.tipo_articulo_id and tipo_default:
            articulo.tipo_articulo = tipo_default
        articulo.save()


class Migration(migrations.Migration):

    dependencies = [
        ('articulos', '0001_initial'),
    ]

    operations = [
        # Crear nuevos modelos primero
        migrations.CreateModel(
            name='TipoArticulo',
            fields=[
                ('codigo', models.CharField(help_text='3 letras representativas (ej: SER, INS, PRO)', max_length=3, primary_key=True, serialize=False, unique=True, verbose_name='Código')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('stockeable', models.CharField(choices=[('SI', 'Sí'), ('NO', 'No')], default='NO', help_text='Si computa stock o no', max_length=2, verbose_name='Stockeable')),
                ('se_compra', models.CharField(choices=[('SI', 'Sí'), ('NO', 'No')], default='SI', help_text='Si se puede comprar este tipo de artículo', max_length=2, verbose_name='Se Compra')),
            ],
            options={
                'verbose_name': 'Tipo de Artículo',
                'verbose_name_plural': 'Tipos de Artículo',
                'ordering': ['codigo'],
            },
        ),
        migrations.CreateModel(
            name='Familia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True, verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Familia',
                'verbose_name_plural': 'Familias',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='SubFamilia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('familia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subfamilias', to='articulos.familia', verbose_name='Familia')),
            ],
            options={
                'verbose_name': 'Sub Familia',
                'verbose_name_plural': 'Sub Familias',
                'ordering': ['familia', 'nombre'],
                'unique_together': {('familia', 'nombre')},
            },
        ),
        
        # Agregar nuevos campos a Articulo como nullable
        migrations.AddField(
            model_name='articulo',
            name='nombre',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Nombre'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='tipo_articulo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='articulos', to='articulos.tipoarticulo', verbose_name='Tipo de Artículo'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='idsubfamilia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articulos', to='articulos.subfamilia', verbose_name='Sub Familia'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='producto_id',
            field=models.CharField(blank=True, help_text='Formato: XXX000001 (3 letras del tipo + 6 números)', max_length=10, null=True, unique=True, verbose_name='ID Producto'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='precio_venta',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Precio de Venta'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='moneda_venta',
            field=models.CharField(choices=[('UYU', 'Peso Uruguayo'), ('USD', 'Dólar Estadounidense'), ('EUR', 'Euro')], default='UYU', max_length=3, verbose_name='Moneda de Venta'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='UNIDAD_VENTA',
            field=models.CharField(choices=[('BIDON', 'Bidón'), ('BOLSA', 'Bolsa'), ('CAJA', 'Caja'), ('FRASCO', 'Frasco'), ('GRAMOS', 'Gramos'), ('HECTAREAS', 'Hectáreas'), ('HORAS', 'Horas'), ('KILOMETROS', 'Kilómetros'), ('KILOS', 'Kilos'), ('LITROS', 'Litros'), ('METROS', 'Metros'), ('METROS_CUADRADOS', 'Metros cuadrados'), ('METROS_CUBICOS', 'Metros cúbicos'), ('TONELADAS', 'Toneladas'), ('UNITARIO', 'Unitario')], default='UNITARIO', max_length=20, verbose_name='Unidad de Venta'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='UNIDAD_STOCK',
            field=models.CharField(choices=[('BIDON', 'Bidón'), ('BOLSA', 'Bolsa'), ('CAJA', 'Caja'), ('FRASCO', 'Frasco'), ('GRAMOS', 'Gramos'), ('HECTAREAS', 'Hectáreas'), ('HORAS', 'Horas'), ('KILOMETROS', 'Kilómetros'), ('KILOS', 'Kilos'), ('LITROS', 'Litros'), ('METROS', 'Metros'), ('METROS_CUADRADOS', 'Metros cuadrados'), ('METROS_CUBICOS', 'Metros cúbicos'), ('TONELADAS', 'Toneladas'), ('UNITARIO', 'Unitario')], default='UNITARIO', max_length=20, verbose_name='Unidad de Stock'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='UNIDAD_COMPRA',
            field=models.CharField(choices=[('BIDON', 'Bidón'), ('BOLSA', 'Bolsa'), ('CAJA', 'Caja'), ('FRASCO', 'Frasco'), ('GRAMOS', 'Gramos'), ('HECTAREAS', 'Hectáreas'), ('HORAS', 'Horas'), ('KILOMETROS', 'Kilómetros'), ('KILOS', 'Kilos'), ('LITROS', 'Litros'), ('METROS', 'Metros'), ('METROS_CUADRADOS', 'Metros cuadrados'), ('METROS_CUBICOS', 'Metros cúbicos'), ('TONELADAS', 'Toneladas'), ('UNITARIO', 'Unitario')], default='UNITARIO', max_length=20, verbose_name='Unidad de Compra'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='ACTIVO_COMERCIAL',
            field=models.CharField(choices=[('SI', 'Sí'), ('NO', 'No')], default='SI', max_length=2, verbose_name='Activo Comercial'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='ACTIVO_STOCK',
            field=models.CharField(choices=[('SI', 'Sí'), ('NO', 'No')], default='SI', max_length=2, verbose_name='Activo Stock'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='ACTIVO_COMPRAS',
            field=models.CharField(choices=[('SI', 'Sí'), ('NO', 'No')], default='SI', max_length=2, verbose_name='Activo Compras'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='ACTIVO_PRODUCCION',
            field=models.CharField(choices=[('SI', 'Sí'), ('NO', 'No')], default='NO', max_length=2, verbose_name='Activo Producción'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='LOTEABLE',
            field=models.CharField(choices=[('SI', 'Sí'), ('NO', 'No')], default='NO', max_length=2, verbose_name='Loteable'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='UNIDAD_PESO',
            field=models.CharField(blank=True, choices=[('BIDON', 'Bidón'), ('BOLSA', 'Bolsa'), ('CAJA', 'Caja'), ('FRASCO', 'Frasco'), ('GRAMOS', 'Gramos'), ('HECTAREAS', 'Hectáreas'), ('HORAS', 'Horas'), ('KILOMETROS', 'Kilómetros'), ('KILOS', 'Kilos'), ('LITROS', 'Litros'), ('METROS', 'Metros'), ('METROS_CUADRADOS', 'Metros cuadrados'), ('METROS_CUBICOS', 'Metros cúbicos'), ('TONELADAS', 'Toneladas'), ('UNITARIO', 'Unitario')], max_length=20, null=True, verbose_name='Unidad de Peso'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='PESO',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=15, null=True, verbose_name='Peso'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='UNIDAD_VOLUMEN',
            field=models.CharField(blank=True, choices=[('BIDON', 'Bidón'), ('BOLSA', 'Bolsa'), ('CAJA', 'Caja'), ('FRASCO', 'Frasco'), ('GRAMOS', 'Gramos'), ('HECTAREAS', 'Hectáreas'), ('HORAS', 'Horas'), ('KILOMETROS', 'Kilómetros'), ('KILOS', 'Kilos'), ('LITROS', 'Litros'), ('METROS', 'Metros'), ('METROS_CUADRADOS', 'Metros cuadrados'), ('METROS_CUBICOS', 'Metros cúbicos'), ('TONELADAS', 'Toneladas'), ('UNITARIO', 'Unitario')], max_length=20, null=True, verbose_name='Unidad de Volumen'),
        ),
        migrations.AddField(
            model_name='articulo',
            name='VOLUMEN',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=15, null=True, verbose_name='Volumen'),
        ),
        
        # Poblar tipos de artículo
        migrations.RunPython(poblar_tipos_articulo, revertir_migracion),
        
        # Migrar datos de artículos existentes
        migrations.RunPython(migrar_datos_articulos, migrations.RunPython.noop),
        
        # Cambiar ordenamiento
        migrations.AlterModelOptions(
            name='articulo',
            options={'ordering': ['producto_id'], 'verbose_name': 'Artículo', 'verbose_name_plural': 'Artículos'},
        ),
    ]

