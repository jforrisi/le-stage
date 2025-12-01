from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import ComprasCabezal, ComprasLineas


class ComprasLineasInline(admin.TabularInline):
    """Inline para editar líneas dentro del cabezal"""
    model = ComprasLineas
    extra = 1
    fields = ('linea', 'id_articulo', 'cantidad', 'precio_original', 'descuento', 
              'precio_neto', 'sub_total', 'iva', 'total')
    readonly_fields = ('precio_neto', 'sub_total', 'iva', 'total')


@admin.register(ComprasCabezal)
class ComprasCabezalAdmin(ModelAdmin):
    list_display = ('transaccion', 'numero_documento', 'id_proveedor', 'fecha_documento', 
                    'forma_pago', 'importe_total')
    list_filter = ('forma_pago', 'fecha_documento', 'tipo_documento', 'moneda')
    search_fields = ('transaccion', 'numero_documento', 'id_proveedor__razon', 
                     'id_proveedor__nombre_comercial')
    readonly_fields = ('transaccion', 'fchhor', 'sub_total', 'iva', 'importe_total', 'monotributista')
    date_hierarchy = 'fecha_documento'
    inlines = [ComprasLineasInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('transaccion', 'id_proveedor', 'tipo_documento', 'serie_documento', 
                      'numero_documento', 'monotributista')
        }),
        ('Fechas', {
            'fields': ('fecha_documento', 'fecha_movimiento', 'fecha_vencimiento')
        }),
        ('Pago', {
            'fields': ('forma_pago', 'plazo', 'disponibilidad', 'moneda', 'precio_iva_inc')
        }),
        ('Totales', {
            'fields': ('sub_total', 'iva', 'importe_total')
        }),
        ('Otros', {
            'fields': ('observaciones', 'fchhor', 'usuario')
        }),
    )


@admin.register(ComprasLineas)
class ComprasLineasAdmin(ModelAdmin):
    list_display = ('transaccion', 'linea', 'id_articulo', 'cantidad', 'precio_original', 'total')
    list_filter = ('transaccion',)
    search_fields = ('transaccion__transaccion', 'id_articulo__nombre', 'id_articulo__producto_id')
    readonly_fields = ('precio_neto', 'sub_total', 'iva', 'total')

