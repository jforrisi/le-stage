from django.urls import path
from . import views

urlpatterns = [
    path('tablas/', views.lista_tablas, name='lista_tablas'),
    path('tablas/exportar/<str:tabla>/', views.exportar_tabla_excel, name='exportar_tabla_excel'),
]

