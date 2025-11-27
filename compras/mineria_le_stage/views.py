from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Equipo, PiedrasCanteras, PuntosPiedrasEquipo, Costos, ResultadosEquipo
from .forms import (
    EquipoForm, PiedrasCanterasForm, PuntosPiedrasEquipoForm,
    CostosForm, ResultadosEquipoForm
)
from configuracion.articulos.models import Familia, Articulo
from erp_demo.config import EMPRESA_NOMBRE


# ==================== EQUIPOS ====================

def lista_equipos(request):
    """Lista de equipos con paginación"""
    equipos = Equipo.objects.all().order_by('nombre_equipo')
    
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        equipos = equipos.filter(
            nombre_equipo__icontains=busqueda
        ) | equipos.filter(
            responsable__icontains=busqueda
        )
    
    paginator = Paginator(equipos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'equipos': page_obj,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Equipos',
    }
    return render(request, 'mineria_le_stage/equipos/lista_equipos.html', context)


def crear_equipo(request):
    """Crear nuevo equipo"""
    if request.method == 'POST':
        form = EquipoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo creado exitosamente.')
            return redirect('mineria_le_stage:lista_equipos')
    else:
        form = EquipoForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Equipo',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/equipos/form_equipo.html', context)


def editar_equipo(request, id_equipo):
    """Editar equipo existente"""
    equipo = get_object_or_404(Equipo, id_equipo=id_equipo)
    
    if request.method == 'POST':
        form = EquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo actualizado exitosamente.')
            return redirect('mineria_le_stage:lista_equipos')
    else:
        form = EquipoForm(instance=equipo)
    
    context = {
        'form': form,
        'equipo': equipo,
        'titulo': f'Editar Equipo {equipo.nombre_equipo}',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/equipos/form_equipo.html', context)


def detalle_equipo(request, id_equipo):
    """Detalle de equipo"""
    equipo = get_object_or_404(Equipo, id_equipo=id_equipo)
    
    context = {
        'equipo': equipo,
        'titulo': f'Equipo {equipo.nombre_equipo}',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/equipos/detalle_equipo.html', context)


def eliminar_equipo(request, id_equipo):
    """Eliminar equipo"""
    equipo = get_object_or_404(Equipo, id_equipo=id_equipo)
    
    if request.method == 'POST':
        equipo.delete()
        messages.success(request, 'Equipo eliminado exitosamente.')
        return redirect('mineria_le_stage:lista_equipos')
    
    context = {
        'equipo': equipo,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/equipos/eliminar_equipo.html', context)


# ==================== PIEDRAS/CANTERAS ====================

def lista_piedras_canteras(request):
    """Lista de piedras/canteras con paginación"""
    piedras = PiedrasCanteras.objects.all().select_related('familia_producto', 'producto').order_by('familia_producto', 'producto')
    
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        piedras = piedras.filter(
            producto__nombre__icontains=busqueda
        ) | piedras.filter(
            familia_producto__nombre__icontains=busqueda
        )
    
    paginator = Paginator(piedras, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'piedras': page_obj,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Piedras/Canteras',
    }
    return render(request, 'mineria_le_stage/piedras_canteras/lista_piedras_canteras.html', context)


def crear_piedra_cantera(request):
    """Crear nueva piedra/cantera"""
    if request.method == 'POST':
        form = PiedrasCanterasForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Piedra/Cantera creada exitosamente.')
            return redirect('mineria_le_stage:lista_piedras_canteras')
    else:
        form = PiedrasCanterasForm()
    
    context = {
        'form': form,
        'titulo': 'Nueva Piedra/Cantera',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/piedras_canteras/form_piedra_cantera.html', context)


def editar_piedra_cantera(request, id):
    """Editar piedra/cantera existente"""
    piedra = get_object_or_404(PiedrasCanteras, id=id)
    
    if request.method == 'POST':
        form = PiedrasCanterasForm(request.POST, instance=piedra)
        if form.is_valid():
            form.save()
            messages.success(request, 'Piedra/Cantera actualizada exitosamente.')
            return redirect('mineria_le_stage:lista_piedras_canteras')
    else:
        form = PiedrasCanterasForm(instance=piedra)
    
    context = {
        'form': form,
        'piedra': piedra,
        'titulo': f'Editar Piedra/Cantera {piedra.producto.nombre}',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/piedras_canteras/form_piedra_cantera.html', context)


def eliminar_piedra_cantera(request, id):
    """Eliminar piedra/cantera"""
    piedra = get_object_or_404(PiedrasCanteras, id=id)
    
    if request.method == 'POST':
        piedra.delete()
        messages.success(request, 'Piedra/Cantera eliminada exitosamente.')
        return redirect('mineria_le_stage:lista_piedras_canteras')
    
    context = {
        'piedra': piedra,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/piedras_canteras/eliminar_piedra_cantera.html', context)


# AJAX: Obtener productos por familia
@require_http_methods(["GET"])
def obtener_productos_familia(request):
    """Endpoint AJAX para obtener productos de una familia"""
    try:
        familia_id = request.GET.get('familia_id')
        if not familia_id:
            return JsonResponse({'productos': []})
        
        productos = Articulo.objects.filter(
            idsubfamilia__familia_id=familia_id
        ).order_by('nombre').values('id', 'nombre', 'producto_id')
        
        return JsonResponse({'productos': list(productos)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==================== PUNTOS PIEDRAS EQUIPO ====================

def lista_puntos_piedras_equipo(request):
    """Lista de puntos por equipo y piedra con paginación"""
    puntos = PuntosPiedrasEquipo.objects.all().select_related(
        'id_equipo', 'piedra_cantera', 'piedra_cantera__producto'
    ).order_by('-mes_año', 'id_equipo', 'piedra_cantera')
    
    # Filtros opcionales
    equipo_id = request.GET.get('equipo_id')
    if equipo_id:
        puntos = puntos.filter(id_equipo_id=equipo_id)
    
    paginator = Paginator(puntos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    equipos = Equipo.objects.all().order_by('nombre_equipo')
    
    context = {
        'puntos': page_obj,
        'equipos': equipos,
        'equipo_seleccionado': int(equipo_id) if equipo_id else None,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Puntos Piedras por Equipo',
    }
    return render(request, 'mineria_le_stage/puntos_piedras_equipo/lista_puntos_piedras_equipo.html', context)


def crear_puntos_piedras_equipo(request):
    """Crear nuevos puntos por equipo y piedra"""
    if request.method == 'POST':
        form = PuntosPiedrasEquipoForm(request.POST)
        if form.is_valid():
            # Si no se especificaron puntos, usar los de la tabla maestra
            if not form.cleaned_data.get('puntos'):
                piedra = form.cleaned_data.get('piedra_cantera')
                if piedra:
                    form.instance.puntos = piedra.puntos
            form.save()
            messages.success(request, 'Puntos creados exitosamente.')
            return redirect('mineria_le_stage:lista_puntos_piedras_equipo')
    else:
        form = PuntosPiedrasEquipoForm()
        # Si hay piedra_cantera seleccionada, sugerir puntos
        piedra_id = request.GET.get('piedra_cantera')
        if piedra_id:
            try:
                piedra = PiedrasCanteras.objects.get(id=piedra_id)
                form.fields['puntos'].initial = piedra.puntos
            except PiedrasCanteras.DoesNotExist:
                pass
    
    context = {
        'form': form,
        'titulo': 'Nuevos Puntos Piedra/Equipo',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/puntos_piedras_equipo/form_puntos_piedras_equipo.html', context)


def editar_puntos_piedras_equipo(request, id):
    """Editar puntos existentes"""
    puntos_obj = get_object_or_404(PuntosPiedrasEquipo, id=id)
    
    if request.method == 'POST':
        form = PuntosPiedrasEquipoForm(request.POST, instance=puntos_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Puntos actualizados exitosamente.')
            return redirect('mineria_le_stage:lista_puntos_piedras_equipo')
    else:
        form = PuntosPiedrasEquipoForm(instance=puntos_obj)
    
    context = {
        'form': form,
        'puntos': puntos_obj,
        'titulo': f'Editar Puntos {puntos_obj.id_equipo.nombre_equipo}',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/puntos_piedras_equipo/form_puntos_piedras_equipo.html', context)


def eliminar_puntos_piedras_equipo(request, id):
    """Eliminar puntos"""
    puntos_obj = get_object_or_404(PuntosPiedrasEquipo, id=id)
    
    if request.method == 'POST':
        puntos_obj.delete()
        messages.success(request, 'Puntos eliminados exitosamente.')
        return redirect('mineria_le_stage:lista_puntos_piedras_equipo')
    
    context = {
        'puntos': puntos_obj,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/puntos_piedras_equipo/eliminar_puntos_piedras_equipo.html', context)


# AJAX: Obtener puntos sugeridos de piedra
@require_http_methods(["GET"])
def obtener_puntos_sugeridos(request):
    """Endpoint AJAX para obtener puntos sugeridos de una piedra"""
    try:
        piedra_id = request.GET.get('piedra_id')
        if not piedra_id:
            return JsonResponse({'puntos': 0})
        
        piedra = PiedrasCanteras.objects.get(id=piedra_id)
        return JsonResponse({'puntos': float(piedra.puntos)})
    except PiedrasCanteras.DoesNotExist:
        return JsonResponse({'puntos': 0}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==================== COSTOS ====================

def lista_costos(request):
    """Lista de costos con paginación"""
    costos = Costos.objects.all().select_related('id_equipo').order_by('-fecha', 'id_equipo', 'rubro')
    
    # Filtros opcionales
    equipo_id = request.GET.get('equipo_id')
    if equipo_id:
        costos = costos.filter(id_equipo_id=equipo_id)
    
    paginator = Paginator(costos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    equipos = Equipo.objects.all().order_by('nombre_equipo')
    
    context = {
        'costos': page_obj,
        'equipos': equipos,
        'equipo_seleccionado': int(equipo_id) if equipo_id else None,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Costos',
    }
    return render(request, 'mineria_le_stage/costos/lista_costos.html', context)


def crear_costo(request):
    """Crear nuevo costo"""
    if request.method == 'POST':
        form = CostosForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Costo creado exitosamente.')
            return redirect('mineria_le_stage:lista_costos')
    else:
        form = CostosForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Costo',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/costos/form_costo.html', context)


def editar_costo(request, id):
    """Editar costo existente"""
    costo = get_object_or_404(Costos, id=id)
    
    if request.method == 'POST':
        form = CostosForm(request.POST, instance=costo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Costo actualizado exitosamente.')
            return redirect('mineria_le_stage:lista_costos')
    else:
        form = CostosForm(instance=costo)
    
    context = {
        'form': form,
        'costo': costo,
        'titulo': f'Editar Costo {costo.id_equipo.nombre_equipo}',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/costos/form_costo.html', context)


def eliminar_costo(request, id):
    """Eliminar costo"""
    costo = get_object_or_404(Costos, id=id)
    
    if request.method == 'POST':
        costo.delete()
        messages.success(request, 'Costo eliminado exitosamente.')
        return redirect('mineria_le_stage:lista_costos')
    
    context = {
        'costo': costo,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/costos/eliminar_costo.html', context)


# ==================== RESULTADOS EQUIPO ====================

def lista_resultados_equipo(request):
    """Lista de resultados con paginación"""
    resultados = ResultadosEquipo.objects.all().select_related(
        'id_equipo', 'piedra', 'piedra__producto'
    ).order_by('-mes_año', 'id_equipo', 'piedra')
    
    # Filtros opcionales
    equipo_id = request.GET.get('equipo_id')
    if equipo_id:
        resultados = resultados.filter(id_equipo_id=equipo_id)
    
    paginator = Paginator(resultados, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    equipos = Equipo.objects.all().order_by('nombre_equipo')
    
    context = {
        'resultados': page_obj,
        'equipos': equipos,
        'equipo_seleccionado': int(equipo_id) if equipo_id else None,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Resultados Equipos',
    }
    return render(request, 'mineria_le_stage/resultados_equipo/lista_resultados_equipo.html', context)


def crear_resultado_equipo(request):
    """Crear nuevo resultado"""
    if request.method == 'POST':
        form = ResultadosEquipoForm(request.POST)
        if form.is_valid():
            # Los puntos se calculan automáticamente en el save() del modelo
            form.save()
            messages.success(request, 'Resultado creado exitosamente.')
            return redirect('mineria_le_stage:lista_resultados_equipo')
    else:
        form = ResultadosEquipoForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Resultado',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/resultados_equipo/form_resultado_equipo.html', context)


def editar_resultado_equipo(request, id):
    """Editar resultado existente"""
    resultado = get_object_or_404(ResultadosEquipo, id=id)
    
    if request.method == 'POST':
        form = ResultadosEquipoForm(request.POST, instance=resultado)
        if form.is_valid():
            # Los puntos se recalculan automáticamente en el save() del modelo
            form.save()
            messages.success(request, 'Resultado actualizado exitosamente.')
            return redirect('mineria_le_stage:lista_resultados_equipo')
    else:
        form = ResultadosEquipoForm(instance=resultado)
    
    context = {
        'form': form,
        'resultado': resultado,
        'titulo': f'Editar Resultado {resultado.id_equipo.nombre_equipo}',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/resultados_equipo/form_resultado_equipo.html', context)


def eliminar_resultado_equipo(request, id):
    """Eliminar resultado"""
    resultado = get_object_or_404(ResultadosEquipo, id=id)
    
    if request.method == 'POST':
        resultado.delete()
        messages.success(request, 'Resultado eliminado exitosamente.')
        return redirect('mineria_le_stage:lista_resultados_equipo')
    
    context = {
        'resultado': resultado,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/resultados_equipo/eliminar_resultado_equipo.html', context)

