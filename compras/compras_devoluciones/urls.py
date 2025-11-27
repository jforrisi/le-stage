from django.urls import path
from . import views

app_name = 'compras_devoluciones'

urlpatterns = [
    # URLs para devoluciones de compras
    path('compras_devoluciones/', views.lista_compras_devoluciones, name='lista_compras_devoluciones'),
    path('compras_devoluciones/nueva/', views.crear_compra_devolucion, name='crear_compra_devolucion'),
    path('compras_devoluciones/<str:transaccion>/', views.detalle_compra_devolucion, name='detalle_compra_devolucion'),
    path('compras_devoluciones/<str:transaccion>/editar/', views.editar_compra_devolucion, name='editar_compra_devolucion'),
    path('compras_devoluciones/<str:transaccion>/eliminar/', views.eliminar_compra_devolucion, name='eliminar_compra_devolucion'),
    # AJAX endpoints
    path('api/articulo/<int:articulo_id>/', views.get_articulo_data, name='get_articulo_data'),
    path('api/buscar-proveedores/', views.buscar_proveedores, name='buscar_proveedores'),
    path('api/buscar-articulos/', views.buscar_articulos, name='buscar_articulos'),
    path('api/compras-proveedor/', views.obtener_compras_proveedor, name='obtener_compras_proveedor'),
    path('api/lineas-compra/', views.obtener_lineas_compra, name='obtener_lineas_compra'),
]

