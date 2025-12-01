from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import VentasDevolucionesCabezal, VentasDevolucionesLineas


class VentasDevolucionesLineasInline(admin.TabularInline):
    """Inline para editar líneas dentro del cabezal"""
    model = VentasDevolucionesLineas
    extra = 1
    fields = ('linea', 'id_articulo', 'cantidad', 'precio', 
              'sub_total', 'iva', 'total')
    readonly_fields = ('sub_total', 'iva', 'total')


@admin.register(VentasDevolucionesCabezal)
class VentasDevolucionesCabezalAdmin(ModelAdmin):
    list_display = ('transaccion', 'numero_documento', 'id_cliente', 'fecha_documento', 
                    'forma_pago', 'importe_total')
    list_filter = ('forma_pago', 'fecha_documento', 'tipo_documento', 'moneda')
    search_fields = ('transaccion', 'numero_documento', 'id_cliente__razon_social', 
                     'id_cliente__nombre_comercial')
    readonly_fields = ('transaccion', 'fchhor', 'sub_total', 'iva', 'importe_total')
    date_hierarchy = 'fecha_documento'
    inlines = [VentasDevolucionesLineasInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('transaccion', 'id_cliente', 'tipo_documento', 'serie_documento', 
                      'numero_documento')
        }),
        ('Fechas', {
            'fields': ('fecha_documento', 'fecha_movimiento')
        }),
        ('Pago', {
            'fields': ('forma_pago', 'disponibilidad', 'moneda', 'precio_iva_inc')
        }),
        ('Totales', {
            'fields': ('sub_total', 'iva', 'importe_total')
        }),
        ('Otros', {
            'fields': ('observaciones', 'fchhor', 'usuario')
        }),
    )


@admin.register(VentasDevolucionesLineas)
class VentasDevolucionesLineasAdmin(ModelAdmin):
    list_display = ('transaccion', 'linea', 'id_articulo', 'cantidad', 'precio', 'total')
    list_filter = ('transaccion',)
    search_fields = ('transaccion__transaccion', 'id_articulo__nombre', 'id_articulo__producto_id')
    readonly_fields = ('sub_total', 'iva', 'total')

