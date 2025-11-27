# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mineria_le_stage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipoCorte',
            fields=[
                ('id_equipo', models.AutoField(db_column='id_equipo', primary_key=True, serialize=False, verbose_name='ID Equipo')),
                ('nombre_equipo', models.CharField(max_length=200, verbose_name='Nombre Equipo')),
                ('responsable', models.CharField(max_length=200, verbose_name='Responsable')),
            ],
            options={
                'verbose_name': 'Equipo Corte',
                'verbose_name_plural': 'Equipos Corte',
                'db_table': 'mineria_equipos_corte',
                'ordering': ['nombre_equipo'],
            },
        ),
    ]

