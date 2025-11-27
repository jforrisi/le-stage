from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Disponibilidad
from .forms import DisponibilidadForm
from erp_demo.config import EMPRESA_NOMBRE


def lista_disponibilidades(request):
    """Vista para listar todas las disponibilidades"""
    disponibilidades = Disponibilidad.objects.all()
    
    busqueda = request.GET.get('busqueda', '')
    tipo_filtro = request.GET.get('tipo', '')
    
    if busqueda:
        disponibilidades = disponibilidades.filter(
            codigo__icontains=busqueda
        ) | disponibilidades.filter(
            nombre_institucion__icontains=busqueda
        ) | disponibilidades.filter(
            alias__icontains=busqueda
        )
    
    if tipo_filtro:
        disponibilidades = disponibilidades.filter(tipo=tipo_filtro)
    
    context = {
        'disponibilidades': disponibilidades,
        'busqueda': busqueda,
        'tipo_filtro': tipo_filtro,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'disponibilidades/lista_disponibilidades.html', context)


def crear_disponibilidad(request):
    """Vista para crear una nueva disponibilidad"""
    if request.method == 'POST':
        form = DisponibilidadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Disponibilidad creada exitosamente.')
            return redirect('lista_disponibilidades')
    else:
        form = DisponibilidadForm()
    
    context = {
        'form': form,
        'titulo': 'Nueva Disponibilidad',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'disponibilidades/form_disponibilidad.html', context)


def editar_disponibilidad(request, pk):
    """Vista para editar una disponibilidad existente"""
    disponibilidad = get_object_or_404(Disponibilidad, pk=pk)
    
    if request.method == 'POST':
        form = DisponibilidadForm(request.POST, instance=disponibilidad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Disponibilidad actualizada exitosamente.')
            return redirect('lista_disponibilidades')
    else:
        form = DisponibilidadForm(instance=disponibilidad)
    
    context = {
        'form': form,
        'disponibilidad': disponibilidad,
        'titulo': 'Editar Disponibilidad',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'disponibilidades/form_disponibilidad.html', context)


def detalle_disponibilidad(request, pk):
    """Vista para ver el detalle de una disponibilidad"""
    disponibilidad = get_object_or_404(Disponibilidad, pk=pk)
    
    context = {
        'disponibilidad': disponibilidad,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'disponibilidades/detalle_disponibilidad.html', context)


def eliminar_disponibilidad(request, pk):
    """Vista para eliminar una disponibilidad"""
    disponibilidad = get_object_or_404(Disponibilidad, pk=pk)
    
    if request.method == 'POST':
        disponibilidad.delete()
        messages.success(request, 'Disponibilidad eliminada exitosamente.')
        return redirect('lista_disponibilidades')
    
    context = {
        'disponibilidad': disponibilidad,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'disponibilidades/eliminar_disponibilidad.html', context)
