from django import forms
from datetime import date
from .models import Equipo, PiedrasCanteras, PuntosPiedrasEquipo, Costos, ResultadosEquipo
from configuracion.articulos.models import Familia, Articulo


class EquipoForm(forms.ModelForm):
    """Formulario para crear y editar equipos"""
    
    class Meta:
        model = Equipo
        fields = ['nombre_equipo', 'responsable']
        widgets = {
            'nombre_equipo': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }
        labels = {
            'nombre_equipo': 'Nombre Equipo',
            'responsable': 'Responsable',
        }


class PiedrasCanterasForm(forms.ModelForm):
    """Formulario para crear y editar piedras/canteras"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar productos según familia seleccionada
        if 'familia_producto' in self.fields:
            self.fields['familia_producto'].queryset = Familia.objects.all().order_by('nombre')
        
        if 'producto' in self.fields:
            # Si hay instancia y tiene familia, filtrar productos
            if self.instance and self.instance.pk and self.instance.familia_producto:
                self.fields['producto'].queryset = Articulo.objects.filter(
                    idsubfamilia__familia=self.instance.familia_producto
                ).order_by('nombre')
            else:
                self.fields['producto'].queryset = Articulo.objects.none()
                self.fields['producto'].widget.attrs['disabled'] = True
    
    class Meta:
        model = PiedrasCanteras
        fields = ['familia_producto', 'producto', 'kpi', 'puntos']
        widgets = {
            'familia_producto': forms.Select(attrs={'class': 'form-control form-control-sm', 'id': 'id_familia_producto'}),
            'producto': forms.Select(attrs={'class': 'form-control form-control-sm', 'id': 'id_producto'}),
            'kpi': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'puntos': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
        }
        labels = {
            'familia_producto': 'Familia de Producto',
            'producto': 'Producto (Piedra)',
            'kpi': 'KPI',
            'puntos': 'Puntos',
        }


class PuntosPiedrasEquipoForm(forms.ModelForm):
    """Formulario para crear y editar puntos por equipo y piedra"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Establecer mes_año por defecto al primer día del mes actual
        if 'mes_año' in self.fields and not self.instance.pk:
            hoy = date.today()
            self.fields['mes_año'].initial = date(hoy.year, hoy.month, 1)
        
        # Si es nuevo registro y tiene piedra_cantera, sugerir puntos de la tabla maestra
        if not self.instance.pk and 'piedra_cantera' in self.fields:
            # Esto se manejará en JavaScript o en la vista
            pass
    
    class Meta:
        model = PuntosPiedrasEquipo
        fields = ['id_equipo', 'piedra_cantera', 'mes_año', 'puntos']
        widgets = {
            'id_equipo': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'piedra_cantera': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'mes_año': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'puntos': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
        }
        labels = {
            'id_equipo': 'Equipo',
            'piedra_cantera': 'Piedra/Cantera',
            'mes_año': 'Mes/Año',
            'puntos': 'Puntos',
        }


class CostosForm(forms.ModelForm):
    """Formulario para crear y editar costos"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Establecer fecha por defecto al primer día del mes actual
        if 'fecha' in self.fields and not self.instance.pk:
            hoy = date.today()
            self.fields['fecha'].initial = date(hoy.year, hoy.month, 1)
    
    class Meta:
        model = Costos
        fields = ['id_equipo', 'fecha', 'rubro', 'costo_dolares']
        widgets = {
            'id_equipo': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'rubro': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'costo_dolares': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
        }
        labels = {
            'id_equipo': 'Equipo',
            'fecha': 'Fecha (Mes/Año)',
            'rubro': 'Rubro',
            'costo_dolares': 'Costo en Dólares',
        }


class ResultadosEquipoForm(forms.ModelForm):
    """Formulario para crear y editar resultados de equipos"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Establecer mes_año por defecto al primer día del mes actual
        if 'mes_año' in self.fields and not self.instance.pk:
            hoy = date.today()
            self.fields['mes_año'].initial = date(hoy.year, hoy.month, 1)
        
        # puntos_calculados es readonly
        if 'puntos_calculados' in self.fields:
            self.fields['puntos_calculados'].widget.attrs['readonly'] = True
            self.fields['puntos_calculados'].required = False
    
    class Meta:
        model = ResultadosEquipo
        fields = ['id_equipo', 'piedra', 'mes_año', 'valuacion', 'kilos', 'puntos_calculados']
        widgets = {
            'id_equipo': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'piedra': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'mes_año': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'valuacion': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'kilos': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'puntos_calculados': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'readonly': True}),
        }
        labels = {
            'id_equipo': 'Equipo',
            'piedra': 'Piedra/Cantera',
            'mes_año': 'Mes/Año',
            'valuacion': 'Valuación',
            'kilos': 'Kilos',
            'puntos_calculados': 'Puntos Calculados',
        }

