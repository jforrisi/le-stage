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
    
    # Piedras/Canteras
    path('piedras-canteras/', views.lista_piedras_canteras, name='lista_piedras_canteras'),
    path('piedras-canteras/crear/', views.crear_piedra_cantera, name='crear_piedra_cantera'),
    path('piedras-canteras/<int:id>/editar/', views.editar_piedra_cantera, name='editar_piedra_cantera'),
    path('piedras-canteras/<int:id>/eliminar/', views.eliminar_piedra_cantera, name='eliminar_piedra_cantera'),
    
    # Puntos Piedras Equipo
    path('puntos-piedras-equipo/', views.lista_puntos_piedras_equipo, name='lista_puntos_piedras_equipo'),
    path('puntos-piedras-equipo/crear/', views.crear_puntos_piedras_equipo, name='crear_puntos_piedras_equipo'),
    path('puntos-piedras-equipo/<int:id>/editar/', views.editar_puntos_piedras_equipo, name='editar_puntos_piedras_equipo'),
    path('puntos-piedras-equipo/<int:id>/eliminar/', views.eliminar_puntos_piedras_equipo, name='eliminar_puntos_piedras_equipo'),
    
    # Costos
    path('costos/', views.lista_costos, name='lista_costos'),
    path('costos/crear/', views.crear_costo, name='crear_costo'),
    path('costos/<int:id>/editar/', views.editar_costo, name='editar_costo'),
    path('costos/<int:id>/eliminar/', views.eliminar_costo, name='eliminar_costo'),
    
    # Resultados Equipo
    path('resultados-equipo/', views.lista_resultados_equipo, name='lista_resultados_equipo'),
    path('resultados-equipo/crear/', views.crear_resultado_equipo, name='crear_resultado_equipo'),
    path('resultados-equipo/<int:id>/editar/', views.editar_resultado_equipo, name='editar_resultado_equipo'),
    path('resultados-equipo/<int:id>/eliminar/', views.eliminar_resultado_equipo, name='eliminar_resultado_equipo'),
    
    # AJAX endpoints
    path('api/productos-familia/', views.obtener_productos_familia, name='obtener_productos_familia'),
    path('api/puntos-sugeridos/', views.obtener_puntos_sugeridos, name='obtener_puntos_sugeridos'),
]

