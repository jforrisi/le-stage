from django import forms
from django.forms import formset_factory
from datetime import date, datetime
from .models import (
    Equipo, EquipoCorte, PiedrasCanteras, ProduccionEquipo, Costos,
    PiezasCorteCantera
)
from configuracion.articulos.models import Familia, Articulo

# Obtener choices de rubros desde el modelo
RUBROS_CHOICES = Costos.RUBROS_CHOICES


class MonthInput(forms.DateInput):
    """Widget personalizado para input type="month" que maneja formato YYYY-MM"""
    input_type = 'month'
    
    def format_value(self, value):
        """Convierte el valor a formato YYYY-MM para el input type="month" """
        if value is None:
            return None
        if isinstance(value, str):
            # Si ya es string, verificar formato
            if len(value) == 7 and value[4] == '-':  # Formato YYYY-MM
                return value
            # Intentar parsear como fecha
            try:
                if len(value) == 10:  # Formato YYYY-MM-DD
                    value = datetime.strptime(value, '%Y-%m-%d').date()
                else:
                    value = datetime.strptime(value, '%Y-%m').date()
            except:
                return None
        if isinstance(value, date):
            return value.strftime('%Y-%m')
        return None


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


class EquipoCorteForm(forms.ModelForm):
    """Formulario para crear y editar equipos de corte"""
    
    class Meta:
        model = EquipoCorte
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
            # Obtener el modelo del campo (ya tiene el db_table correcto configurado)
            producto_field = self.fields['producto']
            ArticuloModel = producto_field.queryset.model
            
            # Determinar la familia a usar para filtrar productos
            familia = None
            
            # Si hay datos POST, usar la familia del POST
            if self.data and 'familia_producto' in self.data:
                try:
                    familia_id = self.data.get('familia_producto')
                    if familia_id:
                        familia = Familia.objects.get(pk=familia_id)
                except (ValueError, Familia.DoesNotExist):
                    pass
            
            # Si no hay datos POST pero hay instancia con familia, usar esa
            if not familia and self.instance and self.instance.pk and self.instance.familia_producto:
                familia = self.instance.familia_producto
            
            # Filtrar productos según la familia usando el modelo del campo
            if familia:
                self.fields['producto'].queryset = ArticuloModel.objects.filter(
                    idsubfamilia__familia=familia
                ).order_by('nombre')
            else:
                # Si no hay familia, usar todos los productos del modelo (ya tiene el db_table correcto)
                self.fields['producto'].queryset = ArticuloModel.objects.all().order_by('nombre')
    
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


class ProduccionEquipoCabezalForm(forms.Form):
    """Formulario para el cabezal de producción (Equipo + Mes/Año)"""
    
    mes_año = forms.DateField(
        label='Mes/Año',
        widget=MonthInput(attrs={'class': 'form-control form-control-sm'}),
        help_text='Seleccione mes y año',
        input_formats=['%Y-%m', '%Y-%m-%d'],  # Aceptar ambos formatos
    )
    
    id_equipo = forms.ModelChoiceField(
        queryset=Equipo.objects.all().order_by('nombre_equipo'),
        label='Equipo',
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer mes_año por defecto al primer día del mes actual
        # El input type="month" necesita formato YYYY-MM (string)
        if not self.initial.get('mes_año'):
            hoy = date.today()
            self.fields['mes_año'].initial = f"{hoy.year}-{hoy.month:02d}"
        else:
            # Si hay un valor inicial (puede ser date o string), convertirlo a formato YYYY-MM
            valor_inicial = self.initial.get('mes_año')
            if isinstance(valor_inicial, date):
                self.fields['mes_año'].initial = valor_inicial.strftime('%Y-%m')
            elif isinstance(valor_inicial, str) and len(valor_inicial) > 7:
                # Si es string con formato de fecha completa, extraer solo año-mes
                try:
                    fecha_obj = date.fromisoformat(valor_inicial[:10])
                    self.fields['mes_año'].initial = fecha_obj.strftime('%Y-%m')
                except:
                    pass


class ProduccionEquipoLineaForm(forms.Form):
    """Formulario para cada línea de producción (una por piedra)"""
    
    piedra_cantera = forms.ModelChoiceField(
        queryset=PiedrasCanteras.objects.none(),  # Se establecerá en la vista
        widget=forms.HiddenInput(),
        required=True,
    )
    
    piedra_nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'readonly': True}),
        label='Piedra/Cantera',
    )
    
    kpi_display = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'readonly': True}),
        label='KPI',
    )
    
    kpi_valor = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),  # Valor real del KPI para JavaScript
    )
    
    puntos = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
        label='Puntos',
    )
    
    valuacion = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
        label='Valor Monetario',
    )
    
    kilos = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
        label='Kilos',
    )
    
    puntos_calculados = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'readonly': True}),
        label='Puntos Calculados',
    )


# Formset para las líneas de producción
# Nota: extra se establecerá dinámicamente en la vista según el número de piedras
ProduccionEquipoLineaFormSet = formset_factory(
    ProduccionEquipoLineaForm,
    extra=0,  # Se ajustará dinámicamente
    can_delete=False,
)


class CostosCabezalForm(forms.Form):
    """Formulario para el cabezal de costos (Equipo + Mes/Año)"""
    
    fecha = forms.DateField(
        label='Mes/Año',
        widget=MonthInput(attrs={'class': 'form-control form-control-sm'}),
        help_text='Seleccione mes y año',
        input_formats=['%Y-%m', '%Y-%m-%d'],
    )
    
    id_equipo = forms.ModelChoiceField(
        queryset=Equipo.objects.all().order_by('nombre_equipo'),
        label='Equipo',
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'}),
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer fecha por defecto al primer día del mes actual
        if not self.initial.get('fecha'):
            hoy = date.today()
            self.fields['fecha'].initial = f"{hoy.year}-{hoy.month:02d}"


class CostosLineaForm(forms.Form):
    """Formulario para cada línea de costo (una por rubro)"""
    
    rubro_display = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'readonly': True}),
        label='Rubro',
    )
    
    rubro_valor = forms.ChoiceField(
        choices=RUBROS_CHOICES,
        required=False,
        widget=forms.HiddenInput(),
    )
    
    costo_dolares = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
        label='Costo (USD)',
    )
    
    costo_dolares = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
        label='Costo (USD)',
    )


# Formset para las líneas de costos
CostosLineaFormSet = formset_factory(
    CostosLineaForm,
    extra=0,  # Se ajustará dinámicamente
    can_delete=False,
)


# ==================== PIEZAS CORTE CANTERA ====================

class PiezasCorteCanteraFormMineria(forms.ModelForm):
    """Formulario para piezas corte cantera - Solo campos de minería"""
    
    class Meta:
        model = PiezasCorteCantera
        fields = [
            'nombre_piedra', 'numero',
            'fecha_extraccion', 'equipo_minero', 'equipo_corte', 'kilos_en_cantera',
            'valuacion_cantera', 'porcentaje_valuacion_corte', 'ganancia_equipo_corte',
        ]
        widgets = {
            'nombre_piedra': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'numero': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'fecha_extraccion': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'equipo_minero': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'equipo_corte': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'kilos_en_cantera': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'valuacion_cantera': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'porcentaje_valuacion_corte': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0', 'max': '100'}),
            'ganancia_equipo_corte': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0', 'readonly': True}),
        }
        labels = {
            'nombre_piedra': 'Nombre Piedra',
            'numero': 'Número',
            'fecha_extraccion': 'Fecha Extracción',
            'equipo_minero': 'Equipo Minero',
            'equipo_corte': 'Equipo de Corte',
            'kilos_en_cantera': 'Kilos en Cantera',
            'valuacion_cantera': 'Valuación Cantera',
            'porcentaje_valuacion_corte': '% de Valuación para Equipo de Corte',
            'ganancia_equipo_corte': 'Ganancia Equipo de Corte',
        }

