from django import forms
from .models import Disponibilidad, BANCOS, IEDES, TIPOS_DISPONIBILIDAD, TIPOS_CUENTA
from configuracion.articulos.models import Moneda


class DisponibilidadForm(forms.ModelForm):
    """Formulario dinámico para crear y editar disponibilidades"""
    
    tipo = forms.ChoiceField(
        choices=TIPOS_DISPONIBILIDAD,
        required=True,
        label='Tipo',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_tipo'})
    )
    
    nombre_institucion_banco = forms.ChoiceField(
        choices=[('', '---------')] + BANCOS,
        required=False,
        label='Banco',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_nombre_institucion_banco'})
    )
    
    nombre_institucion_iede = forms.ChoiceField(
        choices=[('', '---------')] + IEDES,
        required=False,
        label='Institución Emisora de Dinero Electrónico',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_nombre_institucion_iede'})
    )
    
    nombre_institucion = forms.CharField(
        required=False,
        max_length=200,
        label='Nombre Institución',
        widget=forms.HiddenInput(attrs={'id': 'id_nombre_institucion'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo monedas activas
        self.fields['moneda'].queryset = Moneda.objects.filter(activo='SI')
        # Hacer fecha_ingreso_sistema requerida en el formulario
        self.fields['fecha_ingreso_sistema'].required = True
        self.fields['saldo_inicial'].required = True
        
        # Si es edición, establecer valores iniciales
        if self.instance and self.instance.pk:
            if self.instance.tipo == 'BANCO':
                # Buscar el código del banco en BANCOS
                for codigo, nombre in BANCOS:
                    if nombre == self.instance.nombre_institucion:
                        self.fields['nombre_institucion_banco'].initial = codigo
                        break
            elif self.instance.tipo == 'IEDE':
                # Buscar el código del IEDE en IEDES
                for codigo, nombre in IEDES:
                    if nombre == self.instance.nombre_institucion:
                        self.fields['nombre_institucion_iede'].initial = codigo
                        break
    
    class Meta:
        model = Disponibilidad
        fields = [
            'codigo', 'tipo', 'nombre_institucion', 'alias', 'numero',
            'fecha_ingreso_sistema', 'saldo_inicial', 'moneda', 'tipo_cuenta', 
            'chequera', 'activo', 'observaciones'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nombre_institucion': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'alias': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_ingreso_sistema': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'saldo_inicial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-control'}),
            'tipo_cuenta': forms.Select(attrs={'class': 'form-control'}),
            'chequera': forms.Select(attrs={'class': 'form-control'}, choices=[('SI', 'Sí'), ('NO', 'No'), ('NA', 'N/A')]),
            'activo': forms.Select(attrs={'class': 'form-control'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'codigo': 'Código',
            'tipo': 'Tipo',
            'nombre_institucion': 'Nombre Institución',
            'alias': 'Alias',
            'numero': 'Número',
            'fecha_ingreso_sistema': 'Fecha de Ingreso al Sistema',
            'saldo_inicial': 'Saldo Inicial en Moneda Original',
            'moneda': 'Moneda',
            'tipo_cuenta': 'Tipo de Cuenta',
            'chequera': 'Chequera',
            'activo': 'Activo',
            'observaciones': 'Observaciones',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        nombre_institucion_banco = cleaned_data.get('nombre_institucion_banco')
        nombre_institucion_iede = cleaned_data.get('nombre_institucion_iede')
        
        # Validar según el tipo
        if tipo == 'BANCO':
            if not nombre_institucion_banco:
                raise forms.ValidationError({'nombre_institucion_banco': 'Debe seleccionar un banco.'})
            # Establecer nombre_institucion desde BANCOS
            for codigo, nombre in BANCOS:
                if codigo == nombre_institucion_banco:
                    cleaned_data['nombre_institucion'] = nombre
                    break
            # Validar que tipo_cuenta y chequera no sean NA
            if cleaned_data.get('tipo_cuenta') == 'NA':
                raise forms.ValidationError({'tipo_cuenta': 'Debe seleccionar un tipo de cuenta (Cuenta Corriente o Caja de Ahorro).'})
            if cleaned_data.get('chequera') == 'NA':
                raise forms.ValidationError({'chequera': 'Debe indicar si tiene chequera o no.'})
        elif tipo == 'IEDE':
            if not nombre_institucion_iede:
                raise forms.ValidationError({'nombre_institucion_iede': 'Debe seleccionar una IEDE.'})
            # Establecer nombre_institucion desde IEDES
            for codigo, nombre in IEDES:
                if codigo == nombre_institucion_iede:
                    cleaned_data['nombre_institucion'] = nombre
                    break
            # Para IEDE, tipo_cuenta y chequera deben ser NA
            cleaned_data['tipo_cuenta'] = 'NA'
            cleaned_data['chequera'] = 'NA'
        elif tipo == 'CAJA':
            cleaned_data['nombre_institucion'] = 'Caja'
            # Para CAJA, tipo_cuenta y chequera deben ser NA
            cleaned_data['tipo_cuenta'] = 'NA'
            cleaned_data['chequera'] = 'NA'
        
        return cleaned_data

