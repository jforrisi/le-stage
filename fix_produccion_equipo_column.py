"""
Script para corregir el nombre de la columna id_equipo_id a id_equipo
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_demo.settings')
django.setup()

from django.db import connection

def corregir_columna_id_equipo():
    """Renombra la columna id_equipo_id a id_equipo"""
    
    with connection.cursor() as cursor:
        print("=" * 60)
        print("CORRIGIENDO COLUMNA id_equipo_id -> id_equipo")
        print("=" * 60)
        
        # Verificar estructura actual
        cursor.execute("PRAGMA table_info(mineria_produccion_equipos)")
        columnas = cursor.fetchall()
        
        print("\nColumnas actuales:")
        for col in columnas:
            print(f"  - {col[1]} ({col[2]})")
        
        # Verificar si existe id_equipo_id
        nombres_columnas = [col[1] for col in columnas]
        
        if 'id_equipo_id' in nombres_columnas and 'id_equipo' not in nombres_columnas:
            print("\nRenombrando columna id_equipo_id a id_equipo...")
            
            # SQLite no soporta ALTER TABLE RENAME COLUMN directamente en versiones antiguas
            # Necesitamos recrear la tabla
            # Detectar el tipo de base de datos
            db_engine = connection.vendor
            if db_engine == 'postgresql':
                cursor.execute("""
                    CREATE TABLE mineria_produccion_equipos_new (
                        id BIGSERIAL PRIMARY KEY,
                        mes_año DATE NOT NULL,
                        id_equipo INTEGER NOT NULL,
                        piedra_cantera_id INTEGER NOT NULL,
                        puntos DECIMAL(15,2) NOT NULL,
                        valuacion DECIMAL(15,2) NOT NULL DEFAULT 0,
                        kilos DECIMAL(15,2) NOT NULL DEFAULT 0,
                        puntos_calculados DECIMAL(15,2) NOT NULL DEFAULT 0,
                        FOREIGN KEY (id_equipo) REFERENCES mineria_equipos(id_equipo),
                        FOREIGN KEY (piedra_cantera_id) REFERENCES mineria_piedras_canteras(id),
                        UNIQUE(mes_año, id_equipo, piedra_cantera_id)
                    )
                """)
            else:
                # SQLite
                cursor.execute("""
                    CREATE TABLE mineria_produccion_equipos_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mes_año DATE NOT NULL,
                        id_equipo INTEGER NOT NULL,
                        piedra_cantera_id INTEGER NOT NULL,
                        puntos DECIMAL(15,2) NOT NULL,
                        valuacion DECIMAL(15,2) NOT NULL DEFAULT 0,
                        kilos DECIMAL(15,2) NOT NULL DEFAULT 0,
                        puntos_calculados DECIMAL(15,2) NOT NULL DEFAULT 0,
                        FOREIGN KEY (id_equipo) REFERENCES mineria_equipos(id_equipo),
                        FOREIGN KEY (piedra_cantera_id) REFERENCES mineria_piedras_canteras(id),
                        UNIQUE(mes_año, id_equipo, piedra_cantera_id)
                    )
                """)
            
            # Copiar datos
            cursor.execute("""
                INSERT INTO mineria_produccion_equipos_new 
                (id, mes_año, id_equipo, piedra_cantera_id, puntos, valuacion, kilos, puntos_calculados)
                SELECT id, mes_año, id_equipo_id, piedra_cantera_id, puntos, valuacion, kilos, puntos_calculados
                FROM mineria_produccion_equipos
            """)
            
            # Eliminar tabla vieja
            cursor.execute("DROP TABLE mineria_produccion_equipos")
            
            # Renombrar nueva tabla
            cursor.execute("ALTER TABLE mineria_produccion_equipos_new RENAME TO mineria_produccion_equipos")
            
            # Recrear índice único
            cursor.execute("""
                CREATE UNIQUE INDEX mineria_produccion_equipos_mes_equipo_piedra_uniq 
                ON mineria_produccion_equipos(mes_año, id_equipo, piedra_cantera_id)
            """)
            
            print("Columna renombrada exitosamente.")
        elif 'id_equipo' in nombres_columnas:
            print("\nLa columna ya se llama 'id_equipo'. No se necesita corrección.")
        else:
            print("\nERROR: No se encontró la columna id_equipo_id ni id_equipo.")
            return
        
        # Verificar estructura final
        print("\nVerificando estructura final...")
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

if __name__ == '__main__':
    try:
        corregir_columna_id_equipo()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()



