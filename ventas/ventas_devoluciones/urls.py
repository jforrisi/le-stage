from django.urls import path
from . import views

app_name = 'ventas_devoluciones'

urlpatterns = [
    # URLs para devoluciones de ventas
    path('ventas_devoluciones/', views.lista_ventas_devoluciones, name='lista_ventas_devoluciones'),
    path('ventas_devoluciones/nueva/', views.crear_venta_devolucion, name='crear_venta_devolucion'),
    path('ventas_devoluciones/<str:transaccion>/', views.detalle_venta_devolucion, name='detalle_venta_devolucion'),
    path('ventas_devoluciones/<str:transaccion>/editar/', views.editar_venta_devolucion, name='editar_venta_devolucion'),
    path('ventas_devoluciones/<str:transaccion>/eliminar/', views.eliminar_venta_devolucion, name='eliminar_venta_devolucion'),
    # AJAX endpoints
    path('api/articulo/<int:articulo_id>/', views.get_articulo_data, name='get_articulo_data'),
    path('api/buscar-clientes/', views.buscar_clientes, name='buscar_clientes'),
    path('api/buscar-articulos/', views.buscar_articulos, name='buscar_articulos'),
    path('api/ventas-cliente/', views.obtener_ventas_cliente, name='obtener_ventas_cliente'),
    path('api/lineas-venta/', views.obtener_lineas_venta, name='obtener_lineas_venta'),
]

