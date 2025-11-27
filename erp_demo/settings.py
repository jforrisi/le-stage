"""
Django settings for erp_demo project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Lee de variable de entorno, si no existe usa una por defecto (solo para desarrollo)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-demo-key-change-in-production-12345')

# SECURITY WARNING: don't run with debug turned on in production!
# En Railway automáticamente DEBUG=False, localmente DEBUG=True
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ALLOWED_HOSTS: Lee de variable de entorno o usa valores por defecto
ALLOWED_HOSTS_ENV = os.environ.get('ALLOWED_HOSTS', '')
if ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_ENV.split(',') if host.strip()]
else:
    # Localmente solo localhost, en Railway se debe configurar
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# CSRF Trusted Origins para Railway
CSRF_TRUSTED_ORIGINS_ENV = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if CSRF_TRUSTED_ORIGINS_ENV:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_ENV.split(',') if origin.strip()]
else:
    # Localmente
    CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']


# Application definition

INSTALLED_APPS = [
    'unfold',  # Unfold Admin debe ir antes de django.contrib.admin
    'unfold.contrib.filters',  # Filtros adicionales
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps de configuración
    'configuracion.clientes',
    'configuracion.clientes.canal_comercial',
    'configuracion.proveedores',
    'configuracion.articulos',
    'configuracion.disponibilidades',
    'configuracion.documentos',
    'configuracion.transacciones',
    'configuracion.deposito',
    'configuracion.tablas',

    'compras.compras_ingreso',
    'compras.compras_devoluciones',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'erp_demo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'erp_demo.context_processors.empresa_context',
                'erp_demo.context_processors.menu_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'erp_demo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# Si está en Railway (tiene DATABASE_URL) → usa PostgreSQL
# Si está local (no tiene DATABASE_URL) → usa SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Producción: PostgreSQL en Railway
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Desarrollo local: SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es-ar'

TIME_ZONE = 'America/Argentina/Buenos_Aires'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Unfold Admin Configuration
UNFOLD = {
    "SITE_TITLE": "ERP - Sistema de Gestión",
    "SITE_HEADER": "ERP - Sistema de Gestión",
    "SITE_URL": "/",
    "SITE_ICON": None,
    "SITE_LOGO": None,
    "SITE_SYMBOL": "settings",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
}
