from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CanalComercial
from .forms import CanalComercialForm
from erp_demo.config import EMPRESA_NOMBRE


def lista_canales(request):
    """Vista para listar todos los canales comerciales"""
    canales = CanalComercial.objects.all()
    
    # Búsqueda simple
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        canales = canales.filter(
            nombre__icontains=busqueda
        ) | canales.filter(
            descripcion__icontains=busqueda
        )
    
    context = {
        'canales': canales,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'canal_comercial/lista_canales.html', context)


def crear_canal(request):
    """Vista para crear un nuevo canal comercial"""
    if request.method == 'POST':
        form = CanalComercialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Canal comercial creado exitosamente.')
            return redirect('lista_canales')
    else:
        form = CanalComercialForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Canal Comercial',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'canal_comercial/form_canal.html', context)


def editar_canal(request, pk):
    """Vista para editar un canal comercial existente"""
    canal = get_object_or_404(CanalComercial, pk=pk)
    
    if request.method == 'POST':
        form = CanalComercialForm(request.POST, instance=canal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Canal comercial actualizado exitosamente.')
            return redirect('lista_canales')
    else:
        form = CanalComercialForm(instance=canal)
    
    context = {
        'form': form,
        'canal': canal,
        'titulo': 'Editar Canal Comercial',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'canal_comercial/form_canal.html', context)


def eliminar_canal(request, pk):
    """Vista para eliminar un canal comercial"""
    canal = get_object_or_404(CanalComercial, pk=pk)
    
    if request.method == 'POST':
        canal.delete()
        messages.success(request, 'Canal comercial eliminado exitosamente.')
        return redirect('lista_canales')
    
    context = {
        'canal': canal,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'canal_comercial/eliminar_canal.html', context)


def detalle_canal(request, pk):
    """Vista para ver el detalle de un canal comercial"""
    canal = get_object_or_404(CanalComercial, pk=pk)
    
    context = {
        'canal': canal,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'canal_comercial/detalle_canal.html', context)

