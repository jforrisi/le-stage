from django.urls import path
from . import views

app_name = 'industria_le_stage'

urlpatterns = [
    # Tipos de Pulido Piezas
    path('tipos-pulido-piezas/', views.lista_tipos_pulido_piezas, name='lista_tipos_pulido_piezas'),
    path('tipos-pulido-piezas/crear/', views.crear_tipo_pulido_piezas, name='crear_tipo_pulido_piezas'),
    path('tipos-pulido-piezas/<int:id>/editar/', views.editar_tipo_pulido_piezas, name='editar_tipo_pulido_piezas'),
    path('tipos-pulido-piezas/<int:id>/eliminar/', views.eliminar_tipo_pulido_piezas, name='eliminar_tipo_pulido_piezas'),
    
    # Piezas Corte Cantera (Industria)
    path('piezas-corte-industria/', views.lista_piezas_corte_cantera_industria, name='lista_piezas_corte_cantera_industria'),
    path('piezas-corte-industria/<int:id>/guardar/', views.guardar_datos_industria_ajax, name='guardar_datos_industria_ajax'),
    path('piezas-corte-industria/<int:id>/ver/', views.detalle_pieza_corte_cantera_industria, name='detalle_pieza_corte_cantera_industria'),
]

