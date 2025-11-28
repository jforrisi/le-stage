#!/bin/bash
# Script para configurar la base de datos desde cero en Railway
# Borra todo, crea las tablas, y crea los usuarios

set -e  # Salir si hay algún error

echo "🗑️  Limpiando base de datos existente..."

# Borrar todas las tablas (excepto las del sistema de Django)
python manage.py shell << EOF
from django.db import connection
cursor = connection.cursor()

# Obtener todas las tablas
cursor.execute("""
    SELECT tablename FROM pg_tables 
    WHERE schemaname = 'public' 
    AND tablename NOT LIKE 'pg_%'
    AND tablename != 'django_migrations'
""")
tables = cursor.fetchall()

# Borrar cada tabla
for table in tables:
    try:
        cursor.execute(f'DROP TABLE IF EXISTS {table[0]} CASCADE')
        print(f'  ✓ Eliminada: {table[0]}')
    except Exception as e:
        print(f'  ⚠ Error eliminando {table[0]}: {e}')

# También borrar la tabla de migraciones para empezar desde cero
cursor.execute('DROP TABLE IF EXISTS django_migrations CASCADE')
print('  ✓ Eliminada: django_migrations')

connection.commit()
print('✅ Base de datos limpiada')
EOF

echo ""
echo "🔄 Creando tablas desde cero..."
python manage.py migrate

echo ""
echo "📊 Cargando datos iniciales (IVA, Monedas, Documentos)..."
python cargar_datos_iniciales.py

echo ""
echo "👥 Creando usuarios..."
python crear_usuarios.py

echo ""
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Base de datos configurada correctamente"
echo "🚀 Iniciando servidor..."
exec gunicorn erp_demo.wsgi:application

