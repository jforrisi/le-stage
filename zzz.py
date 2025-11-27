from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('compras_devoluciones', '0002_rename_linea_compra_to_id_compra_linea'),
        ('disponibilidades', '0003_rename_tables'),  # Dependencia explícita
    ]

    operations = [
        # Esta migración vacía fuerza a Django a reconocer la dependencia
        # y usar el nombre correcto de la tabla
    ]