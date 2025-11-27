# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('articulos', '0011_rename_tables'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipo',
            fields=[
                ('id_equipo', models.AutoField(db_column='id_equipo', primary_key=True, serialize=False, verbose_name='ID Equipo')),
                ('nombre_equipo', models.CharField(max_length=200, verbose_name='Nombre Equipo')),
                ('responsable', models.CharField(max_length=200, verbose_name='Responsable')),
            ],
            options={
                'verbose_name': 'Equipo',
                'verbose_name_plural': 'Equipos',
                'db_table': 'mineria_equipos',
                'ordering': ['nombre_equipo'],
            },
        ),
        migrations.CreateModel(
            name='PiedrasCanteras',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('kpi', models.CharField(choices=[('Kg', 'Kilogramos'), ('Valuación', 'Valuación')], help_text='Indica si el puntaje se calcula por kilos o por valuación', max_length=20, verbose_name='KPI')),
                ('puntos', models.DecimalField(decimal_places=2, help_text='Puntos por defecto (sugerencia para equipos)', max_digits=15, verbose_name='Puntos')),
                ('familia_producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='piedras_canteras', to='articulos.familia', verbose_name='Familia de Producto')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='piedras_canteras', to='articulos.articulo', verbose_name='Producto (Piedra)')),
            ],
            options={
                'verbose_name': 'Piedra/Cantera',
                'verbose_name_plural': 'Piedras/Canteras',
                'db_table': 'mineria_piedras_canteras',
                'ordering': ['familia_producto', 'producto'],
                'unique_together': {('familia_producto', 'producto')},
            },
        ),
        migrations.CreateModel(
            name='PuntosPiedrasEquipo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('mes_año', models.DateField(help_text='Primer día del mes (ej: 2025-11-01 para noviembre 2025)', verbose_name='Mes/Año')),
                ('puntos', models.DecimalField(decimal_places=2, help_text='Puntos para este equipo, piedra y mes (editable)', max_digits=15, verbose_name='Puntos')),
                ('id_equipo', models.ForeignKey(db_column='id_equipo', on_delete=django.db.models.deletion.PROTECT, related_name='puntos_piedras', to='mineria_le_stage.equipo', verbose_name='Equipo')),
                ('piedra_cantera', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='puntos_equipos', to='mineria_le_stage.piedrascanteras', verbose_name='Piedra/Cantera')),
            ],
            options={
                'verbose_name': 'Puntos Piedra Equipo',
                'verbose_name_plural': 'Puntos Piedras Equipos',
                'db_table': 'mineria_puntos_piedras_equipo',
                'ordering': ['id_equipo', 'piedra_cantera', '-mes_año'],
                'unique_together': {('id_equipo', 'piedra_cantera', 'mes_año')},
            },
        ),
        migrations.CreateModel(
            name='Costos',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(help_text='Primer día del mes (ej: 2025-11-01 para noviembre 2025)', verbose_name='Fecha')),
                ('rubro', models.CharField(choices=[('Producciones', 'Producciones'), ('Sueldos', 'Sueldos'), ('Combustible', 'Combustible'), ('Insumos', 'Insumos'), ('Apoyo', 'Apoyo'), ('Explosivos', 'Explosivos')], max_length=50, verbose_name='Rubro')),
                ('costo_dolares', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Costo en Dólares')),
                ('id_equipo', models.ForeignKey(db_column='id_equipo', on_delete=django.db.models.deletion.PROTECT, related_name='costos', to='mineria_le_stage.equipo', verbose_name='Equipo')),
            ],
            options={
                'verbose_name': 'Costo',
                'verbose_name_plural': 'Costos',
                'db_table': 'mineria_costos',
                'ordering': ['id_equipo', '-fecha', 'rubro'],
                'unique_together': {('id_equipo', 'fecha', 'rubro')},
            },
        ),
        migrations.CreateModel(
            name='ResultadosEquipo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('mes_año', models.DateField(help_text='Primer día del mes (ej: 2025-11-01 para noviembre 2025)', verbose_name='Mes/Año')),
                ('valuacion', models.DecimalField(decimal_places=2, default=0, help_text='Valuación en dinero', max_digits=15, verbose_name='Valuación')),
                ('kilos', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Kilos')),
                ('puntos_calculados', models.DecimalField(decimal_places=2, default=0, help_text='Calculado automáticamente según KPI y puntos vigentes', max_digits=15, verbose_name='Puntos Calculados')),
                ('id_equipo', models.ForeignKey(db_column='id_equipo', on_delete=django.db.models.deletion.PROTECT, related_name='resultados', to='mineria_le_stage.equipo', verbose_name='Equipo')),
                ('piedra', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='resultados_equipos', to='mineria_le_stage.piedrascanteras', verbose_name='Piedra/Cantera')),
            ],
            options={
                'verbose_name': 'Resultado Equipo',
                'verbose_name_plural': 'Resultados Equipos',
                'db_table': 'mineria_resultados_equipo',
                'ordering': ['id_equipo', '-mes_año', 'piedra'],
                'unique_together': {('id_equipo', 'piedra', 'mes_año')},
            },
        ),
    ]

