from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import Cliente
from erp_demo.config import EMPRESA_NOMBRE


@admin.register(Cliente)
class ClienteAdmin(ModelAdmin):
    list_display = ('codigo', 'nombre_comercial', 'razon_social', 'rut', 'telefono', 'email', 'departamento', 'canal_comercial', 'activo', 'fchhor')
    list_filter = ('activo', 'departamento', 'forma_pago', 'canal_comercial', 'monotributista')
    search_fields = ('codigo', 'nombre_comercial', 'razon_social', 'rut', 'email', 'telefono')
    list_editable = ('activo',)
    readonly_fields = ('codigo',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['empresa_nombre'] = EMPRESA_NOMBRE
        return super().changelist_view(request, extra_context=extra_context)

