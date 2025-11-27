from django.urls import path
from . import views

urlpatterns = [
    path('disponibilidades/', views.lista_disponibilidades, name='lista_disponibilidades'),
    path('disponibilidades/nuevo/', views.crear_disponibilidad, name='crear_disponibilidad'),
    path('disponibilidades/<int:pk>/', views.detalle_disponibilidad, name='detalle_disponibilidad'),
    path('disponibilidades/<int:pk>/editar/', views.editar_disponibilidad, name='editar_disponibilidad'),
    path('disponibilidades/<int:pk>/eliminar/', views.eliminar_disponibilidad, name='eliminar_disponibilidad'),
]

