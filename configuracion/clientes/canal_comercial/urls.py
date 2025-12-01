from django.urls import path
from . import views

urlpatterns = [
    path('canales-comerciales/', views.lista_canales, name='lista_canales'),
    path('canales-comerciales/nuevo/', views.crear_canal, name='crear_canal'),
    path('canales-comerciales/<int:pk>/', views.detalle_canal, name='detalle_canal'),
    path('canales-comerciales/<int:pk>/editar/', views.editar_canal, name='editar_canal'),
    path('canales-comerciales/<int:pk>/eliminar/', views.eliminar_canal, name='eliminar_canal'),
]

