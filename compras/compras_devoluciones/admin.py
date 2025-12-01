from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import ComprasDevolucionesCabezal, ComprasDevolucionesLineas 

class ComprasDevolucionesLineasInline(admin.TabularInline):
    """Inline para editar líneas dentro del cabezal"""
    model = ComprasDevolucionesLineas
    extra = 1
    fields = ('linea', 'id_articulo', 'id_compra_linea','serie_doc_afectado',
    'numero_doc_afectado','cantidad','precio', 'sub_total', 'iva','total',
)
    readonly_fields = ('sub_total', 'iva', 'total')


@admin.register(ComprasDevolucionesCabezal)
class ComprasDevolucionesCabezalAdmin(ModelAdmin):
    list_display = ('transaccion', 'numero_documento', 'id_proveedor', 'fecha_documento', 
                    'forma_pago', 'importe_total')
    list_filter = ('forma_pago', 'fecha_documento', 'tipo_documento', 'moneda', 'id_proveedor')
    search_fields = ('transaccion', 'numero_documento', 'id_proveedor__razon', 
                     'id_proveedor__nombre_comercial')
    readonly_fields = ('transaccion', 'fchhor', 'sub_total', 'iva', 'importe_total', 'monotributista')
    date_hierarchy = 'fecha_documento'
    inlines = [ComprasDevolucionesLineasInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('transaccion', 'id_proveedor', 'tipo_documento', 'serie_documento', 
                      'numero_documento', 'monotributista', 'precio_iva_inc', 'moneda', 'tipo_compra')
        }),
        ('Fechas', {
            'fields': ('fecha_documento', 'fecha_movimiento')
        }),
        ('Pago', {
            'fields': ('forma_pago', 'disponibilidad',  )
        }),
        ('Totales', {
            'fields': ('sub_total', 'iva', 'importe_total')
        }),
        ('Otros', {
            'fields': ('observaciones', 'fchhor', 'usuario')
        }),
    )


@admin.register(ComprasDevolucionesLineas)
class ComprasDevolucionesLineasAdmin(ModelAdmin):
    list_display = ('transaccion', 'linea', 'id_articulo', 'id_compra_linea','serie_doc_afectado',
    'numero_doc_afectado','cantidad', 'precio')
    list_filter = ('transaccion',)
    search_fields = ('transaccion__transaccion', 'id_articulo__nombre', 'id_articulo__producto_id')
    readonly_fields = ('sub_total', 'iva', 'total')

