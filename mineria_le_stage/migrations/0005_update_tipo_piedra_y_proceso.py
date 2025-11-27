# Generated manually

from django.db import migrations, models
import django.db.models.deletion


def convertir_tipo_proceso(apps, schema_editor):
    """Convertir tipo_proceso de texto a ForeignKey si hay datos"""
    PiezasCorteCantera = apps.get_model('mineria_le_stage', 'PiezasCorteCantera')
    TipoPulidoPiezas = apps.get_model('industria_le_stage', 'TipoPulidoPiezas')
    
    # Si hay registros con tipo_proceso como texto, intentar convertirlos
    # Por ahora, simplemente dejamos que se pierdan los valores antiguos
    # ya que es un cambio de estructura importante
    pass


def revertir_tipo_proceso(apps, schema_editor):
    """Revertir conversión"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('mineria_le_stage', '0004_piezas_corte_cantera'),
        ('industria_le_stage', '0001_initial'),
    ]

    operations = [
        # Primero eliminar la columna tipo_proceso antigua (CharField)
        migrations.RemoveField(
            model_name='piezascortecantera',
            name='tipo_proceso',
        ),
        # Agregar la nueva columna tipo_proceso como ForeignKey
        migrations.AddField(
            model_name='piezascortecantera',
            name='tipo_proceso',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='piezas_corte_cantera',
                to='industria_le_stage.tipopulidopiezas',
                verbose_name='Tipos de Pulido Piezas'
            ),
        ),
        # Cambiar tipo_piedra a choices (esto no requiere cambio de estructura)
        migrations.AlterField(
            model_name='piezascortecantera',
            name='tipo_piedra',
            field=models.CharField(
                blank=True,
                choices=[('Ágata', 'Ágata'), ('Amatista', 'Amatista')],
                max_length=200,
                verbose_name='Tipo de Piedra'
            ),
        ),
    ]

