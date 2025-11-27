from django import forms
from .models import CanalComercial


class CanalComercialForm(forms.ModelForm):
    """Formulario para crear y editar canales comerciales"""
    
    class Meta:
        model = CanalComercial
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.Select(attrs={'class': 'form-control'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'activo': 'Activo',
        }

