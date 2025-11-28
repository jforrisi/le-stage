#!/bin/bash
# Script para ejecutar migraciones en el orden correcto
# Esto asegura que las dependencias se creen antes de las tablas que las referencian

set -e  # Salir si hay algún error

echo "🔄 Ejecutando migraciones en orden..."

# Primero las apps base sin dependencias
python manage.py migrate contenttypes
python manage.py migrate auth
python manage.py migrate sessions
python manage.py migrate admin

# Apps de configuración base
python manage.py migrate tablas
python manage.py migrate articulos
python manage.py migrate proveedores  # IMPORTANTE: debe ejecutarse antes de compras
python manage.py migrate clientes
python manage.py migrate canal_comercial
python manage.py migrate documentos
python manage.py migrate disponibilidades
python manage.py migrate deposito
python manage.py migrate transacciones

# Apps de compras (dependen de proveedores, articulos, documentos)
python manage.py migrate compras_ingreso
python manage.py migrate compras_devoluciones

# Apps Le Stage
python manage.py migrate mineria_le_stage
python manage.py migrate industria_le_stage
python manage.py migrate gerencia_le_stage

echo "✅ Migraciones completadas"

# Recolectar archivos estáticos
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "🚀 Iniciando servidor..."
exec gunicorn erp_demo.wsgi:application

