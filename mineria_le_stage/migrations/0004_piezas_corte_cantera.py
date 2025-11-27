# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mineria_le_stage', '0003_produccion_equipo'),
    ]

    operations = [
        migrations.CreateModel(
            name='PiezasCorteCantera',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_piedra', models.CharField(blank=True, max_length=200, verbose_name='Nombre Piedra')),
                ('numero', models.CharField(blank=True, max_length=100, verbose_name='Número')),
                ('fecha_extraccion', models.DateField(blank=True, null=True, verbose_name='Fecha Extracción')),
                ('kilos_en_cantera', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Kilos en Cantera')),
                ('valuacion_cantera', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Valuación Cantera')),
                ('porcentaje_valuacion_corte', models.DecimalField(decimal_places=2, default=0, help_text='Porcentaje (ej: 15.50 para 15.5%)', max_digits=5, verbose_name='% de Valuación para Equipo de Corte')),
                ('ganancia_equipo_corte', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Ganancia Equipo de Corte')),
                ('fecha_industria', models.DateField(blank=True, null=True, verbose_name='Fecha Industria')),
                ('kilos_recepcion_industria', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Kilos en Recepción Industria')),
                ('tipo_piedra', models.CharField(blank=True, max_length=200, verbose_name='Tipo de Piedra')),
                ('tipo_proceso', models.CharField(blank=True, max_length=200, verbose_name='Tipo de Proceso')),
                ('kilos_despues_tallado', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Kilos después del Tallado')),
                ('precio_por_kilo_tallado', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Precio por Kilo de Tallado')),
                ('pulido_por_kilo', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Pulido por Kilo')),
                ('extra_carlos', models.CharField(blank=True, max_length=200, verbose_name='Extra Carlos')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('fecha_modificacion', models.DateTimeField(auto_now=True, verbose_name='Fecha de Modificación')),
                ('equipo_corte', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='piezas_corte_cantera_corte', to='mineria_le_stage.equipocorte', verbose_name='Equipo de Corte')),
                ('equipo_minero', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='piezas_corte_cantera_minero', to='mineria_le_stage.equipo', verbose_name='Equipo Minero')),
            ],
            options={
                'verbose_name': 'Pieza Corte Cantera',
                'verbose_name_plural': 'Piezas Corte Cantera',
                'db_table': 'mineria_piezas_corte_cantera',
                'ordering': ['-fecha_creacion'],
            },
        ),
    ]

