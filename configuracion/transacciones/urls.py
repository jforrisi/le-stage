from django.urls import path
from . import views

urlpatterns = [
    path('transacciones/', views.lista_transacciones, name='lista_transacciones'),
]


