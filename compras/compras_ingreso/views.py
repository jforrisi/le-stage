from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json
from .models import ComprasCabezal, ComprasLineas
from .forms import (
    ComprasCabezalForm, ComprasLineasForm, ComprasLineasFormSet
)
from configuracion.proveedores.models import Proveedor
from configuracion.tablas.models import PlazoPago
from configuracion.transacciones.models import Transaccion
from configuracion.documentos.models import Documento
from configuracion.articulos.models import Articulo, CodigoProveedorCompra
from erp_demo.config import EMPRESA_NOMBRE


def lista_compras(request):
    """Vista para listar todas las compras con paginación"""
    compras = ComprasCabezal.objects.all().select_related(
        'id_proveedor', 'tipo_documento', 'moneda'
    ).prefetch_related('lineas').order_by('-fchhor')
    
    # Búsqueda
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        compras = compras.filter(
            transaccion__icontains=busqueda
        ) | compras.filter(
            numero_documento__icontains=busqueda
        ) | compras.filter(
            id_proveedor__razon__icontains=busqueda
        ) | compras.filter(
            id_proveedor__nombre_comercial__icontains=busqueda
        )
    
    # Paginación: 15 registros por página
    paginator = Paginator(compras, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'compras': page_obj,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Compras',
    }
    return render(request, 'compras_ingreso/lista_compras.html', context)


@transaction.atomic
def crear_compra(request):
    """Vista para crear una nueva compra con guardado transaccional"""
    if request.method == 'POST':
        form = ComprasCabezalForm(request.POST)
        # Crear instancia temporal para el formset
        temp_instance = ComprasCabezal()
        formset = ComprasLineasFormSet(request.POST, instance=temp_instance)
        
        # Validar según tipo de compra
        tipo_compra = request.POST.get('tipo_compra', 'CONVENCIONAL')
        if tipo_compra == 'SIMPLIFICADA':
            # Para simplificada, solo validar el formulario principal (no el formset)
            if form.is_valid():
                # Guardar cabezal
                cabezal = form.save(commit=False)
                # Si no se seleccionó tipo_documento, usar 'facprov' por defecto
                if not cabezal.tipo_documento:
                    try:
                        documento = Documento.objects.get(codigo='facprov')
                        cabezal.tipo_documento = documento
                    except Documento.DoesNotExist:
                        pass
                # La transacción y fecha_movimiento se generan automáticamente en el save()
                cabezal.save()
                
                # Crear registro en tabla Transaccion
                try:
                    documento = cabezal.tipo_documento
                    Transaccion.objects.create(
                        transaccion=cabezal.transaccion,
                        documento_id=documento.codigo,
                        usuario=request.user.id if request.user.is_authenticated else None,
                    )
                except Documento.DoesNotExist:
                    pass
                
                # NO actualizar totales (son manuales en simplificada)
                
                messages.success(request, f'Compra Simplificada {cabezal.transaccion} creada exitosamente.')
                return redirect('compras_ingreso:detalle_compra', transaccion=cabezal.transaccion)
            else:
                # Mostrar errores del formulario
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{form.fields[field].label if field in form.fields else field}: {error}')
                messages.error(request, 'Por favor, corrija los errores en el formulario.')
        else:
            # Para convencional, validar formulario y formset
            if form.is_valid() and formset.is_valid():
                # Guardar cabezal
                cabezal = form.save(commit=False)
                # Si no se seleccionó tipo_documento, usar 'facprov' por defecto
                if not cabezal.tipo_documento:
                    try:
                        documento = Documento.objects.get(codigo='facprov')
                        cabezal.tipo_documento = documento
                    except Documento.DoesNotExist:
                        pass
                # Si el proveedor es monotributista, forzar precio_iva_inc = 'SI'
                if cabezal.id_proveedor and cabezal.id_proveedor.monotributista == 'SI':
                    cabezal.precio_iva_inc = 'SI'
                # Si viene del campo hidden (monotributista), usar ese valor
                if 'precio_iva_inc' in request.POST and request.POST['precio_iva_inc'] == 'SI' and cabezal.id_proveedor and cabezal.id_proveedor.monotributista == 'SI':
                    cabezal.precio_iva_inc = 'SI'
                # La transacción y fecha_movimiento se generan automáticamente en el save()
                cabezal.save()
                
                # Guardar líneas - asegurar que tengan número de línea
                lineas = formset.save(commit=False)
                lineas_guardadas = 0
                for idx, linea in enumerate(lineas, start=1):
                    # Solo guardar si tiene artículo y cantidad válidos (ignorar líneas vacías)
                    if linea.id_articulo and linea.cantidad and linea.cantidad > 0:
                        linea.transaccion = cabezal
                        lineas_guardadas += 1
                        # Asignar número de línea si no tiene
                        if not linea.linea or linea.linea == 0:
                            linea.linea = lineas_guardadas
                        linea.save()
                
                # Eliminar líneas marcadas para eliminar
                for obj in formset.deleted_objects:
                    obj.delete()
                
                # Crear registro en tabla Transaccion
                try:
                    # Usar el documento del cabezal (puede ser facprov, factimp o movprov)
                    documento = cabezal.tipo_documento
                    Transaccion.objects.create(
                        transaccion=cabezal.transaccion,
                        documento_id=documento.codigo,
                        usuario=request.user.id if request.user.is_authenticated else None,
                    )
                except Documento.DoesNotExist:
                    pass
                
                # Actualizar totales desde las líneas
                cabezal.actualizar_totales()
            
                messages.success(request, f'Compra {cabezal.transaccion} creada exitosamente.')
                return redirect('compras_ingreso:detalle_compra', transaccion=cabezal.transaccion)
            else:
                # Mostrar errores específicos
                if not form.is_valid():
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f'{form.fields[field].label if field in form.fields else field}: {error}')
                if not formset.is_valid():
                    for form_error in formset.errors:
                        if form_error:
                            for field, errors in form_error.items():
                                for error in errors:
                                    messages.error(request, f'Línea - {field}: {error}')
                    if formset.non_form_errors():
                        for error in formset.non_form_errors():
                            messages.error(request, f'Líneas: {error}')
                
                messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = ComprasCabezalForm()
        # Crear instancia temporal para el formset (necesaria para inlineformset)
        temp_instance = ComprasCabezal()
        formset = ComprasLineasFormSet(instance=temp_instance)
        # Asegurar que solo haya 1 línea inicial (el formset tiene extra=1)
        # Si por alguna razón hay más, mantener solo la primera
        if len(formset.forms) > 1:
            formset.forms = formset.forms[:1]
    
    # Obtener datos para JavaScript
    proveedores_data = []
    for proveedor in Proveedor.objects.filter(activo='SI'):
        proveedores_data.append({
            'id': proveedor.id,
            'codigo': proveedor.codigo,
            'razon': proveedor.razon or '',
            'nombre_comercial': proveedor.nombre_comercial or '',
            'formadepago': proveedor.formadepago or '',
            'monotributista': proveedor.monotributista or 'NO',
        })
    
    formas_pago_data = []
    for fp in PlazoPago.objects.all():
        formas_pago_data.append({
            'codigo': fp.codigo,
            'descripcion': fp.descripcion,
            'plazo_en_dias': int(fp.plazo_en_dias) if fp.plazo_en_dias else 0,
            'fin_de_mes': bool(fp.fin_de_mes) if fp.fin_de_mes is not None else False,
        })
    
    # Obtener artículos para el select
    articulos_data = []
    for articulo in Articulo.objects.filter(ACTIVO_COMPRAS='SI').select_related('iva'):
        articulos_data.append({
            'id': articulo.id,
            'nombre': articulo.nombre or '',
            'producto_id': articulo.producto_id or '',
            'iva_valor': float(articulo.iva.valor) if articulo.iva else 0,
        })
    
    context = {
        'form': form,
        'formset': formset,
        'titulo': 'Nueva Compra',
        'empresa_nombre': EMPRESA_NOMBRE,
        'proveedores_data': json.dumps(proveedores_data),
        'formas_pago_data': json.dumps(formas_pago_data),
        'articulos_data': json.dumps(articulos_data),
    }
    return render(request, 'compras_ingreso/form_compra.html', context)


@transaction.atomic
def editar_compra(request, transaccion):
    """Vista para editar una compra existente"""
    compra = get_object_or_404(ComprasCabezal, transaccion=transaccion)
    
    if request.method == 'POST':
        form = ComprasCabezalForm(request.POST, instance=compra)
        formset = ComprasLineasFormSet(request.POST, instance=compra)
        
        if form.is_valid() and formset.is_valid():
            # Guardar cabezal
            cabezal = form.save(commit=False)
            # Si el proveedor es monotributista, forzar precio_iva_inc = 'SI'
            if cabezal.id_proveedor and cabezal.id_proveedor.monotributista == 'SI':
                cabezal.precio_iva_inc = 'SI'
            # Si viene del campo hidden (monotributista), usar ese valor
            if 'precio_iva_inc' in request.POST and request.POST['precio_iva_inc'] == 'SI' and cabezal.id_proveedor and cabezal.id_proveedor.monotributista == 'SI':
                cabezal.precio_iva_inc = 'SI'
            cabezal.save()
            
            # Guardar líneas
            lineas = formset.save(commit=False)
            for linea in lineas:
                linea.transaccion = cabezal
                linea.save()
            
            # Eliminar líneas marcadas para eliminar
            for obj in formset.deleted_objects:
                obj.delete()
            
            # Actualizar totales
            cabezal.actualizar_totales()
            
            messages.success(request, f'Compra {cabezal.transaccion} actualizada exitosamente.')
            return redirect('compras_ingreso:detalle_compra', transaccion=cabezal.transaccion)
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = ComprasCabezalForm(instance=compra)
        formset = ComprasLineasFormSet(instance=compra)
    
    # Obtener datos para JavaScript
    proveedores_data = []
    for proveedor in Proveedor.objects.filter(activo='SI'):
        proveedores_data.append({
            'id': proveedor.id,
            'codigo': proveedor.codigo,
            'razon': proveedor.razon or '',
            'nombre_comercial': proveedor.nombre_comercial or '',
            'formadepago': proveedor.formadepago or '',
            'monotributista': proveedor.monotributista or 'NO',
        })
    
    formas_pago_data = []
    for fp in PlazoPago.objects.all():
        formas_pago_data.append({
            'codigo': fp.codigo,
            'descripcion': fp.descripcion,
            'plazo_en_dias': int(fp.plazo_en_dias) if fp.plazo_en_dias else 0,
            'fin_de_mes': bool(fp.fin_de_mes) if fp.fin_de_mes is not None else False,
        })
    
    # Obtener artículos para el select
    articulos_data = []
    for articulo in Articulo.objects.filter(ACTIVO_COMPRAS='SI').select_related('iva'):
        articulos_data.append({
            'id': articulo.id,
            'nombre': articulo.nombre or '',
            'producto_id': articulo.producto_id or '',
            'iva_valor': float(articulo.iva.valor) if articulo.iva else 0,
        })
    
    context = {
        'form': form,
        'formset': formset,
        'compra': compra,
        'titulo': f'Editar Compra {compra.transaccion}',
        'empresa_nombre': EMPRESA_NOMBRE,
        'proveedores_data': json.dumps(proveedores_data),
        'formas_pago_data': json.dumps(formas_pago_data),
        'articulos_data': json.dumps(articulos_data),
    }
    return render(request, 'compras_ingreso/form_compra.html', context)


def detalle_compra(request, transaccion):
    """Vista para ver el detalle de una compra"""
    compra = get_object_or_404(ComprasCabezal, transaccion=transaccion)
    lineas = compra.lineas.all().select_related('id_articulo', 'id_articulo__iva').order_by('linea')
    
    context = {
        'compra': compra,
        'lineas': lineas,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': f'Compra {compra.transaccion}',
    }
    return render(request, 'compras_ingreso/detalle_compra.html', context)


@transaction.atomic
def eliminar_compra(request, transaccion):
    """Vista para eliminar una compra"""
    compra = get_object_or_404(ComprasCabezal, transaccion=transaccion)
    
    if request.method == 'POST':
        # Eliminar transacción asociada si existe
        try:
            transaccion_obj = Transaccion.objects.get(transaccion=transaccion)
            transaccion_obj.delete()
        except Transaccion.DoesNotExist:
            pass
        
        # Eliminar compra (las líneas se eliminan en cascada)
        compra.delete()
        messages.success(request, f'Compra {transaccion} eliminada exitosamente.')
        return redirect('compras_ingreso:lista_compras')
    
    context = {
        'compra': compra,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'compras_ingreso/eliminar_compra.html', context)


def get_articulo_data(request, articulo_id):
    """Endpoint AJAX para obtener datos de un artículo (IVA, etc.)"""
    try:
        articulo = Articulo.objects.get(pk=articulo_id)
        data = {
            'id': articulo.id,
            'nombre': articulo.nombre or '',
            'iva_valor': float(articulo.iva.valor) if articulo.iva else 0,
            'iva_codigo': articulo.iva.codigo if articulo.iva else '',
        }
        return JsonResponse(data)
    except Articulo.DoesNotExist:
        return JsonResponse({'error': 'Artículo no encontrado'}, status=404)


@require_http_methods(["GET"])
def buscar_proveedores(request):
    """Vista AJAX para buscar proveedores por razón social o nombre comercial"""
    try:
        query = request.GET.get('q', '').strip()
        
        if not query:
            proveedores = Proveedor.objects.filter(activo='SI').order_by('razon', 'nombre_comercial')[:50]
        else:
            proveedores = Proveedor.objects.filter(
                activo='SI'
            ).filter(
                razon__icontains=query
            ) | Proveedor.objects.filter(
                activo='SI'
            ).filter(
                nombre_comercial__icontains=query
            ) | Proveedor.objects.filter(
                activo='SI'
            ).filter(
                codigo__icontains=query
            )
            proveedores = proveedores.distinct().order_by('razon', 'nombre_comercial')[:50]
        
        resultados = []
        for proveedor in proveedores:
            # Usar razon si existe, sino nombre_comercial
            nombre_display = proveedor.razon if proveedor.razon else (proveedor.nombre_comercial if proveedor.nombre_comercial else 'Sin nombre')
            
            resultados.append({
                'id': proveedor.pk,
                'codigo': proveedor.codigo or '',
                'razon': proveedor.razon or '',
                'nombre_comercial': proveedor.nombre_comercial or '',
                'text': nombre_display,  # Solo nombre, sin ID
                'monotributista': proveedor.monotributista or 'NO',
                'formadepago': proveedor.formadepago or '',
            })
        
        return JsonResponse({'results': resultados})
    except Exception as e:
        import traceback
        print(f"Error en buscar_proveedores: {e}")
        print(traceback.format_exc())
        return JsonResponse({'results': [], 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def buscar_articulos(request):
    """Vista AJAX para buscar artículos por nombre o código de proveedor"""
    try:
        query = request.GET.get('q', '').strip()
        modo = request.GET.get('modo', 'nombre').strip()  # 'nombre' o 'codigo'
        proveedor_id = request.GET.get('proveedor_id', '').strip()
        
        if modo == 'codigo' and proveedor_id:
            # Buscar por código de proveedor
            if not query:
                # Si no hay query, retornar vacío
                return JsonResponse({'results': []})
            
            # Buscar en CodigoProveedorCompra por código_proveedor y proveedor
            codigos_proveedor = CodigoProveedorCompra.objects.filter(
                proveedor_id=proveedor_id,
                codigo_proveedor__icontains=query
            ).select_related('articulo', 'articulo__iva')
            
            resultados = []
            for codigo_prov in codigos_proveedor:
                articulo = codigo_prov.articulo
                if articulo.ACTIVO_COMPRAS == 'SI':
                    resultados.append({
                        'id': articulo.pk,
                        'nombre': articulo.nombre or '',
                        'producto_id': articulo.producto_id or '',
                        'text': f"{codigo_prov.codigo_proveedor} - {articulo.nombre or 'Sin nombre'}",
                        'codigo_proveedor': codigo_prov.codigo_proveedor,
                        'iva_valor': float(articulo.iva.valor) if articulo.iva else 0,
                    })
            
            return JsonResponse({'results': resultados})
        
        else:
            # Buscar por nombre (modo por defecto)
            if not query:
                articulos = Articulo.objects.filter(ACTIVO_COMPRAS='SI').select_related('iva').order_by('nombre')[:50]
            else:
                articulos = Articulo.objects.filter(
                    ACTIVO_COMPRAS='SI'
                ).filter(
                    nombre__icontains=query
                ) | Articulo.objects.filter(
                    ACTIVO_COMPRAS='SI'
                ).filter(
                    producto_id__icontains=query
                )
                articulos = articulos.distinct().select_related('iva').order_by('nombre')[:50]
            
            resultados = []
            for articulo in articulos:
                resultados.append({
                    'id': articulo.pk,
                    'nombre': articulo.nombre or '',
                    'producto_id': articulo.producto_id or '',
                    'text': articulo.nombre or 'Sin nombre',  # Solo nombre, sin ID
                    'iva_valor': float(articulo.iva.valor) if articulo.iva else 0,
                })
            
            return JsonResponse({'results': resultados})
            
    except Exception as e:
        import traceback
        print(f"Error en buscar_articulos: {e}")
        print(traceback.format_exc())
        return JsonResponse({'results': [], 'error': str(e)}, status=500)

