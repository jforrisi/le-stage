from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import Disponibilidad


@admin.register(Disponibilidad)
class DisponibilidadAdmin(ModelAdmin):
    list_display = ('codigo', 'tipo', 'nombre_institucion', 'alias', 'moneda', 'saldo_inicial', 'fecha_ingreso_sistema', 'activo')
    list_filter = ('tipo', 'moneda', 'activo', 'tipo_cuenta', 'chequera', 'fecha_ingreso_sistema')
    search_fields = ('codigo', 'nombre_institucion', 'alias', 'numero')
    list_editable = ('activo',)
