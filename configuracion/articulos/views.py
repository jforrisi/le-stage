from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import TipoArticulo, Familia, SubFamilia, Articulo, CodigoProveedorCompra, Moneda, IVA
from .forms import TipoArticuloForm, FamiliaForm, SubFamiliaForm, ArticuloForm, CodigoProveedorForm
from configuracion.proveedores.models import Proveedor
from erp_demo.config import EMPRESA_NOMBRE


# ========== TIPO DE ARTÍCULO ==========
def lista_tipos_articulo(request):
    """Vista para listar todos los tipos de artículo"""
    tipos = TipoArticulo.objects.all()
    
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        tipos = tipos.filter(
            nombre__icontains=busqueda
        ) | tipos.filter(
            codigo__icontains=busqueda
        )
    
    context = {
        'tipos': tipos,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'articulos/tipo_articulo/lista_tipos.html', context)


def crear_tipo_articulo(request):
    """Vista para crear un nuevo tipo de artículo"""
    if request.method == 'POST':
        form = TipoArticuloForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de artículo creado exitosamente.')
            return redirect('lista_tipos_articulo')
    else:
        form = TipoArticuloForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Tipo de Artículo',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'articulos/tipo_articulo/form_tipo.html', context)


def editar_tipo_articulo(request, codigo):
    """Vista para editar un tipo de artículo existente"""
    tipo = get_object_or_404(TipoArticulo, codigo=codigo)
    
    if request.method == 'POST':
        form = TipoArticuloForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de artículo actualizado exitosamente.')
            return redirect('lista_tipos_articulo')
    else:
        form = TipoArticuloForm(instance=tipo)
    
    context = {
        'form': form,
        'tipo': tipo,
        'titulo': 'Editar Tipo de Artículo',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'articulos/tipo_articulo/form_tipo.html', context)


def eliminar_tipo_articulo(request, codigo):
    """Vista para eliminar un tipo de artículo"""
    tipo = get_object_or_404(TipoArticulo, codigo=codigo)
    
    if request.method == 'POST':
        tipo.delete()
        messages.success(request, 'Tipo de artículo eliminado exitosamente.')
        return redirect('lista_tipos_articulo')
    
    context = {
        'tipo': tipo,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'articulos/tipo_articulo/eliminar_tipo.html', context)


# ========== FAMILIA ==========
def lista_familias(request):
    """Vista para listar todas las familias"""
    familias = Familia.objects.all()
    
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        familias = familias.filter(
            nombre__icontains=busqueda
        ) | familias.filter(
            codigo__icontains=busqueda
        )
    
    context = {
        'familias': familias,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'articulos/familia/lista_familias.html', context)


def crear_familia(request):
    """Vista para crear una nueva familia"""
    if request.method == 'POST':
        form = FamiliaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Familia creada exitosamente.')
            return redirect('lista_familias')
    else:
        form = FamiliaForm()
    
    context = {
        'form': form,
        'titulo': 'Nueva Familia',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'articulos/familia/form_familia.html', context)


def editar_familia(request, pk):
    """Vista para editar una familia existente"""
    familia = get_object_or_404(Familia, pk=pk)
    
    if request.method == 'POST':
        form = FamiliaForm(request.POST, instance=familia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Familia actualizada exitosamente.')
            return redirect('lista_familias')
    else:
        form = FamiliaForm(instance=familia)
    
    context = {
        'form': form,
        'familia': familia,
        'titulo': 'Editar Familia',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'articulos/familia/form_familia.html', context)


def eliminar_familia(request, pk):
    """Vista para eliminar una familia"""
    familia = get_object_or_404(Familia, pk=pk)
    
    if request.method == 'POST':
        familia.delete()
        messages.success(request, 'Familia eliminada exitosamente.')
        return redirect('lista_familias')
    
    context = {
        'familia': familia,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'articulos/familia/eliminar_familia.html', context)


# ========== SUB FAMILIA ==========
def lista_subfamilias(request):
    """Vista para listar todas las subfamilias"""
    subfamilias = SubFamilia.objects.all()
    
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        subfamilias = subfamilias.filter(
            nombre__icontains=busqueda
        ) | subfamilias.filter(
            codigo__icontains=busqueda
        )
    
    context = {
        'subfamilias': subfamilias,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'articulos/subfamilia/lista_subfamilias.html', context)


def crear_subfamilia(request):
    """Vista para crear una nueva subfamilia"""
    if request.method == 'POST':
        form = SubFamiliaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sub familia creada exitosamente.')
            return redirect('lista_subfamilias')
    else:
        form = SubFamiliaForm()
    
    context = {
        'form': form,
        'titulo': 'Nueva Sub Familia',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'articulos/subfamilia/form_subfamilia.html', context)


def editar_subfamilia(request, pk):
    """Vista para editar una subfamilia existente"""
    subfamilia = get_object_or_404(SubFamilia, pk=pk)
    
    if request.method == 'POST':
        form = SubFamiliaForm(request.POST, instance=subfamilia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sub familia actualizada exitosamente.')
            return redirect('lista_subfamilias')
    else:
        form = SubFamiliaForm(instance=subfamilia)
    
    context = {
        'form': form,
        'subfamilia': subfamilia,
        'titulo': 'Editar Sub Familia',
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'articulos/subfamilia/form_subfamilia.html', context)


def eliminar_subfamilia(request, pk):
    """Vista para eliminar una subfamilia"""
    subfamilia = get_object_or_404(SubFamilia, pk=pk)
    
    if request.method == 'POST':
        subfamilia.delete()
        messages.success(request, 'Sub familia eliminada exitosamente.')
        return redirect('lista_subfamilias')
    
    context = {
        'subfamilia': subfamilia,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'articulos/subfamilia/eliminar_subfamilia.html', context)


# ========== ARTÍCULO ==========
def lista_articulos(request):
    """Vista para listar todos los artículos"""
    articulos = Articulo.objects.all()
    
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        articulos = articulos.filter(
            nombre__icontains=busqueda
        ) | articulos.filter(
            producto_id__icontains=busqueda
        )
    
    context = {
        'articulos': articulos,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'articulos/articulo/lista_articulos.html', context)


def crear_articulo(request):
    """Vista para crear un nuevo artículo"""
    if request.method == 'POST':
        form = ArticuloForm(request.POST)
        if form.is_valid():
            articulo = form.save()
            
            # Procesar códigos de proveedor
            codigos_proveedor_data = request.POST.getlist('codigos_proveedor')
            proveedores_data = request.POST.getlist('proveedores')
            codigos_data = request.POST.getlist('codigos')
            
            # Eliminar códigos existentes si estamos editando
            if articulo.pk:
                CodigoProveedorCompra.objects.filter(articulo=articulo).delete()
            
            # Crear nuevos códigos de proveedor
            proveedores_agregados = set()  # Para evitar duplicados
            for i, proveedor_id in enumerate(proveedores_data):
                if proveedor_id and codigos_data[i]:
                    if proveedor_id in proveedores_agregados:
                        messages.warning(request, f'El proveedor seleccionado ya tiene un código asignado. Se omitió el duplicado.')
                        continue
                    try:
                        proveedor = Proveedor.objects.get(pk=proveedor_id)
                        CodigoProveedorCompra.objects.create(
                            articulo=articulo,
                            proveedor=proveedor,
                            codigo_proveedor=codigos_data[i]
                        )
                        proveedores_agregados.add(proveedor_id)
                    except Proveedor.DoesNotExist:
                        pass
                    except Exception as e:
                        # Manejar error de integridad (proveedor duplicado)
                        if 'UNIQUE constraint' in str(e) or 'unique constraint' in str(e).lower():
                            messages.warning(request, f'El proveedor ya tiene un código asignado. Se omitió el duplicado.')
                        else:
                            raise
            
            messages.success(request, 'Artículo creado exitosamente.')
            return redirect('lista_articulos')
    else:
        form = ArticuloForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Artículo',
        'empresa_nombre': EMPRESA_NOMBRE,
        'codigos_proveedor': [],
    }
    return render(request, 'articulos/articulo/form_articulo.html', context)


def editar_articulo(request, pk):
    """Vista para editar un artículo existente"""
    articulo = get_object_or_404(Articulo, pk=pk)
    
    if request.method == 'POST':
        form = ArticuloForm(request.POST, instance=articulo)
        if form.is_valid():
            articulo = form.save()
            
            # Procesar códigos de proveedor
            codigos_proveedor_data = request.POST.getlist('codigos_proveedor')
            proveedores_data = request.POST.getlist('proveedores')
            codigos_data = request.POST.getlist('codigos')
            
            # Eliminar códigos existentes
            CodigoProveedorCompra.objects.filter(articulo=articulo).delete()
            
            # Crear nuevos códigos de proveedor
            proveedores_agregados = set()  # Para evitar duplicados
            for i, proveedor_id in enumerate(proveedores_data):
                if proveedor_id and codigos_data[i]:
                    if proveedor_id in proveedores_agregados:
                        messages.warning(request, f'El proveedor seleccionado ya tiene un código asignado. Se omitió el duplicado.')
                        continue
                    try:
                        proveedor = Proveedor.objects.get(pk=proveedor_id)
                        CodigoProveedorCompra.objects.create(
                            articulo=articulo,
                            proveedor=proveedor,
                            codigo_proveedor=codigos_data[i]
                        )
                        proveedores_agregados.add(proveedor_id)
                    except Proveedor.DoesNotExist:
                        pass
                    except Exception as e:
                        # Manejar error de integridad (proveedor duplicado)
                        if 'UNIQUE constraint' in str(e) or 'unique constraint' in str(e).lower():
                            messages.warning(request, f'El proveedor ya tiene un código asignado. Se omitió el duplicado.')
                        else:
                            raise
            
            messages.success(request, 'Artículo actualizado exitosamente.')
            return redirect('lista_articulos')
    else:
        form = ArticuloForm(instance=articulo)
        codigos_proveedor = CodigoProveedorCompra.objects.filter(articulo=articulo)
    
    context = {
        'form': form,
        'articulo': articulo,
        'titulo': 'Editar Artículo',
        'empresa_nombre': EMPRESA_NOMBRE,
        'codigos_proveedor': codigos_proveedor,
    }
    return render(request, 'articulos/articulo/form_articulo.html', context)


def eliminar_articulo(request, pk):
    """Vista para eliminar un artículo"""
    articulo = get_object_or_404(Articulo, pk=pk)
    
    if request.method == 'POST':
        articulo.delete()
        messages.success(request, 'Artículo eliminado exitosamente.')
        return redirect('lista_articulos')
    
    context = {
        'articulo': articulo,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'articulos/articulo/eliminar_articulo.html', context)


def detalle_articulo(request, pk):
    """Vista para ver el detalle de un artículo"""
    articulo = get_object_or_404(Articulo, pk=pk)
    
    context = {
        'articulo': articulo,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'articulos/articulo/detalle_articulo.html', context)


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
            # Usar razon si existe, sino nombre_comercial, sino 'Sin nombre'
            nombre_display = proveedor.razon if proveedor.razon else (proveedor.nombre_comercial if proveedor.nombre_comercial else 'Sin nombre')
            codigo_display = proveedor.codigo if proveedor.codigo else 'Sin código'
            
            resultados.append({
                'id': proveedor.pk,
                'codigo': codigo_display,
                'razon': proveedor.razon if proveedor.razon else '',
                'nombre_comercial': proveedor.nombre_comercial if proveedor.nombre_comercial else '',
                'text': f"{codigo_display} - {nombre_display}"
            })
        
        return JsonResponse({'results': resultados})
    except Exception as e:
        import traceback
        print(f"Error en buscar_proveedores: {e}")
        print(traceback.format_exc())
        return JsonResponse({'results': [], 'error': str(e)}, status=500)


def lista_ivas(request):
    """Vista para listar todas las tasas de IVA"""
    ivas = IVA.objects.all()
    
    context = {
        'ivas': ivas,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Lista de IVAs',
    }
    return render(request, 'articulos/iva/lista_ivas.html', context)
