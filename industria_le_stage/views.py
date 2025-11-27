from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import TipoPulidoPiezas
from .forms import TipoPulidoPiezasForm, PiezasCorteCanteraFormIndustria
from mineria_le_stage.models import PiezasCorteCantera
from erp_demo.config import EMPRESA_NOMBRE

# ==================== PROCESOS DE PULIDO PIEZAS DE CORTE ====================

def lista_tipos_pulido_piezas(request):
    """Lista de tipos de pulido de piezas"""
    tipos = TipoPulidoPiezas.objects.all().order_by('nombre')
    
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        tipos = tipos.filter(nombre__icontains=busqueda)
    
    paginator = Paginator(tipos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tipos': page_obj,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Tipos de Pulido Piezas',
    }
    return render(request, 'industria_le_stage/tipos_pulido_piezas/lista_tipos_pulido_piezas.html', context)


def crear_tipo_pulido_piezas(request):
    """Crear nuevo tipo de pulido de piezas"""
    if request.method == 'POST':
        form = TipoPulidoPiezasForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de pulido creado exitosamente.')
            return redirect('industria_le_stage:lista_tipos_pulido_piezas')
    else:
        form = TipoPulidoPiezasForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Tipo de Pulido Piezas',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'industria_le_stage/tipos_pulido_piezas/form_tipo_pulido_piezas.html', context)


def editar_tipo_pulido_piezas(request, id):
    """Editar tipo de pulido de piezas"""
    tipo = get_object_or_404(TipoPulidoPiezas, id=id)
    
    if request.method == 'POST':
        form = TipoPulidoPiezasForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de pulido actualizado exitosamente.')
            return redirect('industria_le_stage:lista_tipos_pulido_piezas')
    else:
        form = TipoPulidoPiezasForm(instance=tipo)
    
    context = {
        'form': form,
        'tipo': tipo,
        'titulo': f'Editar Tipo de Pulido {tipo.nombre}',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'industria_le_stage/tipos_pulido_piezas/form_tipo_pulido_piezas.html', context)


def eliminar_tipo_pulido_piezas(request, id):
    """Eliminar tipo de pulido de piezas"""
    tipo = get_object_or_404(TipoPulidoPiezas, id=id)
    
    if request.method == 'POST':
        nombre = tipo.nombre
        tipo.delete()
        messages.success(request, f'Tipo de pulido "{nombre}" eliminado exitosamente.')
        return redirect('industria_le_stage:lista_tipos_pulido_piezas')
    
    context = {
        'tipo': tipo,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'industria_le_stage/tipos_pulido_piezas/eliminar_tipo_pulido_piezas.html', context)


# ==================== PIEZAS CORTE CANTERA (INDUSTRIA) ====================

def lista_piezas_corte_cantera_industria(request):
    """Lista de piezas corte cantera para industria - Solo muestra datos básicos"""
    piezas = PiezasCorteCantera.objects.all().select_related('equipo_minero', 'equipo_corte', 'tipo_proceso').order_by('-fecha_creacion')
    
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        piezas = piezas.filter(
            nombre_piedra__icontains=busqueda
        ) | piezas.filter(
            numero__icontains=busqueda
        )
    
    paginator = Paginator(piezas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Preparar formularios para cada pieza (para desplegar inline)
    piezas_con_formularios = []
    for pieza in page_obj:
        form = PiezasCorteCanteraFormIndustria(instance=pieza)
        # Verificar si ya tiene datos de industria
        tiene_datos_industria = any([
            pieza.fecha_industria,
            pieza.kilos_recepcion_industria > 0,
            pieza.tipo_piedra,
            pieza.tipo_proceso,
            pieza.kilos_despues_tallado > 0,
            pieza.precio_por_kilo_tallado > 0,
            pieza.pulido_por_kilo > 0,
            pieza.extra_carlos,
        ])
        piezas_con_formularios.append({
            'pieza': pieza,
            'form': form,
            'tiene_datos_industria': tiene_datos_industria,
        })
    
    context = {
        'piezas_con_formularios': piezas_con_formularios,
        'piezas': page_obj,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Piezas de Corte en Cantera',
    }
    return render(request, 'industria_le_stage/piezas_corte_cantera/lista_piezas_corte_cantera_industria.html', context)


@require_http_methods(["POST"])
def guardar_datos_industria_ajax(request, id):
    """Guardar datos de industria vía AJAX"""
    pieza = get_object_or_404(PiezasCorteCantera, id=id)
    
    form = PiezasCorteCanteraFormIndustria(request.POST, instance=pieza)
    
    if form.is_valid():
        form.save()
        return JsonResponse({
            'success': True,
            'message': 'Datos de industria guardados exitosamente.',
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors,
        }, status=400)


def detalle_pieza_corte_cantera_industria(request, id):
    """Ver detalles completos de una pieza (modal o página)"""
    pieza = get_object_or_404(PiezasCorteCantera.objects.select_related('equipo_minero', 'equipo_corte', 'tipo_proceso'), id=id)
    
    context = {
        'pieza': pieza,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': f'Pieza {pieza.nombre_piedra or pieza.id}',
    }
    return render(request, 'industria_le_stage/piezas_corte_cantera/detalle_pieza_corte_cantera_industria.html', context)
