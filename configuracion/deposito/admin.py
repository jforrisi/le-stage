from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import Deposito


@admin.register(Deposito)
class DepositoAdmin(ModelAdmin):
    list_display = ('id', 'nombre', 'explicacion')
    list_filter = ('nombre',)
    search_fields = ('nombre', 'explicacion')
    list_editable = ('nombre',)

