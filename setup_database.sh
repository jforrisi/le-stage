#!/bin/bash
# Script para configurar la base de datos en Railway
# Solo ejecuta migraciones y carga datos iniciales si no existen

set -e  # Salir si hay algún error

echo "🔄 Aplicando migraciones..."
python manage.py migrate --noinput

echo ""
echo "📊 Verificando y cargando datos iniciales (IVA, Monedas, Documentos)..."
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

