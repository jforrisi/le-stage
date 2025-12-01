from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Deposito
from erp_demo.config import EMPRESA_NOMBRE


def lista_depositos(request):
    """Vista para listar todos los depósitos"""
    depositos = Deposito.objects.all()
    
    busqueda = request.GET.get('busqueda', '')
    
    if busqueda:
        depositos = depositos.filter(
            nombre__icontains=busqueda
        ) | depositos.filter(
            explicacion__icontains=busqueda
        )
    
    context = {
        'depositos': depositos,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Lista de Depósitos',
    }
    return render(request, 'deposito/lista_depositos.html', context)


