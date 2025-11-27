# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transacciones', '0001_initial'),
        ('documentos', '0002_auto_20251119_1451'),
    ]

    operations = [
        # Eliminar tabla antigua de relación
        migrations.RunSQL(
            "DROP TABLE IF EXISTS transacciones_transacciondocumento;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Eliminar tabla antigua de transacciones
        migrations.RunSQL(
            "DROP TABLE IF EXISTS transacciones_transaccion;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Crear nueva tabla con estructura correcta
        migrations.RunSQL(
            """
            CREATE TABLE config_transaccion (
                transaccion VARCHAR(10) NOT NULL PRIMARY KEY,
                documento_id VARCHAR(20),
                fecha DATETIME NOT NULL,
                usuario INTEGER,
                FOREIGN KEY (documento_id) REFERENCES documentos_documento(codigo)
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS config_transaccion;",
        ),
    ]
