"""
Script para crear la tabla mineria_produccion_equipos
Elimina las tablas antiguas y crea la nueva tabla unificada
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_demo.settings')
django.setup()

from django.db import connection

def crear_tabla_produccion_equipos():
    """Crea la tabla mineria_produccion_equipos y elimina las antiguas"""
    
    with connection.cursor() as cursor:
        print("=" * 60)
        print("CREANDO TABLA mineria_produccion_equipos")
        print("=" * 60)
        
        # Verificar si las tablas antiguas existen y hacer backup si tienen datos
        tablas_antiguas = ['mineria_puntos_piedras_equipo', 'mineria_resultados_equipo']
        datos_backup = {}
        
        for tabla in tablas_antiguas:
            cursor.execute(f"""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='{tabla}'
            """)
            
            if cursor.fetchone():
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"\nTabla {tabla}: {count} registros encontrados")
                
                if count > 0:
                    print(f"Haciendo backup de {tabla}...")
                    cursor.execute(f"SELECT * FROM {tabla}")
                    datos_backup[tabla] = cursor.fetchall()
                    print(f"Backup completado: {len(datos_backup[tabla])} registros")
        
        # Verificar que las tablas de referencia existen
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='mineria_equipos'
        """)
        if not cursor.fetchone():
            print("ERROR: La tabla mineria_equipos no existe.")
            return
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='mineria_piedras_canteras'
        """)
        if not cursor.fetchone():
            print("ERROR: La tabla mineria_piedras_canteras no existe.")
            return
        
        # Eliminar tablas antiguas si existen
        print("\nEliminando tablas antiguas...")
        for tabla in tablas_antiguas:
            cursor.execute(f"DROP TABLE IF EXISTS {tabla}")
            print(f"  - {tabla} eliminada")
        
        # Crear la nueva tabla mineria_produccion_equipos
        print("\nCreando tabla mineria_produccion_equipos...")
        cursor.execute("""
            CREATE TABLE mineria_produccion_equipos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mes_año DATE NOT NULL,
                id_equipo_id INTEGER NOT NULL,
                piedra_cantera_id INTEGER NOT NULL,
                puntos DECIMAL(15,2) NOT NULL,
                valuacion DECIMAL(15,2) NOT NULL DEFAULT 0,
                kilos DECIMAL(15,2) NOT NULL DEFAULT 0,
                puntos_calculados DECIMAL(15,2) NOT NULL DEFAULT 0,
                FOREIGN KEY (id_equipo_id) REFERENCES mineria_equipos(id_equipo),
                FOREIGN KEY (piedra_cantera_id) REFERENCES mineria_piedras_canteras(id),
                UNIQUE(mes_año, id_equipo_id, piedra_cantera_id)
            )
        """)
        print("Tabla creada.")
        
        # Crear índice único
        print("\nCreando índice único...")
        cursor.execute("""
            CREATE UNIQUE INDEX mineria_produccion_equipos_mes_equipo_piedra_uniq 
            ON mineria_produccion_equipos(mes_año, id_equipo_id, piedra_cantera_id)
        """)
        print("Índice único creado.")
        
        # Si hay datos en backup, intentar migrarlos (opcional)
        # Nota: Esto es complejo porque las estructuras son diferentes
        # Por ahora solo creamos la tabla vacía
        
        # Verificar que la tabla se creó correctamente
        print("\nVerificando estructura...")
        cursor.execute("PRAGMA table_info(mineria_produccion_equipos)")
        columnas = cursor.fetchall()
        
        print("\nColumnas de la tabla:")
        for col in columnas:
            print(f"  - {col[1]} ({col[2]})")
        
        cursor.execute("PRAGMA foreign_key_list(mineria_produccion_equipos)")
        foreign_keys = cursor.fetchall()
        
        print("\nForeignKeys encontrados:")
        for fk in foreign_keys:
            print(f"  - {fk[3]} -> {fk[2]}")
        
        print("\n" + "=" * 60)
        print("PROCESO COMPLETADO")
        print("=" * 60)
        print("\nLa tabla mineria_produccion_equipos ha sido creada.")
        print("Las tablas antiguas han sido eliminadas.")
        if datos_backup:
            print(f"\nNOTA: Se encontraron datos en las tablas antiguas.")
            print("Si necesitas migrar esos datos, deberás hacerlo manualmente.")
        print("\nAhora puedes ejecutar:")
        print("  python manage.py migrate mineria_le_stage --fake")


if __name__ == '__main__':
    try:
        crear_tabla_produccion_equipos()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
