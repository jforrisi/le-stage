from django.urls import path
from . import views

app_name = 'gerencia_le_stage'

urlpatterns = [
    # Control de Producción
    path('control-produccion/piezas-corte/', views.control_produccion_piezas_corte, name='control_produccion_piezas_corte'),
    path('control-produccion/piezas-corte/<int:id>/ver/', views.detalle_pieza_corte, name='detalle_pieza_corte'),
]

