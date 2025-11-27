from django.urls import path
from . import views

urlpatterns = [
    # Tipo de Artículo
    path('tipos-articulo/', views.lista_tipos_articulo, name='lista_tipos_articulo'),
    path('tipos-articulo/nuevo/', views.crear_tipo_articulo, name='crear_tipo_articulo'),
    path('tipos-articulo/<str:codigo>/editar/', views.editar_tipo_articulo, name='editar_tipo_articulo'),
    path('tipos-articulo/<str:codigo>/eliminar/', views.eliminar_tipo_articulo, name='eliminar_tipo_articulo'),
    
    # Familia
    path('familias/', views.lista_familias, name='lista_familias'),
    path('familias/nuevo/', views.crear_familia, name='crear_familia'),
    path('familias/<int:pk>/editar/', views.editar_familia, name='editar_familia'),
    path('familias/<int:pk>/eliminar/', views.eliminar_familia, name='eliminar_familia'),
    
    # Sub Familia
    path('subfamilias/', views.lista_subfamilias, name='lista_subfamilias'),
    path('subfamilias/nuevo/', views.crear_subfamilia, name='crear_subfamilia'),
    path('subfamilias/<int:pk>/editar/', views.editar_subfamilia, name='editar_subfamilia'),
    path('subfamilias/<int:pk>/eliminar/', views.eliminar_subfamilia, name='eliminar_subfamilia'),
    
    # Artículo
    path('articulos/', views.lista_articulos, name='lista_articulos'),
    path('articulos/nuevo/', views.crear_articulo, name='crear_articulo'),
    path('articulos/<int:pk>/', views.detalle_articulo, name='detalle_articulo'),
    path('articulos/<int:pk>/editar/', views.editar_articulo, name='editar_articulo'),
    path('articulos/<int:pk>/eliminar/', views.eliminar_articulo, name='eliminar_articulo'),
    
    # IVA
    path('ivas/', views.lista_ivas, name='lista_ivas'),

    # Búsqueda de proveedores (AJAX)
    path('buscar-proveedores/', views.buscar_proveedores, name='buscar_proveedores'),
]
