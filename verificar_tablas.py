"""
Script para verificar qué tablas relacionadas con proveedores existen en la BD
"""
import sqlite3
import os

db_path = 'db.sqlite3'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Buscar todas las tablas relacionadas con proveedor
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%proveedor%' OR name LIKE '%config_proveedor%')")
    tablas = cursor.fetchall()
    
    print("=" * 60)
    print("TABLAS RELACIONADAS CON PROVEEDORES:")
    print("=" * 60)
    if tablas:
        for tabla in tablas:
            print(f"  ✓ {tabla[0]}")
            
            # Ver estructura de la tabla
            cursor.execute(f"PRAGMA table_info({tabla[0]})")
            columnas = cursor.fetchall()
            print(f"    Columnas: {len(columnas)}")
            for col in columnas[:5]:  # Primeras 5 columnas
                print(f"      - {col[1]} ({col[2]})")
            if len(columnas) > 5:
                print(f"      ... y {len(columnas) - 5} más")
            print()
    else:
        print("  ⚠️  No se encontraron tablas relacionadas con proveedores")
    
    # Verificar si existe la tabla correcta
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = 'config_proveedores_maestro'")
    if cursor.fetchone():
        print("✅ La tabla 'config_proveedores_maestro' EXISTE")
    else:
        print("❌ La tabla 'config_proveedores_maestro' NO EXISTE")
    
    # Verificar si existe la tabla incorrecta
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = 'proveedores_proveedor'")
    if cursor.fetchone():
        print("⚠️  La tabla 'proveedores_proveedor' EXISTE (nombre incorrecto)")
    else:
        print("✓ La tabla 'proveedores_proveedor' NO existe (correcto)")
    
    conn.close()
else:
    print(f"❌ No se encontró la base de datos en: {db_path}")

