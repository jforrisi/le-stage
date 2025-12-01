from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json
from .models import VentasDevolucionesCabezal, VentasDevolucionesLineas
from .forms import (
    VentasDevolucionesCabezalForm, VentasDevolucionesLineasForm, VentasDevolucionesLineasFormSet
)
from configuracion.clientes.models import Cliente
from configuracion.transacciones.models import Transaccion
from configuracion.documentos.models import Documento
from configuracion.articulos.models import Articulo
from erp_demo.config import EMPRESA_NOMBRE


def lista_ventas_devoluciones(request):
    """Vista para listar todas las devoluciones de ventas con paginación"""
    ventas_devoluciones = VentasDevolucionesCabezal.objects.all().select_related(
        'id_cliente', 'tipo_documento'
    ).prefetch_related('lineas').order_by('-fchhor')
    
    # Búsqueda
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        ventas_devoluciones = ventas_devoluciones.filter(
            transaccion__icontains=busqueda
        ) | ventas_devoluciones.filter(
            numero_documento__icontains=busqueda
        ) | ventas_devoluciones.filter(
            id_cliente__razon_social__icontains=busqueda
        ) | ventas_devoluciones.filter(
            id_cliente__nombre_comercial__icontains=busqueda
        )
    
    # Paginación: 15 registros por página
    paginator = Paginator(ventas_devoluciones, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'devoluciones': page_obj,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Devoluciones Ventas',
    }
    return render(request, 'ventas_devoluciones/lista_ventas_devoluciones.html', context)


@transaction.atomic
def crear_venta_devolucion(request):
    """Vista para crear una nueva devolución de venta con guardado transaccional"""
    if request.method == 'POST':
        # Crear una copia mutable del POST
        post_data = request.POST.copy()
        # En devoluciones de ventas, precio_iva_inc siempre es 'SI' (el campo está deshabilitado, así que no viene en POST)
        if 'precio_iva_inc' not in post_data or not post_data.get('precio_iva_inc'):
            post_data['precio_iva_inc'] = 'SI'
        
        form = VentasDevolucionesCabezalForm(post_data)
        # Crear instancia temporal para el formset
        temp_instance = VentasDevolucionesCabezal()
        formset = VentasDevolucionesLineasFormSet(request.POST, instance=temp_instance)
        

        if form.is_valid() and formset.is_valid():
            # Guardar cabezal
            cabezal = form.save(commit=False)
            # Si no se seleccionó tipo_documento, usar 'devmovcli' por defecto
            if not cabezal.tipo_documento:
                try:
                    documento = Documento.objects.get(codigo='devmovcli')
                    cabezal.tipo_documento = documento
                except Documento.DoesNotExist:
                    pass
            # Copiar monotributista del cliente si existe
            if cabezal.id_cliente:
                try:
                    cliente = cabezal.id_cliente
                    if hasattr(cliente, 'monotributista') and cliente.monotributista:
                        cabezal.monotributista = cliente.monotributista
                    else:
                        cabezal.monotributista = 'NO'
                except:
                    cabezal.monotributista = 'NO'
            else:
                cabezal.monotributista = 'NO'
            cabezal.usuario = request.user.id if request.user.is_authenticated else None
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
                # Usar el documento del cabezal (puede ser devmovcli, tncredit, ncreexpo)
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
        
            messages.success(request, f'Devolución de Venta {cabezal.transaccion} creada exitosamente.')
            return redirect('ventas_devoluciones:detalle_venta_devolucion', transaccion=cabezal.transaccion)
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
        form = VentasDevolucionesCabezalForm()
        # Crear instancia temporal para el formset (necesaria para inlineformset)
        temp_instance = VentasDevolucionesCabezal()
        formset = VentasDevolucionesLineasFormSet(instance=temp_instance)
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
        })
    
    
    # Obtener artículos para el select - ordenar SER* primero (ACTIVO_COMERCIAL para ventas)
    articulos_data = []
    # Primero obtener artículos SER* (producto_id que empieza con SER)
    articulos_ser = Articulo.objects.filter(
        ACTIVO_COMERCIAL='SI',
        producto_id__startswith='SER'
    ).select_related('iva').order_by('producto_id')
    
    # Luego obtener el resto de artículos
    articulos_otros = Articulo.objects.filter(
        ACTIVO_COMERCIAL='SI'
    ).exclude(
        producto_id__startswith='SER'
    ).select_related('iva').order_by('nombre')
    
    # Agregar primero los SER*
    for articulo in articulos_ser:
        articulos_data.append({
            'id': articulo.id,
            'nombre': articulo.nombre or '',
            'producto_id': articulo.producto_id or '',
            'iva_valor': float(articulo.iva.valor) if articulo.iva else 0,
            'es_ser': True,  # Flag para identificar artículos SER*
        })
    
    # Luego agregar el resto
    for articulo in articulos_otros:
        articulos_data.append({
            'id': articulo.id,
            'nombre': articulo.nombre or '',
            'producto_id': articulo.producto_id or '',
            'iva_valor': float(articulo.iva.valor) if articulo.iva else 0,
            'es_ser': False,
        })
    
    context = {
        'form': form,
        'formset': formset,
        'titulo': 'Nueva Devolución de Venta',
        'empresa_nombre': EMPRESA_NOMBRE,
        'clientes_data': json.dumps(clientes_data),
        'articulos_data': json.dumps(articulos_data),
    }
    return render(request, 'ventas_devoluciones/form_venta_devolucion.html', context)


@transaction.atomic
def editar_venta_devolucion(request, transaccion):
    """Vista para editar una devolución de venta existente"""
    venta_devolucion = get_object_or_404(VentasDevolucionesCabezal, transaccion=transaccion)
    
    if request.method == 'POST':
        # Crear una copia mutable del POST
        post_data = request.POST.copy()
        # En devoluciones de ventas, precio_iva_inc siempre es 'SI' (el campo está deshabilitado, así que no viene en POST)
        if 'precio_iva_inc' not in post_data or not post_data.get('precio_iva_inc'):
            post_data['precio_iva_inc'] = 'SI'
        
        form = VentasDevolucionesCabezalForm(post_data, instance=venta_devolucion)
        formset = VentasDevolucionesLineasFormSet(request.POST, instance=venta_devolucion)
        
        if form.is_valid() and formset.is_valid():
            # Guardar cabezal
            cabezal = form.save(commit=False)
            # Copiar monotributista del cliente si existe
            if cabezal.id_cliente:
                try:
                    cliente = cabezal.id_cliente
                    if hasattr(cliente, 'monotributista') and cliente.monotributista:
                        cabezal.monotributista = cliente.monotributista
                    else:
                        cabezal.monotributista = 'NO'
                except:
                    cabezal.monotributista = 'NO'
            elif not cabezal.monotributista:
                cabezal.monotributista = 'NO'
            cabezal.save()
            
            # Guardar líneas
            lineas = formset.save(commit=False)
            lineas_guardadas = 0
            for idx, linea in enumerate(lineas, start=1):
                if linea.id_articulo and linea.cantidad and linea.cantidad > 0:
                    linea.transaccion = cabezal
                    lineas_guardadas += 1
                    if not linea.linea or linea.linea == 0:
                        linea.linea = lineas_guardadas
                    linea.save()
            
            # Eliminar líneas marcadas para eliminar
            for obj in formset.deleted_objects:
                obj.delete()
            
            # Actualizar totales
            cabezal.actualizar_totales()
            
            messages.success(request, f'Devolución de venta {cabezal.transaccion} actualizada exitosamente.')
            return redirect('ventas_devoluciones:detalle_venta_devolucion', transaccion=cabezal.transaccion)
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
        form = VentasDevolucionesCabezalForm(instance=venta_devolucion)
        formset = VentasDevolucionesLineasFormSet(instance=venta_devolucion)
    
    # Obtener datos para JavaScript
    clientes_data = []
    for cliente in Cliente.objects.filter(activo='SI'):
        clientes_data.append({
            'id': cliente.id,
            'codigo': cliente.codigo,
            'razon_social': cliente.razon_social or '',
            'nombre_comercial': cliente.nombre_comercial or '',
        })
    

    
    # Obtener artículos para el select - ordenar SER* primero (ACTIVO_COMERCIAL para ventas)
    articulos_data = []
    # Primero obtener artículos SER* (producto_id que empieza con SER)
    articulos_ser = Articulo.objects.filter(
        ACTIVO_COMERCIAL='SI',
        producto_id__startswith='SER'
    ).select_related('iva').order_by('producto_id')
    
    # Luego obtener el resto de artículos
    articulos_otros = Articulo.objects.filter(
        ACTIVO_COMERCIAL='SI'
    ).exclude(
        producto_id__startswith='SER'
    ).select_related('iva').order_by('nombre')
    
    # Agregar primero los SER*
    for articulo in articulos_ser:
        articulos_data.append({
            'id': articulo.id,
            'nombre': articulo.nombre or '',
            'producto_id': articulo.producto_id or '',
            'iva_valor': float(articulo.iva.valor) if articulo.iva else 0,
            'es_ser': True,  # Flag para identificar artículos SER*
        })
    
    # Luego agregar el resto
    for articulo in articulos_otros:
        articulos_data.append({
            'id': articulo.id,
            'nombre': articulo.nombre or '',
            'producto_id': articulo.producto_id or '',
            'iva_valor': float(articulo.iva.valor) if articulo.iva else 0,
            'es_ser': False,
        })
    
    context = {
        'form': form,
        'formset': formset,
        'venta_devolucion': venta_devolucion,
        'titulo': f'Editar Devolución de Venta {venta_devolucion.transaccion}',
        'empresa_nombre': EMPRESA_NOMBRE,
        'clientes_data': json.dumps(clientes_data),
        'articulos_data': json.dumps(articulos_data),
    }
    return render(request, 'ventas_devoluciones/form_venta_devolucion.html', context)


def detalle_venta_devolucion(request, transaccion):
    """Vista para ver el detalle de una devolución de venta"""
    venta_devolucion = get_object_or_404(VentasDevolucionesCabezal, transaccion=transaccion)
    lineas = venta_devolucion.lineas.all().select_related('id_articulo', 'id_articulo__iva').order_by('linea')
    
    context = {
        'venta_devolucion': venta_devolucion,
        'lineas': lineas,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': f'Devolución de Venta {venta_devolucion.transaccion}',
    }
    return render(request, 'ventas_devoluciones/detalle_venta_devolucion.html', context)


@transaction.atomic
def eliminar_venta_devolucion(request, transaccion):
    """Vista para eliminar una devolución de venta"""
    venta_devolucion = get_object_or_404(VentasDevolucionesCabezal, transaccion=transaccion)
    
    if request.method == 'POST':
        # Eliminar transacción asociada si existe
        try:
            transaccion_obj = Transaccion.objects.get(transaccion=transaccion)
            transaccion_obj.delete()
        except Transaccion.DoesNotExist:
            pass
        
        # Eliminar devolución venta (las líneas se eliminan en cascada)
        venta_devolucion.delete()
        messages.success(request, f'Devolución de Venta {transaccion} eliminada exitosamente.')
        return redirect('ventas_devoluciones:lista_ventas_devoluciones')
    
    context = {
        'venta_devolucion': venta_devolucion,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'ventas_devoluciones/eliminar_venta_devolucion.html', context)


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
        
        # Buscar por nombre (modo por defecto) - ACTIVO_COMERCIAL para ventas
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
            es_ser = articulo.producto_id and articulo.producto_id.startswith('SER')
            resultados.append({
                'id': articulo.pk,
                'nombre': articulo.nombre or '',
                'producto_id': articulo.producto_id or '',
                'text': articulo.nombre or 'Sin nombre',  # Solo nombre, sin ID
                'iva_valor': float(articulo.iva.valor) if articulo.iva else 0,
                'es_ser': es_ser,
            })
        
        return JsonResponse({'results': resultados})
            
    except Exception as e:
        import traceback
        print(f"Error en buscar_articulos: {e}")
        print(traceback.format_exc())
        return JsonResponse({'results': [], 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def obtener_ventas_cliente(request):
    """API AJAX para obtener ventas (facturas) de un cliente para devoluciones
    Filtra según el tipo de documento de devolución:
    - tncredit → solo trae efactura
    - devmovcli → solo trae movcli
    - ncreexpo → solo trae factexpo
    
    Si se pasa articulo_id, solo muestra las ventas que contienen ese artículo.
    """
    try:
        cliente_id = request.GET.get('cliente_id', '').strip()
        tipo_documento_devolucion = request.GET.get('tipo_documento_devolucion', '').strip()
        articulo_id = request.GET.get('articulo_id', '').strip()
        
        if not cliente_id:
            return JsonResponse({'results': [], 'error': 'cliente_id requerido'}, status=400)
        
        # Importar desde ventas_ingreso
        from ventas.ventas_ingreso.models import VentasCabezal, VentasLineas
        
        # Mapeo: tipo documento devolución → tipo documento venta
        mapeo_tipos = {
            'tncredit': 'efactura',      # Nota de Crédito Cliente → E-Factura
            'devmovcli': 'movcli',        # Devolución Movimiento Cliente → Movimiento Cliente
            'ncreexpo': 'factexpo',       # Nota de Crédito Exportación → Factura Exportación
        }
        
        # Obtener el tipo de documento de venta según el tipo de devolución
        tipo_documento_venta = mapeo_tipos.get(tipo_documento_devolucion)
        
        # Filtrar ventas del cliente
        ventas = VentasCabezal.objects.filter(
            id_cliente_id=cliente_id
        ).select_related('tipo_documento', 'id_cliente')
        
        # Si se especificó tipo_documento_devolucion, filtrar por el tipo de venta correspondiente
        if tipo_documento_venta:
            ventas = ventas.filter(tipo_documento__codigo=tipo_documento_venta)
        
        # Si se especificó articulo_id, filtrar solo las ventas que tienen ese artículo
        if articulo_id:
            # Obtener las transacciones de ventas que tienen este artículo
            ventas_con_articulo = VentasLineas.objects.filter(
                id_articulo_id=articulo_id
            ).values_list('transaccion', flat=True).distinct()
            
            # Filtrar por cliente y tipo de documento si aplica
            ventas_filtradas = VentasCabezal.objects.filter(
                transaccion__in=ventas_con_articulo,
                id_cliente_id=cliente_id
            )
            
            if tipo_documento_venta:
                ventas_filtradas = ventas_filtradas.filter(tipo_documento__codigo=tipo_documento_venta)
            
            ventas = ventas_filtradas.select_related('tipo_documento', 'id_cliente')
        
        ventas = ventas.order_by('-fecha_documento', '-transaccion')
        
        resultados = []
        for venta in ventas:
            resultados.append({
                'transaccion': venta.transaccion,
                'serie_documento': venta.serie_documento or '',
                'numero_documento': venta.numero_documento,
                'tipo_documento_codigo': venta.tipo_documento.codigo if venta.tipo_documento else '',
                'text': f"{venta.serie_documento or ''} {venta.numero_documento} ({venta.tipo_documento.codigo if venta.tipo_documento else ''})",
            })
        
        return JsonResponse({'results': resultados})
    except Exception as e:
        import traceback
        print(f"Error en obtener_ventas_cliente: {e}")
        print(traceback.format_exc())
        return JsonResponse({'results': [], 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def obtener_lineas_venta(request):
    """
    API AJAX para obtener líneas de una venta específica.
    Si se pasa articulo_id, solo muestra las líneas de ese artículo.
    """
    try:
        transaccion = request.GET.get('transaccion', '').strip()
        articulo_id = request.GET.get('articulo_id', '').strip()
        
        if not transaccion:
            return JsonResponse({'results': [], 'error': 'transaccion requerida'}, status=400)
        
        # Importar desde ventas_ingreso
        from ventas.ventas_ingreso.models import VentasCabezal, VentasLineas
        
        # Verificar que la venta existe
        try:
            venta = VentasCabezal.objects.get(transaccion=transaccion)
        except VentasCabezal.DoesNotExist:
            return JsonResponse({'results': [], 'error': 'Venta no encontrada'}, status=404)
        
        # Obtener líneas de la venta
        lineas = VentasLineas.objects.filter(
            transaccion=venta
        ).select_related('id_articulo', 'id_articulo__iva')
        
        # Si se especificó articulo_id, filtrar solo las líneas de ese artículo
        if articulo_id:
            lineas = lineas.filter(id_articulo_id=articulo_id)
        
        lineas = lineas.order_by('linea')
        
        resultados = []
        for linea in lineas:
            if linea.id_articulo:
                resultados.append({
                    'linea': linea.linea,
                    'id_articulo': linea.id_articulo.id,
                    'articulo_producto_id': linea.id_articulo.producto_id or '',
                    'articulo_nombre': linea.id_articulo.nombre or '',
                    'cantidad': float(linea.cantidad) if linea.cantidad else 0,
                    'precio_original': float(linea.precio_original) if linea.precio_original else 0,
                    'precio_neto': float(linea.precio_neto) if linea.precio_neto else 0,
                    'id_venta_linea': linea.id,
                    'iva_valor': float(linea.id_articulo.iva.valor) if linea.id_articulo.iva else 0,
                })
        
        return JsonResponse({
            'results': resultados,
            'venta_info': {
                'transaccion': venta.transaccion,
                'serie_documento': venta.serie_documento or '',
                'numero_documento': venta.numero_documento,
                'cliente_id': venta.id_cliente_id,
            }
        })
    except Exception as e:
        import traceback
        print(f"Error en obtener_lineas_venta: {e}")
        print(traceback.format_exc())
        return JsonResponse({'results': [], 'error': str(e)}, status=500)
