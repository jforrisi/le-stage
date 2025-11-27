from django import forms
from .models import TipoPulidoPiezas
from mineria_le_stage.models import PiezasCorteCantera


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


class PiezasCorteCanteraFormIndustria(forms.ModelForm):
    """Formulario para campos de industria en piezas corte cantera"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar que tipo_piedra tenga las opciones correctas
        self.fields['tipo_piedra'].choices = [('', '---------'), ('Ágata', 'Ágata'), ('Amatista', 'Amatista')]
        
        # Formatear fecha_industria para que se muestre correctamente en input type="date"
        if self.instance and self.instance.pk and self.instance.fecha_industria:
            self.fields['fecha_industria'].widget.attrs['value'] = self.instance.fecha_industria.strftime('%Y-%m-%d')
    
    class Meta:
        model = PiezasCorteCantera
        fields = [
            'fecha_industria', 'kilos_recepcion_industria', 'tipo_piedra',
            'tipo_proceso', 'kilos_despues_tallado', 'precio_por_kilo_tallado',
            'pulido_por_kilo', 'extra_carlos',
        ]
        widgets = {
            'fecha_industria': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}, format='%Y-%m-%d'),
            'kilos_recepcion_industria': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'tipo_piedra': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'tipo_proceso': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'kilos_despues_tallado': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'precio_por_kilo_tallado': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'pulido_por_kilo': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'extra_carlos': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }
        labels = {
            'fecha_industria': 'Fecha Industria',
            'kilos_recepcion_industria': 'Kilos en Recepción Industria',
            'tipo_piedra': 'Tipo de Piedra',
            'tipo_proceso': 'Tipos de Pulido Piezas',
            'kilos_despues_tallado': 'Kilos después del Tallado',
            'precio_por_kilo_tallado': 'Precio por Kilo de Tallado',
            'pulido_por_kilo': 'Pulido por Kilo',
            'extra_carlos': 'Extra Carlos',
        }

