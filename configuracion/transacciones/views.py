from django.shortcuts import render
from .models import Transaccion
from erp_demo.config import EMPRESA_NOMBRE


def lista_transacciones(request):
    """Vista para listar todas las transacciones"""
    transacciones = Transaccion.objects.all()
    
    context = {
        'transacciones': transacciones,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Lista de Transacciones',
    }
    return render(request, 'transacciones/lista_transacciones.html', context)


