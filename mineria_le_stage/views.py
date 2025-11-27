from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.forms import formset_factory
from django.db.models import Sum
from django.db import models
from datetime import date
from .models import (
    Equipo, EquipoCorte, PiedrasCanteras, ProduccionEquipo, Costos,
    PiezasCorteCantera
)
from .forms import (
    EquipoForm, EquipoCorteForm, PiedrasCanterasForm, 
    ProduccionEquipoCabezalForm, ProduccionEquipoLineaForm,
    CostosCabezalForm, CostosLineaForm, CostosLineaFormSet,
    PiezasCorteCanteraFormMineria
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


# ==================== EQUIPOS CORTE ====================

def lista_equipos_corte(request):
    """Lista de equipos de corte con paginación"""
    equipos = EquipoCorte.objects.all().order_by('nombre_equipo')
    
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
        'titulo': 'Equipos Corte',
    }
    return render(request, 'mineria_le_stage/equipos_corte/lista_equipos_corte.html', context)


def crear_equipo_corte(request):
    """Crear nuevo equipo de corte"""
    if request.method == 'POST':
        form = EquipoCorteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo Corte creado exitosamente.')
            return redirect('mineria_le_stage:lista_equipos_corte')
    else:
        form = EquipoCorteForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Equipo Corte',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/equipos_corte/form_equipo_corte.html', context)


def editar_equipo_corte(request, id_equipo):
    """Editar equipo de corte existente"""
    equipo = get_object_or_404(EquipoCorte, id_equipo=id_equipo)
    
    if request.method == 'POST':
        form = EquipoCorteForm(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo Corte actualizado exitosamente.')
            return redirect('mineria_le_stage:lista_equipos_corte')
    else:
        form = EquipoCorteForm(instance=equipo)
    
    context = {
        'form': form,
        'equipo': equipo,
        'titulo': f'Editar Equipo Corte {equipo.nombre_equipo}',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/equipos_corte/form_equipo_corte.html', context)


def detalle_equipo_corte(request, id_equipo):
    """Detalle de equipo de corte"""
    equipo = get_object_or_404(EquipoCorte, id_equipo=id_equipo)
    
    context = {
        'equipo': equipo,
        'titulo': f'Equipo Corte {equipo.nombre_equipo}',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/equipos_corte/detalle_equipo_corte.html', context)


def eliminar_equipo_corte(request, id_equipo):
    """Eliminar equipo de corte"""
    equipo = get_object_or_404(EquipoCorte, id_equipo=id_equipo)
    
    if request.method == 'POST':
        equipo.delete()
        messages.success(request, 'Equipo Corte eliminado exitosamente.')
        return redirect('mineria_le_stage:lista_equipos_corte')
    
    context = {
        'equipo': equipo,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/equipos_corte/eliminar_equipo_corte.html', context)


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


# ==================== PRODUCCIÓN EQUIPOS ====================

def lista_produccion_equipos(request):
    """Lista de producción agrupada por Equipo + Mes/Año"""
    # Obtener todas las producciones agrupadas por equipo y mes
    producciones_agrupadas = ProduccionEquipo.objects.values(
        'id_equipo', 'mes_año'
    ).annotate(
        total_puntos=Sum('puntos_calculados'),
        total_valuacion=Sum('valuacion'),
        total_kilos=Sum('kilos'),
    ).order_by('-mes_año', 'id_equipo')
    
    # Calcular precio promedio para cada grupo
    
    # Filtros opcionales
    equipo_id = request.GET.get('equipo_id')
    if equipo_id:
        producciones_agrupadas = producciones_agrupadas.filter(id_equipo_id=equipo_id)
    
    mes_año = request.GET.get('mes_año')
    if mes_año:
        producciones_agrupadas = producciones_agrupadas.filter(mes_año=mes_año)
    
    # Convertir a lista para poder paginar
    producciones_list = []
    for item in producciones_agrupadas:
        equipo = Equipo.objects.get(id_equipo=item['id_equipo'])
        total_valuacion = item['total_valuacion'] or 0
        total_kilos = item['total_kilos'] or 0
        precio_promedio = (total_valuacion / total_kilos) if total_kilos > 0 else 0
        
        producciones_list.append({
            'equipo': equipo,
            'mes_año': item['mes_año'],
            'total_puntos': item['total_puntos'] or 0,
            'total_valuacion': total_valuacion,
            'total_kilos': total_kilos,
            'precio_promedio': precio_promedio,
        })
    
    paginator = Paginator(producciones_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    equipos = Equipo.objects.all().order_by('nombre_equipo')
    
    context = {
        'producciones': page_obj,
        'equipos': equipos,
        'equipo_seleccionado': int(equipo_id) if equipo_id else None,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Producción Equipos',
    }
    return render(request, 'mineria_le_stage/produccion_equipos/lista_produccion_equipos.html', context)


def crear_produccion_equipo(request):
    """Crear nueva producción con formset de líneas"""
    # Obtener todas las piedras para el formset
    piedras = PiedrasCanteras.objects.all().select_related('producto', 'familia_producto').order_by('familia_producto', 'producto')
    
    # Crear formset dinámicamente según el número de piedras
    ProduccionEquipoLineaFormSet = formset_factory(
        ProduccionEquipoLineaForm,
        extra=len(piedras),  # Una forma por cada piedra
        can_delete=False,
    )
    
    if request.method == 'POST':
        cabezal_form = ProduccionEquipoCabezalForm(request.POST)
        formset = ProduccionEquipoLineaFormSet(request.POST)
        
        # Configurar el queryset de piedra_cantera en cada form del formset
        for form in formset:
            form.fields['piedra_cantera'].queryset = PiedrasCanteras.objects.all()
        
        if cabezal_form.is_valid() and formset.is_valid():
            mes_año = cabezal_form.cleaned_data['mes_año']
            # Asegurar que mes_año sea el primer día del mes
            if mes_año:
                mes_año = date(mes_año.year, mes_año.month, 1)
            id_equipo = cabezal_form.cleaned_data['id_equipo']
            
            # Verificar si ya existe producción para este equipo y mes
            produccion_existente = ProduccionEquipo.objects.filter(
                id_equipo=id_equipo,
                mes_año=mes_año
            ).first()
            
            if produccion_existente:
                messages.error(request, f'Este equipo ya tiene producción registrada para el mes {mes_año.strftime("%m/%Y")}. Por favor, edite la producción existente desde la lista.')
                # Re-renderizar el formulario con los datos ingresados
                formset = ProduccionEquipoLineaFormSet(request.POST)
                for form in formset:
                    form.fields['piedra_cantera'].queryset = PiedrasCanteras.objects.all()
            else:
                # Guardar cada línea del formset
                registros_guardados = 0
                for form_linea in formset:
                    if form_linea.cleaned_data and form_linea.cleaned_data.get('piedra_cantera'):
                        piedra_cantera = form_linea.cleaned_data['piedra_cantera']
                        puntos = form_linea.cleaned_data.get('puntos', 0) or 0
                        valuacion = form_linea.cleaned_data.get('valuacion', 0) or 0
                        kilos = form_linea.cleaned_data.get('kilos', 0) or 0
                        
                        # Solo guardar si hay datos (valuacion o kilos > 0)
                        if valuacion > 0 or kilos > 0:
                            produccion = ProduccionEquipo(
                                mes_año=mes_año,
                                id_equipo=id_equipo,
                                piedra_cantera=piedra_cantera,
                                puntos=puntos,
                                valuacion=valuacion,
                                kilos=kilos,
                            )
                            produccion.save()  # calcular_puntos se ejecuta en save()
                            registros_guardados += 1
                
                if registros_guardados > 0:
                    messages.success(request, f'Producción creada exitosamente. {registros_guardados} registro(s) guardado(s).')
                    return redirect('mineria_le_stage:lista_produccion_equipos')
                else:
                    messages.warning(request, 'No se guardaron registros. Debe ingresar al menos un valor en Valor Monetario o Kilos.')
    else:
        cabezal_form = ProduccionEquipoCabezalForm()
        # Crear formset con instancias iniciales para cada piedra
        formset_initial = []
        for piedra in piedras:
            formset_initial.append({
                'piedra_cantera': piedra.id,
                'piedra_nombre': f"{piedra.producto.nombre} ({piedra.familia_producto.nombre})",
                'kpi_display': piedra.get_kpi_display(),
                'kpi_valor': piedra.kpi,  # Valor real para JavaScript
                'puntos': piedra.puntos,
                'valuacion': 0,
                'kilos': 0,
                'puntos_calculados': 0,
            })
        
        formset = ProduccionEquipoLineaFormSet(initial=formset_initial)
        
        # Configurar el queryset de piedra_cantera en cada form del formset
        for form in formset:
            form.fields['piedra_cantera'].queryset = PiedrasCanteras.objects.all()
    
    context = {
        'cabezal_form': cabezal_form,
        'formset': formset,
        'piedras': piedras,
        'titulo': 'Nueva Producción',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/produccion_equipos/form_produccion_equipo.html', context)


def editar_produccion_equipo(request, equipo_id, mes_año):
    """Editar producción de un equipo y mes específico (muestra todas las líneas)"""
    from datetime import datetime
    
    # Convertir mes_año de string a date si es necesario
    if isinstance(mes_año, str):
        try:
            mes_año = datetime.strptime(mes_año, '%Y-%m-%d').date()
        except:
            mes_año = datetime.strptime(mes_año, '%Y-%m').date()
    
    equipo = get_object_or_404(Equipo, id_equipo=equipo_id)
    
    # Obtener todas las piedras
    piedras = PiedrasCanteras.objects.all().select_related('producto', 'familia_producto').order_by('familia_producto', 'producto')
    
    # Obtener producciones existentes para este equipo y mes
    producciones_existentes = ProduccionEquipo.objects.filter(
        id_equipo=equipo,
        mes_año=mes_año
    ).select_related('piedra_cantera', 'piedra_cantera__producto', 'piedra_cantera__familia_producto')
    
    # Crear diccionario de producciones existentes por piedra
    producciones_dict = {prod.piedra_cantera_id: prod for prod in producciones_existentes}
    
    # Crear formset dinámicamente
    ProduccionEquipoLineaFormSet = formset_factory(
        ProduccionEquipoLineaForm,
        extra=len(piedras),
        can_delete=False,
    )
    
    if request.method == 'POST':
        cabezal_form = ProduccionEquipoCabezalForm(request.POST)
        formset = ProduccionEquipoLineaFormSet(request.POST)
        
        # Configurar el queryset de piedra_cantera en cada form del formset
        for form in formset:
            form.fields['piedra_cantera'].queryset = PiedrasCanteras.objects.all()
        
        if cabezal_form.is_valid() and formset.is_valid():
            mes_año_nuevo = cabezal_form.cleaned_data['mes_año']
            # Asegurar que mes_año sea el primer día del mes
            if mes_año_nuevo:
                mes_año_nuevo = date(mes_año_nuevo.year, mes_año_nuevo.month, 1)
            id_equipo_nuevo = cabezal_form.cleaned_data['id_equipo']
            
            # Eliminar todas las producciones existentes para este equipo y mes
            ProduccionEquipo.objects.filter(id_equipo=id_equipo_nuevo, mes_año=mes_año_nuevo).delete()
            
            # Guardar cada línea del formset
            registros_guardados = 0
            for form_linea in formset:
                if form_linea.cleaned_data and form_linea.cleaned_data.get('piedra_cantera'):
                    piedra_cantera = form_linea.cleaned_data['piedra_cantera']
                    puntos = form_linea.cleaned_data.get('puntos', 0) or 0
                    valuacion = form_linea.cleaned_data.get('valuacion', 0) or 0
                    kilos = form_linea.cleaned_data.get('kilos', 0) or 0
                    
                    # Solo guardar si hay datos (valuacion o kilos > 0)
                    if valuacion > 0 or kilos > 0:
                        produccion = ProduccionEquipo(
                            mes_año=mes_año_nuevo,
                            id_equipo=id_equipo_nuevo,
                            piedra_cantera=piedra_cantera,
                            puntos=puntos,
                            valuacion=valuacion,
                            kilos=kilos,
                        )
                        produccion.save()
                        registros_guardados += 1
            
            if registros_guardados > 0:
                messages.success(request, f'Producción actualizada exitosamente. {registros_guardados} registro(s) guardado(s).')
            else:
                messages.warning(request, 'No se guardaron registros. Debe ingresar al menos un valor en Valor Monetario o Kilos.')
            
            return redirect('mineria_le_stage:lista_produccion_equipos')
    else:
        # Inicializar formulario de cabezal con valores existentes
        # Convertir mes_año a formato YYYY-MM para el input type="month"
        mes_año_str = mes_año.strftime('%Y-%m') if mes_año else None
        cabezal_form = ProduccionEquipoCabezalForm(initial={
            'id_equipo': equipo,
            'mes_año': mes_año_str,
        })
        
        # Crear formset con datos existentes o valores por defecto
        formset_initial = []
        for piedra in piedras:
            if piedra.id in producciones_dict:
                # Usar datos existentes
                prod = producciones_dict[piedra.id]
                formset_initial.append({
                    'piedra_cantera': piedra.id,
                    'piedra_nombre': f"{piedra.producto.nombre} ({piedra.familia_producto.nombre})",
                    'kpi_display': piedra.get_kpi_display(),
                    'kpi_valor': piedra.kpi,
                    'puntos': prod.puntos,
                    'valuacion': prod.valuacion,
                    'kilos': prod.kilos,
                    'puntos_calculados': prod.puntos_calculados,
                })
            else:
                # Usar valores por defecto
                formset_initial.append({
                    'piedra_cantera': piedra.id,
                    'piedra_nombre': f"{piedra.producto.nombre} ({piedra.familia_producto.nombre})",
                    'kpi_display': piedra.get_kpi_display(),
                    'kpi_valor': piedra.kpi,
                    'puntos': piedra.puntos,
                    'valuacion': 0,
                    'kilos': 0,
                    'puntos_calculados': 0,
                })
        
        formset = ProduccionEquipoLineaFormSet(initial=formset_initial)
        
        # Configurar el queryset de piedra_cantera en cada form del formset
        for form in formset:
            form.fields['piedra_cantera'].queryset = PiedrasCanteras.objects.all()
    
    context = {
        'cabezal_form': cabezal_form,
        'formset': formset,
        'piedras': piedras,
        'equipo': equipo,
        'mes_año': mes_año,
        'titulo': f'Editar Producción - {equipo.nombre_equipo} - {mes_año.strftime("%m/%Y")}',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/produccion_equipos/form_produccion_equipo.html', context)


def eliminar_produccion_equipo_mes(request, equipo_id, mes_año):
    """Eliminar todas las producciones de un equipo y mes"""
    from datetime import datetime
    
    equipo = get_object_or_404(Equipo, id_equipo=equipo_id)
    
    # Convertir mes_año de string a date si es necesario
    if isinstance(mes_año, str):
        try:
            mes_año = datetime.strptime(mes_año, '%Y-%m-%d').date()
        except:
            mes_año = datetime.strptime(mes_año, '%Y-%m').date()
    
    producciones = ProduccionEquipo.objects.filter(id_equipo=equipo, mes_año=mes_año)
    
    if request.method == 'POST':
        count = producciones.count()
        producciones.delete()
        messages.success(request, f'Se eliminaron {count} registro(s) de producción exitosamente.')
        return redirect('mineria_le_stage:lista_produccion_equipos')
    
    context = {
        'equipo': equipo,
        'mes_año': mes_año,
        'count': producciones.count(),
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/produccion_equipos/eliminar_produccion_equipo.html', context)


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
    """Lista de costos agrupada por Equipo + Mes/Año"""
    from datetime import datetime
    
    # Obtener todas las costos agrupadas por equipo y fecha
    costos_agrupados = Costos.objects.values(
        'id_equipo', 'fecha'
    ).annotate(
        total_costo=Sum('costo_dolares'),
    ).order_by('-fecha', 'id_equipo')
    
    # Filtros opcionales
    equipo_id = request.GET.get('equipo_id')
    if equipo_id:
        costos_agrupados = costos_agrupados.filter(id_equipo_id=equipo_id)
    
    fecha_filtro = request.GET.get('fecha')
    if fecha_filtro:
        # Convertir YYYY-MM a un objeto date para el filtro
        try:
            fecha_date = datetime.strptime(fecha_filtro, '%Y-%m').date()
            costos_agrupados = costos_agrupados.filter(fecha=fecha_date)
        except ValueError:
            messages.error(request, "Formato de fecha inválido. Use YYYY-MM.")
    
    # Convertir a lista para poder paginar
    costos_list = []
    for item in costos_agrupados:
        equipo = Equipo.objects.get(id_equipo=item['id_equipo'])
        costos_list.append({
            'equipo': equipo,
            'fecha': item['fecha'],
            'total_costo': item['total_costo'] or 0,
        })
    
    paginator = Paginator(costos_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    equipos = Equipo.objects.all().order_by('nombre_equipo')
    
    context = {
        'costos': page_obj,
        'equipos': equipos,
        'equipo_seleccionado': int(equipo_id) if equipo_id else None,
        'fecha_seleccionada': fecha_filtro,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Costos Equipos',
    }
    return render(request, 'mineria_le_stage/costos/lista_costos.html', context)


def crear_costo(request):
    """Crear nuevo costo con formset de líneas (una por rubro)"""
    # Obtener todos los rubros
    rubros = Costos.RUBROS_CHOICES
    
    # Crear formset dinámicamente según el número de rubros
    CostosLineaFormSet = formset_factory(
        CostosLineaForm,
        extra=len(rubros),
        can_delete=False,
    )
    
    if request.method == 'POST':
        cabezal_form = CostosCabezalForm(request.POST)
        formset = CostosLineaFormSet(request.POST)
        
        # Configurar choices de rubro_valor en cada form del formset
        for form in formset:
            form.fields['rubro_valor'].choices = rubros
        
        if cabezal_form.is_valid() and formset.is_valid():
            fecha = cabezal_form.cleaned_data['fecha']
            # Asegurar que fecha sea el primer día del mes
            if fecha:
                fecha = date(fecha.year, fecha.month, 1)
            id_equipo = cabezal_form.cleaned_data['id_equipo']
            
            # Verificar si ya existe costo para este equipo y mes
            costo_existente = Costos.objects.filter(
                id_equipo=id_equipo,
                fecha=fecha
            ).first()
            
            if costo_existente:
                messages.error(request, f'Este equipo ya tiene costos registrados para el mes {fecha.strftime("%m/%Y")}. Por favor, edite los costos existentes desde la lista.')
                # Re-renderizar el formulario con los datos ingresados
                formset = CostosLineaFormSet(request.POST)
                for form in formset:
                    form.fields['rubro_valor'].choices = rubros
            else:
                # Guardar cada línea del formset
                registros_guardados = 0
                for form_linea in formset:
                    if form_linea.cleaned_data and form_linea.cleaned_data.get('rubro_valor'):
                        rubro = form_linea.cleaned_data['rubro_valor']
                        costo_dolares = form_linea.cleaned_data.get('costo_dolares', 0) or 0
                        
                        # Solo guardar si hay costo > 0
                        if costo_dolares > 0:
                            costo = Costos(
                                fecha=fecha,
                                id_equipo=id_equipo,
                                rubro=rubro,
                                costo_dolares=costo_dolares,
                            )
                            costo.save()
                            registros_guardados += 1
                
                if registros_guardados > 0:
                    messages.success(request, f'Costos creados exitosamente. {registros_guardados} registro(s) guardado(s).')
                    return redirect('mineria_le_stage:lista_costos')
                else:
                    messages.warning(request, 'No se guardaron registros. Debe ingresar al menos un costo mayor a 0.')
    else:
        cabezal_form = CostosCabezalForm()
        # Crear formset con instancias iniciales para cada rubro
        formset_initial = []
        for rubro_valor, rubro_display in rubros:
            formset_initial.append({
                'rubro_display': rubro_display,
                'rubro_valor': rubro_valor,
                'costo_dolares': 0,
            })
        
        formset = CostosLineaFormSet(initial=formset_initial)
        
        # Configurar choices de rubro_valor en cada form del formset
        for form in formset:
            form.fields['rubro_valor'].choices = rubros
    
    context = {
        'cabezal_form': cabezal_form,
        'formset': formset,
        'rubros': rubros,
        'titulo': 'Nuevo Costo',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/costos/form_costo.html', context)


def editar_costo(request, equipo_id, fecha):
    """Editar costos de un equipo y mes específico (muestra todas las líneas)"""
    from datetime import datetime
    
    equipo = get_object_or_404(Equipo, id_equipo=equipo_id)
    
    # Convertir fecha de string a date si es necesario
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        except:
            fecha = datetime.strptime(fecha, '%Y-%m').date()
    
    # Obtener todos los rubros
    rubros = Costos.RUBROS_CHOICES
    
    # Obtener costos existentes para este equipo y fecha
    costos_existentes = Costos.objects.filter(
        id_equipo=equipo,
        fecha=fecha
    )
    
    # Crear diccionario de costos existentes por rubro
    costos_dict = {costo.rubro: costo for costo in costos_existentes}
    
    # Crear formset dinámicamente
    CostosLineaFormSet = formset_factory(
        CostosLineaForm,
        extra=len(rubros),
        can_delete=False,
    )
    
    if request.method == 'POST':
        cabezal_form = CostosCabezalForm(request.POST)
        formset = CostosLineaFormSet(request.POST)
        
        # Configurar choices de rubro_valor en cada form del formset
        for form in formset:
            form.fields['rubro_valor'].choices = rubros
        
        if cabezal_form.is_valid() and formset.is_valid():
            fecha_nueva = cabezal_form.cleaned_data['fecha']
            # Asegurar que fecha sea el primer día del mes
            if fecha_nueva:
                fecha_nueva = date(fecha_nueva.year, fecha_nueva.month, 1)
            id_equipo_nuevo = cabezal_form.cleaned_data['id_equipo']
            
            # Eliminar todas las costos existentes para este equipo y fecha
            Costos.objects.filter(id_equipo=id_equipo_nuevo, fecha=fecha_nueva).delete()
            
            # Guardar cada línea del formset
            registros_guardados = 0
            for form_linea in formset:
                if form_linea.cleaned_data and form_linea.cleaned_data.get('rubro_valor'):
                    rubro = form_linea.cleaned_data['rubro_valor']
                    costo_dolares = form_linea.cleaned_data.get('costo_dolares', 0) or 0
                    
                    # Solo guardar si hay costo > 0
                    if costo_dolares > 0:
                        costo = Costos(
                            fecha=fecha_nueva,
                            id_equipo=id_equipo_nuevo,
                            rubro=rubro,
                            costo_dolares=costo_dolares,
                        )
                        costo.save()
                        registros_guardados += 1
            
            if registros_guardados > 0:
                messages.success(request, f'Costos actualizados exitosamente. {registros_guardados} registro(s) guardado(s).')
            else:
                messages.warning(request, 'No se guardaron registros. Debe ingresar al menos un costo mayor a 0.')
            
            return redirect('mineria_le_stage:lista_costos')
    else:
        # Inicializar formulario de cabezal con valores existentes
        fecha_str = fecha.strftime('%Y-%m') if fecha else None
        cabezal_form = CostosCabezalForm(initial={
            'id_equipo': equipo,
            'fecha': fecha_str,
        })
        
        # Crear formset con datos existentes o valores por defecto
        formset_initial = []
        for rubro_valor, rubro_display in rubros:
            if rubro_valor in costos_dict:
                # Usar datos existentes
                costo_obj = costos_dict[rubro_valor]
                formset_initial.append({
                    'rubro_display': rubro_display,
                    'rubro_valor': rubro_valor,
                    'costo_dolares': costo_obj.costo_dolares,
                })
            else:
                # Usar valores por defecto
                formset_initial.append({
                    'rubro_display': rubro_display,
                    'rubro_valor': rubro_valor,
                    'costo_dolares': 0,
                })
        
        formset = CostosLineaFormSet(initial=formset_initial)
        
        # Configurar choices de rubro_valor en cada form del formset
        for form in formset:
            form.fields['rubro_valor'].choices = rubros
    
    context = {
        'cabezal_form': cabezal_form,
        'formset': formset,
        'rubros': rubros,
        'equipo': equipo,
        'fecha': fecha,
        'titulo': f'Editar Costos - {equipo.nombre_equipo} - {fecha.strftime("%m/%Y")}',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/costos/form_costo.html', context)


def eliminar_costo_mes(request, equipo_id, fecha):
    """Eliminar todos los costos de un equipo y mes"""
    from datetime import datetime
    
    equipo = get_object_or_404(Equipo, id_equipo=equipo_id)
    
    # Convertir fecha de string a date si es necesario
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        except:
            fecha = datetime.strptime(fecha, '%Y-%m').date()
    
    costos = Costos.objects.filter(id_equipo=equipo, fecha=fecha)
    
    if request.method == 'POST':
        count = costos.count()
        costos.delete()
        messages.success(request, f'Se eliminaron {count} registro(s) de costos exitosamente.')
        return redirect('mineria_le_stage:lista_costos')
    
    context = {
        'equipo': equipo,
        'fecha': fecha,
        'count': costos.count(),
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/costos/eliminar_costo.html', context)


# ==================== PIEZAS CORTE CANTERA ====================

def lista_piezas_corte_cantera(request):
    """Lista de piezas corte cantera (solo vista de minería)"""
    piezas = PiezasCorteCantera.objects.all().order_by('-fecha_creacion')
    
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
    
    context = {
        'piezas': page_obj,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Piezas de Corte en Cantera',
    }
    return render(request, 'mineria_le_stage/piezas_corte_cantera/lista_piezas_corte_cantera.html', context)


def crear_pieza_corte_cantera(request):
    """Crear nueva pieza corte cantera (solo campos de minería)"""
    if request.method == 'POST':
        form = PiezasCorteCanteraFormMineria(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pieza de corte creada exitosamente.')
            return redirect('mineria_le_stage:lista_piezas_corte_cantera')
    else:
        form = PiezasCorteCanteraFormMineria()
    
    context = {
        'form': form,
        'titulo': 'Nueva Pieza de Corte en Cantera',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/piezas_corte_cantera/form_pieza_corte_cantera.html', context)


def editar_pieza_corte_cantera(request, id):
    """Editar pieza corte cantera (solo campos de minería)"""
    pieza = get_object_or_404(PiezasCorteCantera, id=id)
    
    if request.method == 'POST':
        form = PiezasCorteCanteraFormMineria(request.POST, instance=pieza)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pieza de corte actualizada exitosamente.')
            return redirect('mineria_le_stage:lista_piezas_corte_cantera')
    else:
        form = PiezasCorteCanteraFormMineria(instance=pieza)
    
    context = {
        'form': form,
        'pieza': pieza,
        'titulo': f'Editar Pieza de Corte {pieza.nombre_piedra or pieza.id}',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/piezas_corte_cantera/form_pieza_corte_cantera.html', context)


def eliminar_pieza_corte_cantera(request, id):
    """Eliminar pieza corte cantera"""
    pieza = get_object_or_404(PiezasCorteCantera, id=id)
    
    if request.method == 'POST':
        nombre = pieza.nombre_piedra or f"Pieza {pieza.id}"
        pieza.delete()
        messages.success(request, f'Pieza de corte "{nombre}" eliminada exitosamente.')
        return redirect('mineria_le_stage:lista_piezas_corte_cantera')
    
    context = {
        'pieza': pieza,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'mineria_le_stage/piezas_corte_cantera/eliminar_pieza_corte_cantera.html', context)
