from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import TipoArticulo, Familia, SubFamilia, Articulo, CodigoProveedorCompra, Moneda, IVA


@admin.register(TipoArticulo)
class TipoArticuloAdmin(ModelAdmin):
    list_display = ('codigo', 'nombre', 'stockeable', 'se_compra', 'loteable')
    list_filter = ('stockeable', 'se_compra', 'loteable')
    search_fields = ('codigo', 'nombre')


@admin.register(Familia)
class FamiliaAdmin(ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')


@admin.register(SubFamilia)
class SubFamiliaAdmin(ModelAdmin):
    list_display = ('codigo', 'familia', 'nombre')
    list_filter = ('familia',)
    search_fields = ('codigo', 'nombre', 'familia__nombre')


@admin.register(Articulo)
class ArticuloAdmin(ModelAdmin):
    list_display = ('producto_id', 'nombre', 'tipo_articulo', 'precio_venta', 'moneda_venta', 'ACTIVO_COMERCIAL')
    list_filter = ('tipo_articulo', 'ACTIVO_COMERCIAL', 'ACTIVO_STOCK', 'ACTIVO_COMPRAS', 'ACTIVO_PRODUCCION', 'LOTEABLE')
    search_fields = ('producto_id', 'nombre', 'tipo_articulo__nombre')
    list_editable = ('ACTIVO_COMERCIAL',)


@admin.register(CodigoProveedorCompra)
class CodigoProveedorCompraAdmin(ModelAdmin):
    list_display = ('articulo', 'proveedor', 'codigo_proveedor')
    list_filter = ('proveedor',)
    search_fields = ('articulo__producto_id', 'articulo__nombre', 'proveedor__razon', 'proveedor__nombre_comercial', 'codigo_proveedor')


@admin.register(Moneda)
class MonedaAdmin(ModelAdmin):
    list_display = ('codigo', 'nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre')
    list_editable = ('activo',)


@admin.register(IVA)
class IVAAdmin(ModelAdmin):
    list_display = ('codigo', 'nombre', 'valor', 'activo')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre')
    list_editable = ('activo',)
