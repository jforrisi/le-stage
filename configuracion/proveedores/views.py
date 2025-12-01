from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Proveedor
from .forms import ProveedorForm
from erp_demo.config import EMPRESA_NOMBRE


def lista_proveedores(request):
    """Vista para listar todos los proveedores"""
    proveedores = Proveedor.objects.all()
    
    # Búsqueda simple
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        proveedores = proveedores.filter(
            razon__icontains=busqueda
        ) | proveedores.filter(
            codigo__icontains=busqueda
        ) | proveedores.filter(
            email__icontains=busqueda
        ) | proveedores.filter(
            rut__icontains=busqueda
        )
    
    context = {
        'proveedores': proveedores,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'proveedores/lista_proveedores.html', context)


def crear_proveedor(request):
    """Vista para crear un nuevo proveedor"""
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor creado exitosamente.')
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Proveedor',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'proveedores/form_proveedor.html', context)


def editar_proveedor(request, pk):
    """Vista para editar un proveedor existente"""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado exitosamente.')
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    
    context = {
        'form': form,
        'proveedor': proveedor,
        'titulo': 'Editar Proveedor',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'proveedores/form_proveedor.html', context)


def eliminar_proveedor(request, pk):
    """Vista para eliminar un proveedor"""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    if request.method == 'POST':
        proveedor.delete()
        messages.success(request, 'Proveedor eliminado exitosamente.')
        return redirect('lista_proveedores')
    
    context = {
        'proveedor': proveedor,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'proveedores/eliminar_proveedor.html', context)


def detalle_proveedor(request, pk):
    """Vista para ver el detalle de un proveedor"""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    
    context = {
        'proveedor': proveedor,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'proveedores/detalle_proveedor.html', context)
