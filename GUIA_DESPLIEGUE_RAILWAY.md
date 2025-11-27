# Guía de Despliegue en Railway - Le Stage

## 📋 Requisitos Previos

1. Cuenta en Railway (https://railway.app)
2. Repositorio Git (GitHub, GitLab, o Bitbucket)
3. Tu proyecto Django funcionando localmente

## 🚀 Pasos para Desplegar

### 1. Preparar el Repositorio

```bash
# Asegúrate de tener todo en Git
git add .
git commit -m "Preparado para Railway"
git push
```

### 2. Crear Proyecto en Railway

1. Ve a https://railway.app
2. Haz clic en "New Project"
3. Selecciona "Deploy from GitHub repo" (o tu proveedor Git)
4. Conecta tu repositorio
5. **Nombra el proyecto: "le_stage"**

### 3. Agregar Base de Datos PostgreSQL

1. En el proyecto "le_stage", haz clic en "+ New"
2. Selecciona "Database" → "Add PostgreSQL"
3. Railway creará automáticamente la base de datos
4. La variable `DATABASE_URL` se configurará automáticamente

### 4. Configurar Variables de Entorno

En Railway, ve a tu servicio Django → "Variables" y agrega:

```
SECRET_KEY=genera-una-clave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=*.railway.app,tu-dominio.railway.app
```

**Para generar SECRET_KEY:**
```python
# En Python shell:
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 5. Configurar el Servicio Web

1. Railway detectará automáticamente que es Django
2. Si no, en "Settings" → "Start Command":
   ```
   gunicorn erp_demo.wsgi:application
   ```

### 6. Ejecutar Migraciones

Railway ejecutará automáticamente las migraciones gracias al `Procfile`.

Si necesitas ejecutarlas manualmente:
1. Ve a tu servicio en Railway
2. Abre la terminal
3. Ejecuta: `python manage.py migrate`

### 7. Crear Superusuario

1. Abre la terminal en Railway
2. Ejecuta: `python manage.py createsuperuser`
3. Sigue las instrucciones

### 8. Verificar Despliegue

1. Railway te dará una URL (ej: `tu-proyecto.railway.app`)
2. Visita la URL
3. Deberías ver tu aplicación funcionando

## 🔄 Actualizar la Aplicación

Cada vez que hagas cambios:

```bash
# 1. Prueba localmente
python manage.py runserver

# 2. Si funciona, sube a Git
git add .
git commit -m "Descripción de cambios"
git push

# 3. Railway detectará el push y desplegará automáticamente
# Espera 2-3 minutos y listo
```

## 📊 Acceder a la Base de Datos

### Desde Railway:
1. Ve a tu servicio PostgreSQL
2. Haz clic en "Query" para ejecutar queries SQL
3. O descarga los datos desde el panel

### Desde Django Admin:
- Accede a: `https://tu-dominio.railway.app/admin/`
- Usa tu superusuario creado

## 🔒 Seguridad

- ✅ `SECRET_KEY` está en variables de entorno (no en el código)
- ✅ `DEBUG=False` en producción
- ✅ `ALLOWED_HOSTS` configurado
- ✅ Base de datos PostgreSQL (más seguro que SQLite)

## 🐛 Troubleshooting

**Error: "No module named 'gunicorn'"**
- Verifica que `gunicorn` esté en `requirements.txt`

**Error: "Database connection failed"**
- Verifica que PostgreSQL esté agregado al proyecto
- Verifica que `DATABASE_URL` esté configurada automáticamente

**Error: "Static files not found"**
- Railway ejecuta `collectstatic` automáticamente
- Verifica que `STATIC_ROOT` esté configurado en `settings.py`

**La app no carga:**
- Revisa los logs en Railway → "Deployments" → "View Logs"
- Verifica que todas las variables de entorno estén configuradas

## 📝 Notas Importantes

- Los datos locales (SQLite) NO se suben a Railway
- La base de datos de producción es independiente
- Cada despliegue ejecuta migraciones automáticamente
- Puedes hacer rollback desde Railway si algo falla

## 🎉 ¡Listo!

Tu aplicación estará disponible en: `https://tu-proyecto.railway.app`

