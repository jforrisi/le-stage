from django import forms
from .models import TipoPulidoPiezas


class TipoPulidoPiezasForm(forms.ModelForm):
    """Formulario para crear y editar tipos de pulido de piezas"""
    
    class Meta:
        model = TipoPulidoPiezas
        fields = ['nombre', 'observaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3}),
        }
        labels = {
            'nombre': 'Nombre',
            'observaciones': 'Observaciones',
        }

