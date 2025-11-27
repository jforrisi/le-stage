from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from erp_demo.decorators import acceso_por_app
from .models import Cliente, FormaPago
from .forms import ClienteForm
from erp_demo.config import EMPRESA_NOMBRE


@acceso_por_app(['configuracion', 'gerencia_le_stage'])
def home(request):
    """Vista para la página principal/home"""
    context = {
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'clientes/home.html', context)


@acceso_por_app(['configuracion', 'gerencia_le_stage'])
def lista_clientes(request):
    """Vista para listar todos los clientes"""
    clientes = Cliente.objects.all()
    
    # Búsqueda simple
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        clientes = clientes.filter(
            nombre_comercial__icontains=busqueda
        ) | clientes.filter(
            codigo__icontains=busqueda
        ) | clientes.filter(
            email__icontains=busqueda
        ) | clientes.filter(
            rut__icontains=busqueda
        ) | clientes.filter(
            razon_social__icontains=busqueda
        )
    
    context = {
        'clientes': clientes,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'clientes/lista_clientes.html', context)


@acceso_por_app(['configuracion', 'gerencia_le_stage'])
def crear_cliente(request):
    """Vista para crear un nuevo cliente"""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            # El código se genera automáticamente en el save()
            cliente.save()
            messages.success(request, 'Cliente creado exitosamente.')
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Cliente',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'clientes/form_cliente.html', context)


@acceso_por_app(['configuracion', 'gerencia_le_stage'])
def editar_cliente(request, pk):
    """Vista para editar un cliente existente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente.')
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'form': form,
        'cliente': cliente,
        'titulo': 'Editar Cliente',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'clientes/form_cliente.html', context)


@acceso_por_app(['configuracion', 'gerencia_le_stage'])
def eliminar_cliente(request, pk):
    """Vista para eliminar un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado exitosamente.')
        return redirect('lista_clientes')
    
    context = {
        'cliente': cliente,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'clientes/eliminar_cliente.html', context)


@acceso_por_app(['configuracion', 'gerencia_le_stage'])
def detalle_cliente(request, pk):
    """Vista para ver el detalle de un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    context = {
        'cliente': cliente,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'clientes/detalle_cliente.html', context)


@acceso_por_app(['configuracion', 'gerencia_le_stage'])
def lista_formas_pago(request):
    """Vista para listar todas las formas de pago"""
    formas_pago = FormaPago.objects.all()
    
    context = {
        'formas_pago': formas_pago,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Formas de Pago',
    }
    return render(request, 'clientes/lista_formas_pago.html', context)

