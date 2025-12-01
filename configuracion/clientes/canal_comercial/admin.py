from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import CanalComercial


@admin.register(CanalComercial)
class CanalComercialAdmin(ModelAdmin):
    list_display = ('nombre', 'descripcion', 'activo', 'fchhor')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo',)

