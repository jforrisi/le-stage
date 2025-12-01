"""
URL configuration for erp_demo project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from erp_demo import auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Autenticación
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('', include('configuracion.clientes.urls')),
    path('', include('configuracion.clientes.canal_comercial.urls')),
    path('', include('configuracion.proveedores.urls')),
    path('', include('configuracion.articulos.urls')),
    path('', include('configuracion.disponibilidades.urls')),
    path('', include('configuracion.transacciones.urls')),
    path('', include('configuracion.tablas.urls')),
    path('', include('configuracion.deposito.urls')),
    # URLs de compras
    path('', include('compras.compras_ingreso.urls')),
    path('', include('compras.compras_devoluciones.urls')),
    # URLs de ventas
    path('', include('ventas.ventas_ingreso.urls')),
    path('', include('ventas.ventas_devoluciones.urls')),
    path('', include(('mineria_le_stage.urls', 'mineria_le_stage'), namespace='mineria_le_stage')),
    path('', include(('industria_le_stage.urls', 'industria_le_stage'), namespace='industria_le_stage')),
    path('', include(('gerencia_le_stage.urls', 'gerencia_le_stage'), namespace='gerencia_le_stage')),
]
    # URLs de ventas le stage


# Servir archivos estáticos en desarrollo
# En desarrollo, Django usa django.contrib.staticfiles automáticamente
# Esta configuración solo es necesaria si STATIC_ROOT está configurado y contiene archivos
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()

