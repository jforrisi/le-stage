# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mineria_le_stage', '0002_equipo_corte'),
    ]

    operations = [
        # Eliminar tablas antiguas
        migrations.RunSQL(
            "DROP TABLE IF EXISTS mineria_puntos_piedras_equipo;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS mineria_resultados_equipo;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Crear nueva tabla ProduccionEquipo
        migrations.CreateModel(
            name='ProduccionEquipo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('mes_año', models.DateField(help_text='Primer día del mes (ej: 2025-11-01 para noviembre 2025)', verbose_name='Mes/Año')),
                ('puntos', models.DecimalField(decimal_places=2, help_text='Puntos editables (por defecto de PiedrasCanteras, pero el usuario puede cambiarlos)', max_digits=15, verbose_name='Puntos')),
                ('valuacion', models.DecimalField(decimal_places=2, default=0, help_text='Valuación en dinero', max_digits=15, verbose_name='Valor Monetario')),
                ('kilos', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Kilos')),
                ('puntos_calculados', models.DecimalField(decimal_places=2, default=0, help_text='Calculado automáticamente: kilos × puntos (si KPI es Kg) o valuacion × puntos (si KPI es Valuación)', max_digits=15, verbose_name='Puntos Calculados')),
                ('id_equipo', models.ForeignKey(db_column='id_equipo', on_delete=django.db.models.deletion.PROTECT, related_name='producciones', to='mineria_le_stage.equipo', verbose_name='Equipo')),
                ('piedra_cantera', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='producciones_equipos', to='mineria_le_stage.piedrascanteras', verbose_name='Piedra/Cantera')),
            ],
            options={
                'verbose_name': 'Producción Equipo',
                'verbose_name_plural': 'Producciones Equipos',
                'db_table': 'mineria_produccion_equipos',
                'ordering': ['id_equipo', '-mes_año', 'piedra_cantera'],
                'unique_together': {('mes_año', 'id_equipo', 'piedra_cantera')},
            },
        ),
    ]

