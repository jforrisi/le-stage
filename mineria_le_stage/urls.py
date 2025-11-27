from django.urls import path
from . import views

app_name = 'mineria_le_stage'

urlpatterns = [
    # Equipos
    path('equipos/', views.lista_equipos, name='lista_equipos'),
    path('equipos/crear/', views.crear_equipo, name='crear_equipo'),
    path('equipos/<int:id_equipo>/', views.detalle_equipo, name='detalle_equipo'),
    path('equipos/<int:id_equipo>/editar/', views.editar_equipo, name='editar_equipo'),
    path('equipos/<int:id_equipo>/eliminar/', views.eliminar_equipo, name='eliminar_equipo'),
    
    # Equipos Corte
    path('equipos-corte/', views.lista_equipos_corte, name='lista_equipos_corte'),
    path('equipos-corte/crear/', views.crear_equipo_corte, name='crear_equipo_corte'),
    path('equipos-corte/<int:id_equipo>/', views.detalle_equipo_corte, name='detalle_equipo_corte'),
    path('equipos-corte/<int:id_equipo>/editar/', views.editar_equipo_corte, name='editar_equipo_corte'),
    path('equipos-corte/<int:id_equipo>/eliminar/', views.eliminar_equipo_corte, name='eliminar_equipo_corte'),
    
    # Piedras/Canteras
    path('piedras-canteras/', views.lista_piedras_canteras, name='lista_piedras_canteras'),
    path('piedras-canteras/crear/', views.crear_piedra_cantera, name='crear_piedra_cantera'),
    path('piedras-canteras/<int:id>/editar/', views.editar_piedra_cantera, name='editar_piedra_cantera'),
    path('piedras-canteras/<int:id>/eliminar/', views.eliminar_piedra_cantera, name='eliminar_piedra_cantera'),
    
    # Producción Equipos
    path('produccion-equipos/', views.lista_produccion_equipos, name='lista_produccion_equipos'),
    path('produccion-equipos/crear/', views.crear_produccion_equipo, name='crear_produccion_equipo'),
    path('produccion-equipos/<int:equipo_id>/<str:mes_año>/editar/', views.editar_produccion_equipo, name='editar_produccion_equipo'),
    path('produccion-equipos/<int:equipo_id>/<str:mes_año>/eliminar/', views.eliminar_produccion_equipo_mes, name='eliminar_produccion_equipo_mes'),
    
    # Costos
    path('costos/', views.lista_costos, name='lista_costos'),
    path('costos/crear/', views.crear_costo, name='crear_costo'),
    path('costos/<int:equipo_id>/<str:fecha>/editar/', views.editar_costo, name='editar_costo'),
    path('costos/<int:equipo_id>/<str:fecha>/eliminar/', views.eliminar_costo_mes, name='eliminar_costo_mes'),
    
    # Piezas Corte Cantera
    path('piezas-corte-cantera/', views.lista_piezas_corte_cantera, name='lista_piezas_corte_cantera'),
    path('piezas-corte-cantera/crear/', views.crear_pieza_corte_cantera, name='crear_pieza_corte_cantera'),
    path('piezas-corte-cantera/<int:id>/editar/', views.editar_pieza_corte_cantera, name='editar_pieza_corte_cantera'),
    path('piezas-corte-cantera/<int:id>/eliminar/', views.eliminar_pieza_corte_cantera, name='eliminar_pieza_corte_cantera'),
    
    # AJAX endpoints
    path('api/productos-familia/', views.obtener_productos_familia, name='obtener_productos_familia'),
    path('api/puntos-sugeridos/', views.obtener_puntos_sugeridos, name='obtener_puntos_sugeridos'),
]

