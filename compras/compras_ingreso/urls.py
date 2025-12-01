from django.urls import path
from . import views

# Definir el namespace para esta app
app_name = 'compras_ingreso'

urlpatterns = [
    # URLs para compras
    path('compras/', views.lista_compras, name='lista_compras'),
    path('compras/nueva/', views.crear_compra, name='crear_compra'),
    path('compras/<str:transaccion>/', views.detalle_compra, name='detalle_compra'),
    path('compras/<str:transaccion>/editar/', views.editar_compra, name='editar_compra'),
    path('compras/<str:transaccion>/eliminar/', views.eliminar_compra, name='eliminar_compra'),
    # AJAX endpoints
    path('api/articulo/<int:articulo_id>/', views.get_articulo_data, name='get_articulo_data'),
    path('api/buscar-proveedores/', views.buscar_proveedores, name='buscar_proveedores'),
    path('api/buscar-articulos/', views.buscar_articulos, name='buscar_articulos'),
]

