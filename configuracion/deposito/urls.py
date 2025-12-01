from django.urls import path
from . import views

urlpatterns = [
    path('depositos/', views.lista_depositos, name='lista_depositos'),
]


