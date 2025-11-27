from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import Proveedor


@admin.register(Proveedor)
class ProveedorAdmin(ModelAdmin):
    list_display = ('codigo', 'razon', 'rut', 'telefono', 'email', 'activo', 'fchhor')
    list_filter = ('activo', 'monotributista')
    search_fields = ('codigo', 'razon', 'razon2', 'rut', 'email', 'telefono')
    list_editable = ('activo',)
