from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json
from .models import ComprasDevolucionesCabezal, ComprasDevolucionesLineas
from .forms import (
    ComprasDevolucionesCabezalForm, ComprasDevolucionesLineasForm, ComprasDevolucionesLineasFormSet
)
from configuracion.proveedores.models import Proveedor
from configuracion.transacciones.models import Transaccion
from configuracion.documentos.models import Documento
from configuracion.articulos.models import Articulo, CodigoProveedorCompra
from configuracion.tablas.models import PlazoPago
from erp_demo.config import EMPRESA_NOMBRE


def lista_compras_devoluciones(request):
    """Vista para listar todas las devoluciones de compras con paginación"""
    compras_devoluciones = ComprasDevolucionesCabezal.objects.all().select_related(
        'id_proveedor', 'tipo_documento'
    ).prefetch_related('lineas').order_by('-fchhor')
    
    # Búsqueda
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        compras_devoluciones = compras_devoluciones.filter(
            transaccion__icontains=busqueda
        ) | compras_devoluciones.filter(
            numero_documento__icontains=busqueda
        ) | compras_devoluciones.filter(
            id_proveedor__razon__icontains=busqueda
        ) | compras_devoluciones.filter(
            id_proveedor__nombre_comercial__icontains=busqueda
        )
    
    # Paginación: 15 registros por página
    paginator = Paginator(compras_devoluciones, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'devoluciones': page_obj,  # Cambiado a 'devoluciones' para consistencia con el template
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Devoluciones Compras',
    }
    return render(request, 'compras_devoluciones/lista_compras_devoluciones.html', context)


@transaction.atomic
def crear_compra_devolucion(request):
    """Vista para crear una nueva devolución de compra con guardado transaccional"""
    if request.method == 'POST':
        form = ComprasDevolucionesCabezalForm(request.POST)
        # Crear instancia temporal para el formset
        temp_instance = ComprasDevolucionesCabezal()
        formset = ComprasDevolucionesLineasFormSet(request.POST, instance=temp_instance)
        

        if form.is_valid() and formset.is_valid():
            # Guardar cabezal
            cabezal = form.save(commit=False)
            # Si no se seleccionó tipo_documento, usar 'ncprov' por defecto
            if not cabezal.tipo_documento:
                try:
                    documento = Documento.objects.get(codigo='ncprov')
                    cabezal.tipo_documento = documento
                except Documento.DoesNotExist:
                    pass
            # Si el proveedor es monotributista, forzar precio_iva_inc = 'SI'
            if cabezal.id_proveedor and cabezal.id_proveedor.monotributista == 'SI':
                cabezal.precio_iva_inc = 'SI'
            # Si viene del campo hidden (monotributista), usar ese valor
            if 'precio_iva_inc' in request.POST and request.POST['precio_iva_inc'] == 'SI' and cabezal.id_proveedor and cabezal.id_proveedor.monotributista == 'SI':
                cabezal.precio_iva_inc = 'SI'
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
                # Usar el documento del cabezal (puede ser  ncprov, devmovprov, ncimpo)
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
        
            messages.success(request, f'Devolución de Compra {cabezal.transaccion} creada exitosamente.')
            return redirect('compras_devoluciones:detalle_compra_devolucion', transaccion=cabezal.transaccion)
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
        form = ComprasDevolucionesCabezalForm()
        # Crear instancia temporal para el formset (necesaria para inlineformset)
        temp_instance = ComprasDevolucionesCabezal()
        formset = ComprasDevolucionesLineasFormSet(instance=temp_instance)
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
    
    # Obtener artículos para el select - ordenar SER* primero
    articulos_data = []
    # Primero obtener artículos SER* (producto_id que empieza con SER)
    articulos_ser = Articulo.objects.filter(
        ACTIVO_COMPRAS='SI',
        producto_id__startswith='SER'
    ).select_related('iva').order_by('producto_id')
    
    # Luego obtener el resto de artículos
    articulos_otros = Articulo.objects.filter(
        ACTIVO_COMPRAS='SI'
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
        'titulo': 'Nueva Devolución de Compra',
        'empresa_nombre': EMPRESA_NOMBRE,
        'proveedores_data': json.dumps(proveedores_data),
        'formas_pago_data': json.dumps(formas_pago_data),
        'articulos_data': json.dumps(articulos_data),
    }
    return render(request, 'compras_devoluciones/form_compra_devolucion.html', context)


@transaction.atomic
def editar_compra_devolucion(request, transaccion):
    """Vista para editar una devolución de compra existente"""
    compra_devolucion = get_object_or_404(ComprasDevolucionesCabezal, transaccion=transaccion)
    
    if request.method == 'POST':
        form = ComprasDevolucionesCabezalForm(request.POST, instance=compra_devolucion)
        formset = ComprasDevolucionesLineasFormSet(request.POST, instance=compra_devolucion)
        
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
            
            messages.success(request, f'Devolución de compra {cabezal.transaccion} actualizada exitosamente.')
            return redirect('compras_devoluciones:detalle_compra_devolucion', transaccion=cabezal.transaccion)
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
        form = ComprasDevolucionesCabezalForm(instance=compra_devolucion)
        formset = ComprasDevolucionesLineasFormSet(instance=compra_devolucion)
    
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
    
    # Obtener artículos para el select - ordenar SER* primero
    articulos_data = []
    # Primero obtener artículos SER* (producto_id que empieza con SER)
    articulos_ser = Articulo.objects.filter(
        ACTIVO_COMPRAS='SI',
        producto_id__startswith='SER'
    ).select_related('iva').order_by('producto_id')
    
    # Luego obtener el resto de artículos
    articulos_otros = Articulo.objects.filter(
        ACTIVO_COMPRAS='SI'
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
        'compra_devolucion': compra_devolucion,
        'titulo': f'Editar Devolución de Compra {compra_devolucion.transaccion}',
        'empresa_nombre': EMPRESA_NOMBRE,
        'proveedores_data': json.dumps(proveedores_data),
        'formas_pago_data': json.dumps(formas_pago_data),
        'articulos_data': json.dumps(articulos_data),
    }
    return render(request, 'compras_devoluciones/form_compra_devolucion.html', context)


def detalle_compra_devolucion(request, transaccion):
    """Vista para ver el detalle de una devolución de compra"""
    compra_devolucion = get_object_or_404(ComprasDevolucionesCabezal, transaccion=transaccion)
    lineas = compra_devolucion.lineas.all().select_related('id_articulo', 'id_articulo__iva').order_by('linea')
    
    context = {
        'compra_devolucion': compra_devolucion,
        'lineas': lineas,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': f'Devolución de Compra {compra_devolucion.transaccion}',
    }
    return render(request, 'compras_devoluciones/detalle_compra_devolucion.html', context)


@transaction.atomic
def eliminar_compra_devolucion(request, transaccion):
    """Vista para eliminar una devolución de compra"""
    compra_devolucion = get_object_or_404(ComprasDevolucionesCabezal, transaccion=transaccion)
    
    if request.method == 'POST':
        # Eliminar transacción asociada si existe
        try:
            transaccion_obj = Transaccion.objects.get(transaccion=transaccion)
            transaccion_obj.delete()
        except Transaccion.DoesNotExist:
            pass
        
        # Eliminar devolución compra (las líneas se eliminan en cascada)
        compra_devolucion.delete()
        messages.success(request, f'Devolución de Compra {transaccion} eliminada exitosamente.')
        return redirect('compras_devoluciones:lista_compras_devoluciones')
    
    context = {
        'compra_devolucion': compra_devolucion,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'compras_devoluciones/eliminar_compra_devolucion.html', context)


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
                    es_ser = articulo.producto_id and articulo.producto_id.startswith('SER')
                    resultados.append({
                        'id': articulo.pk,
                        'nombre': articulo.nombre or '',
                        'producto_id': articulo.producto_id or '',
                        'text': f"{codigo_prov.codigo_proveedor} - {articulo.nombre or 'Sin nombre'}",
                        'codigo_proveedor': codigo_prov.codigo_proveedor,
                        'iva_valor': float(articulo.iva.valor) if articulo.iva else 0,
                        'es_ser': es_ser,
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
def obtener_compras_proveedor(request):
    """API AJAX para obtener compras (facturas) de un proveedor para devoluciones
    Filtra según el tipo de documento de devolución:
    - ncprov → solo trae facprov
    - devmovprov → solo trae movprov
    - ncimpo → solo trae factimp
    
    Si se pasa articulo_id, solo muestra las compras que contienen ese artículo.
    """
    try:
        proveedor_id = request.GET.get('proveedor_id', '').strip()
        tipo_documento_devolucion = request.GET.get('tipo_documento_devolucion', '').strip()
        articulo_id = request.GET.get('articulo_id', '').strip()
        
        if not proveedor_id:
            return JsonResponse({'results': [], 'error': 'proveedor_id requerido'}, status=400)
        
        # Importar desde compras_ingreso
        from compras.compras_ingreso.models import ComprasCabezal, ComprasLineas
        
        # Mapeo: tipo documento devolución → tipo documento compra
        mapeo_tipos = {
            'ncprov': 'facprov',      # Nota de Crédito Proveedor → Factura Proveedor
            'devmovprov': 'movprov',  # Devolución Movimiento Proveedor → Movimiento Proveedor
            'ncimpo': 'factimp',      # Nota de Crédito Importación → Factura Importación
        }
        
        # Obtener el tipo de documento de compra según el tipo de devolución
        tipo_documento_compra = mapeo_tipos.get(tipo_documento_devolucion)
        
        # Filtrar compras del proveedor
        compras = ComprasCabezal.objects.filter(
            id_proveedor_id=proveedor_id
        ).select_related('tipo_documento', 'id_proveedor')
        
        # Si se especificó tipo_documento_devolucion, filtrar por el tipo de compra correspondiente
        if tipo_documento_compra:
            compras = compras.filter(tipo_documento__codigo=tipo_documento_compra)
        
        # Si se especificó articulo_id, filtrar solo las compras que tienen ese artículo
        if articulo_id:
            # Obtener las transacciones de compras que tienen este artículo
            compras_con_articulo = ComprasLineas.objects.filter(
                id_articulo_id=articulo_id
            ).values_list('transaccion', flat=True).distinct()
            
            # Filtrar por proveedor y tipo de documento si aplica
            compras_filtradas = ComprasCabezal.objects.filter(
                transaccion__in=compras_con_articulo,
                id_proveedor_id=proveedor_id
            )
            
            if tipo_documento_compra:
                compras_filtradas = compras_filtradas.filter(tipo_documento__codigo=tipo_documento_compra)
            
            compras = compras_filtradas.select_related('tipo_documento', 'id_proveedor')
        
        compras = compras.order_by('-fecha_documento', '-transaccion')
        
        resultados = []
        for compra in compras:
            resultados.append({
                'transaccion': compra.transaccion,
                'serie_documento': compra.serie_documento or '',
                'numero_documento': compra.numero_documento,
                'tipo_documento_codigo': compra.tipo_documento.codigo if compra.tipo_documento else '',
                'text': f"{compra.serie_documento or ''} {compra.numero_documento} ({compra.tipo_documento.codigo if compra.tipo_documento else ''})",
            })
        
        return JsonResponse({'results': resultados})
    except Exception as e:
        import traceback
        print(f"Error en obtener_compras_proveedor: {e}")
        print(traceback.format_exc())
        return JsonResponse({'results': [], 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def obtener_lineas_compra(request):
    """API AJAX para obtener líneas (artículos) de una compra específica para devoluciones
    Si se pasa articulo_id, solo muestra las líneas de ese artículo.
    """
    try:
        transaccion = request.GET.get('transaccion', '').strip()
        articulo_id = request.GET.get('articulo_id', '').strip()
        
        if not transaccion:
            return JsonResponse({'results': [], 'error': 'transaccion requerida'}, status=400)
        
        # Importar desde compras_ingreso
        from compras.compras_ingreso.models import ComprasCabezal, ComprasLineas
        
        # Verificar que la compra existe
        try:
            compra = ComprasCabezal.objects.get(transaccion=transaccion)
        except ComprasCabezal.DoesNotExist:
            return JsonResponse({'results': [], 'error': 'Compra no encontrada'}, status=404)
        
        # Obtener líneas de la compra
        lineas = ComprasLineas.objects.filter(
            transaccion=compra
        ).select_related('id_articulo', 'id_articulo__iva')
        
        # Si se especificó articulo_id, filtrar solo las líneas de ese artículo
        if articulo_id:
            lineas = lineas.filter(id_articulo_id=articulo_id)
        
        lineas = lineas.order_by('linea')
        
        resultados = []
        for linea in lineas:
            if linea.id_articulo:  # Solo incluir líneas con artículo
                resultados.append({
                    'linea': linea.linea,
                    'id_articulo': linea.id_articulo.id,
                    'articulo_producto_id': linea.id_articulo.producto_id or '',
                    'articulo_nombre': linea.id_articulo.nombre or '',
                    'cantidad': float(linea.cantidad) if linea.cantidad else 0,
                    'precio_neto': float(linea.precio_neto) if linea.precio_neto else 0,
                    'id_compra_linea': linea.id,
                    'iva_valor': float(linea.id_articulo.iva.valor) if linea.id_articulo.iva else 0,
                })
        
        return JsonResponse({
            'results': resultados,
            'compra_info': {
                'transaccion': compra.transaccion,
                'serie_documento': compra.serie_documento or '',
                'numero_documento': compra.numero_documento,
                'proveedor_id': compra.id_proveedor_id,
            }
        })
    except Exception as e:
        import traceback
        print(f"Error en obtener_lineas_compra: {e}")
        print(traceback.format_exc())
        return JsonResponse({'results': [], 'error': str(e)}, status=500)