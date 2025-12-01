from django.urls import path
from . import views

# Definir el namespace para esta app
app_name = 'ventas_ingreso'

urlpatterns = [
    # URLs para ventas
    path('ventas/', views.lista_ventas, name='lista_ventas'),
    path('ventas/nueva/', views.crear_venta, name='crear_venta'),
    path('ventas/<str:transaccion>/', views.detalle_venta, name='detalle_venta'),
    path('ventas/<str:transaccion>/editar/', views.editar_venta, name='editar_venta'),
    path('ventas/<str:transaccion>/eliminar/', views.eliminar_venta, name='eliminar_venta'),
    # AJAX endpoints
    path('api/articulo/<int:articulo_id>/', views.get_articulo_data, name='get_articulo_data'),
    path('api/buscar-clientes/', views.buscar_clientes, name='buscar_clientes'),
    path('api/buscar-articulos/', views.buscar_articulos, name='buscar_articulos'),
]

