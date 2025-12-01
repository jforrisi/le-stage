from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json
from .models import VentasCabezal, VentasLineas
from .forms import (
    VentasCabezalForm, VentasLineasForm, VentasLineasFormSet
)
from configuracion.clientes.models import Cliente
from configuracion.tablas.models import PlazoPago
from configuracion.transacciones.models import Transaccion
from configuracion.documentos.models import Documento
from configuracion.articulos.models import Articulo
from erp_demo.config import EMPRESA_NOMBRE


def lista_ventas(request):
    """Vista para listar todas las ventas con paginación"""
    ventas = VentasCabezal.objects.all().select_related(
        'id_cliente', 'tipo_documento', 'moneda'
    ).prefetch_related('lineas').order_by('-fchhor')
    
    # Búsqueda
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        ventas = ventas.filter(
            transaccion__icontains=busqueda
        ) | ventas.filter(
            numero_documento__icontains=busqueda
        ) | ventas.filter(
            id_cliente__razon_social__icontains=busqueda
        ) | ventas.filter(
            id_cliente__nombre_comercial__icontains=busqueda
        )
    
    # Paginación: 15 registros por página
    paginator = Paginator(ventas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'ventas': page_obj,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Ventas',
    }
    return render(request, 'ventas_ingreso/lista_ventas.html', context)


@transaction.atomic
def crear_venta(request):
    """Vista para crear una nueva venta con guardado transaccional"""
    if request.method == 'POST':
        # Crear una copia mutable del POST
        post_data = request.POST.copy()
        # En ventas, precio_iva_inc siempre es 'SI' (el campo está deshabilitado, así que no viene en POST)
        if 'precio_iva_inc' not in post_data or not post_data.get('precio_iva_inc'):
            post_data['precio_iva_inc'] = 'SI'
        
        form = VentasCabezalForm(post_data)
        # Crear instancia temporal para el formset
        temp_instance = VentasCabezal()
        formset = VentasLineasFormSet(request.POST, instance=temp_instance)
        
        # Validar según tipo de venta
        tipo_venta = request.POST.get('tipo_venta', 'CONVENCIONAL')
        if tipo_venta == 'SIMPLIFICADA':
            # Para simplificada, solo validar el formulario principal (no el formset)
            if form.is_valid():
                # Guardar cabezal
                cabezal = form.save(commit=False)
                # Si no se seleccionó tipo_documento, usar 'movcli' por defecto
                if not cabezal.tipo_documento:
                    try:
                        documento = Documento.objects.get(codigo='movcli')
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
                
                messages.success(request, f'Venta Simplificada {cabezal.transaccion} creada exitosamente.')
                return redirect('ventas_ingreso:detalle_venta', transaccion=cabezal.transaccion)
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
                # Si no se seleccionó tipo_documento, usar 'movcli' por defecto
                if not cabezal.tipo_documento:
                    try:
                        documento = Documento.objects.get(codigo='movcli')
                        cabezal.tipo_documento = documento
                    except Documento.DoesNotExist:
                        pass
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
                    # Usar el documento del cabezal (puede ser movcli, efactura o factexpo)
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
            
                messages.success(request, f'Venta {cabezal.transaccion} creada exitosamente.')
                return redirect('ventas_ingreso:detalle_venta', transaccion=cabezal.transaccion)
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
        form = VentasCabezalForm()
        # Crear instancia temporal para el formset (necesaria para inlineformset)
        temp_instance = VentasCabezal()
        formset = VentasLineasFormSet(instance=temp_instance)
        # Asegurar que solo haya 1 línea inicial (el formset tiene extra=1)
        # Si por alguna razón hay más, mantener solo la primera
        if len(formset.forms) > 1:
            formset.forms = formset.forms[:1]
    
    # Obtener datos para JavaScript
    clientes_data = []
    for cliente in Cliente.objects.filter(activo='SI'):
        clientes_data.append({
            'id': cliente.id,
            'codigo': cliente.codigo,
            'razon_social': cliente.razon_social or '',
            'nombre_comercial': cliente.nombre_comercial or '',
            'formadepago': cliente.forma_pago or '',  # Mapear forma_pago a formadepago para consistencia con compras
        })
    
    formas_pago_data = []
    for fp in PlazoPago.objects.all():
        formas_pago_data.append({
            'codigo': fp.codigo,
            'descripcion': fp.descripcion,
            'plazo_en_dias': int(fp.plazo_en_dias) if fp.plazo_en_dias else 0,
            'fin_de_mes': bool(fp.fin_de_mes) if fp.fin_de_mes is not None else False,
        })
    
    # Obtener artículos para el select (ACTIVO_COMERCIAL para ventas)
    articulos_data = []
    for articulo in Articulo.objects.filter(ACTIVO_COMERCIAL='SI').select_related('iva'):
        articulos_data.append({
            'id': articulo.id,
            'nombre': articulo.nombre or '',
            'producto_id': articulo.producto_id or '',
            'precio_venta': float(articulo.precio_venta) if articulo.precio_venta else 0,
            'iva_valor': float(articulo.iva.valor) if articulo.iva else 0,
        })
    
    context = {
        'form': form,
        'formset': formset,
        'titulo': 'Nueva Venta',
        'empresa_nombre': EMPRESA_NOMBRE,
        'clientes_data': json.dumps(clientes_data),
        'formas_pago_data': json.dumps(formas_pago_data),
        'articulos_data': json.dumps(articulos_data),
    }
    return render(request, 'ventas_ingreso/form_venta.html', context)


@transaction.atomic
def editar_venta(request, transaccion):
    """Vista para editar una venta existente"""
    venta = get_object_or_404(VentasCabezal, transaccion=transaccion)
    
    if request.method == 'POST':
        # Crear una copia mutable del POST
        post_data = request.POST.copy()
        # En ventas, precio_iva_inc siempre es 'SI' (el campo está deshabilitado, así que no viene en POST)
        if 'precio_iva_inc' not in post_data or not post_data.get('precio_iva_inc'):
            post_data['precio_iva_inc'] = 'SI'
        
        form = VentasCabezalForm(post_data, instance=venta)
        formset = VentasLineasFormSet(request.POST, instance=venta)
        
        if form.is_valid() and formset.is_valid():
            # Guardar cabezal
            cabezal = form.save(commit=False)
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
            
            messages.success(request, f'Venta {cabezal.transaccion} actualizada exitosamente.')
            return redirect('ventas_ingreso:detalle_venta', transaccion=cabezal.transaccion)
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = VentasCabezalForm(instance=venta)
        formset = VentasLineasFormSet(instance=venta)
    
    # Obtener datos para JavaScript
    clientes_data = []
    for cliente in Cliente.objects.filter(activo='SI'):
        clientes_data.append({
            'id': cliente.id,
            'codigo': cliente.codigo,
            'razon_social': cliente.razon_social or '',
            'nombre_comercial': cliente.nombre_comercial or '',
            'formadepago': cliente.forma_pago or '',  # Mapear forma_pago a formadepago para consistencia con compras
        })
    
    formas_pago_data = []
    for fp in PlazoPago.objects.all():
        formas_pago_data.append({
            'codigo': fp.codigo,
            'descripcion': fp.descripcion,
            'plazo_en_dias': int(fp.plazo_en_dias) if fp.plazo_en_dias else 0,
            'fin_de_mes': bool(fp.fin_de_mes) if fp.fin_de_mes is not None else False,
        })
    
    # Obtener artículos para el select (ACTIVO_COMERCIAL para ventas)
    articulos_data = []
    for articulo in Articulo.objects.filter(ACTIVO_COMERCIAL='SI').select_related('iva'):
        articulos_data.append({
            'id': articulo.id,
            'nombre': articulo.nombre or '',
            'producto_id': articulo.producto_id or '',
            'precio_venta': float(articulo.precio_venta) if articulo.precio_venta else 0,
            'iva_valor': float(articulo.iva.valor) if articulo.iva else 0,
        })
    
    context = {
        'form': form,
        'formset': formset,
        'venta': venta,
        'titulo': f'Editar Venta {venta.transaccion}',
        'empresa_nombre': EMPRESA_NOMBRE,
        'clientes_data': json.dumps(clientes_data),
        'formas_pago_data': json.dumps(formas_pago_data),
        'articulos_data': json.dumps(articulos_data),
    }
    return render(request, 'ventas_ingreso/form_venta.html', context)


def detalle_venta(request, transaccion):
    """Vista para ver el detalle de una venta"""
    venta = get_object_or_404(VentasCabezal, transaccion=transaccion)
    lineas = venta.lineas.all().select_related('id_articulo', 'id_articulo__iva').order_by('linea')
    
    context = {
        'venta': venta,
        'lineas': lineas,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': f'Venta {venta.transaccion}',
    }
    return render(request, 'ventas_ingreso/detalle_venta.html', context)


@transaction.atomic
def eliminar_venta(request, transaccion):
    """Vista para eliminar una venta"""
    venta = get_object_or_404(VentasCabezal, transaccion=transaccion)
    
    if request.method == 'POST':
        # Eliminar transacción asociada si existe
        try:
            transaccion_obj = Transaccion.objects.get(transaccion=transaccion)
            transaccion_obj.delete()
        except Transaccion.DoesNotExist:
            pass
        
        # Eliminar venta (las líneas se eliminan en cascada)
        venta.delete()
        messages.success(request, f'Venta {transaccion} eliminada exitosamente.')
        return redirect('ventas_ingreso:lista_ventas')
    
    context = {
        'venta': venta,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'ventas_ingreso/eliminar_venta.html', context)


def get_articulo_data(request, articulo_id):
    """Endpoint AJAX para obtener datos de un artículo (IVA, precio_venta, etc.)"""
    try:
        articulo = Articulo.objects.get(pk=articulo_id)
        data = {
            'id': articulo.id,
            'nombre': articulo.nombre or '',
            'precio_venta': float(articulo.precio_venta) if articulo.precio_venta else 0,
            'iva_valor': float(articulo.iva.valor) if articulo.iva else 0,
            'iva_codigo': articulo.iva.codigo if articulo.iva else '',
        }
        return JsonResponse(data)
    except Articulo.DoesNotExist:
        return JsonResponse({'error': 'Artículo no encontrado'}, status=404)


@require_http_methods(["GET"])
def buscar_clientes(request):
    """Vista AJAX para buscar clientes por razón social o nombre comercial"""
    try:
        query = request.GET.get('q', '').strip()
        
        if not query:
            clientes = Cliente.objects.filter(activo='SI').order_by('razon_social', 'nombre_comercial')[:50]
        else:
            clientes = Cliente.objects.filter(
                activo='SI'
            ).filter(
                razon_social__icontains=query
            ) | Cliente.objects.filter(
                activo='SI'
            ).filter(
                nombre_comercial__icontains=query
            ) | Cliente.objects.filter(
                activo='SI'
            ).filter(
                codigo__icontains=query
            )
            clientes = clientes.distinct().order_by('razon_social', 'nombre_comercial')[:50]
        
        resultados = []
        for cliente in clientes:
            # Usar razon_social si existe, sino nombre_comercial
            nombre_display = cliente.razon_social if cliente.razon_social else (cliente.nombre_comercial if cliente.nombre_comercial else 'Sin nombre')
            
            resultados.append({
                'id': cliente.pk,
                'codigo': cliente.codigo or '',
                'razon_social': cliente.razon_social or '',
                'nombre_comercial': cliente.nombre_comercial or '',
                'text': nombre_display,  # Solo nombre, sin ID
                'formadepago': cliente.forma_pago or '',  # Mapear forma_pago a formadepago para consistencia con compras
            })
        
        return JsonResponse({'results': resultados})
    except Exception as e:
        import traceback
        print(f"Error en buscar_clientes: {e}")
        print(traceback.format_exc())
        return JsonResponse({'results': [], 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def buscar_articulos(request):
    """Vista AJAX para buscar artículos por nombre (para ventas)"""
    try:
        query = request.GET.get('q', '').strip()
        
        # Buscar por nombre (modo por defecto)
        if not query:
            articulos = Articulo.objects.filter(ACTIVO_COMERCIAL='SI').select_related('iva').order_by('nombre')[:50]
        else:
            articulos = Articulo.objects.filter(
                ACTIVO_COMERCIAL='SI'
            ).filter(
                nombre__icontains=query
            ) | Articulo.objects.filter(
                ACTIVO_COMERCIAL='SI'
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
                'precio_venta': float(articulo.precio_venta) if articulo.precio_venta else 0,  # Precio del maestro sin importar moneda
            })
        
        return JsonResponse({'results': resultados})
            
    except Exception as e:
        import traceback
        print(f"Error en buscar_articulos: {e}")
        print(traceback.format_exc())
        return JsonResponse({'results': [], 'error': str(e)}, status=500)

