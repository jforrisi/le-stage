from django import forms
from .models import Cliente, DEPARTAMENTOS_URUGUAY, FORMAS_PAGO, PAISES
from configuracion.clientes.canal_comercial.models import CanalComercial


class ClienteForm(forms.ModelForm):
    """Formulario para crear y editar clientes"""
    
    nombre_comercial = forms.CharField(
        required=True, 
        max_length=200, 
        label='Nombre Comercial',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ingrese el nombre comercial'})
    )
    razon_social = forms.CharField(
        required=True, 
        max_length=200, 
        label='Razón Social',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ingrese la razón social'})
    )
    rut = forms.IntegerField(
        required=True,
        label='RUT',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo canales activos
        self.fields['canal_comercial'].queryset = CanalComercial.objects.filter(activo='SI')
        
        # Hacer departamento obligatorio solo si país es Uruguay
        if 'pais' in self.data:
            pais = self.data.get('pais', 'UY')
            if pais != 'UY':
                self.fields['departamento'].required = False
        elif self.instance and self.instance.pk:
            if self.instance.pais != 'UY':
                self.fields['departamento'].required = False
        else:
            # Por defecto es Uruguay, así que departamento es obligatorio
            self.fields['departamento'].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        pais = cleaned_data.get('pais', 'UY')
        departamento = cleaned_data.get('departamento')
        
        # Validar que departamento sea obligatorio si país es Uruguay
        if pais == 'UY' and not departamento:
            raise forms.ValidationError({'departamento': 'El departamento es obligatorio cuando el país es Uruguay.'})
        
        return cleaned_data
    
    class Meta:
        model = Cliente
        fields = ['codigo', 'nombre_comercial', 'razon_social', 'rut', 'domicilio', 'pais',
                  'departamento', 'telefono', 'celular', 'contacto', 'email', 'forma_pago', 
                  'canal_comercial', 'observaciones', 'activo', 'monotributista']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'domicilio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ingrese la dirección'}),
            'pais': forms.Select(attrs={'class': 'form-control', 'id': 'id_pais'}, choices=PAISES),
            'departamento': forms.Select(attrs={'class': 'form-control'}, choices=[('', '---------')] + DEPARTAMENTOS_URUGUAY),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'forma_pago': forms.Select(attrs={'class': 'form-control'}, choices=FORMAS_PAGO),
            'canal_comercial': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.Select(attrs={'class': 'form-control'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
            'monotributista': forms.Select(attrs={'class': 'form-control'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
        }
        labels = {
            'codigo': 'Código',
            'nombre_comercial': 'Nombre Comercial',
            'razon_social': 'Razón Social',
            'rut': 'RUT',
            'domicilio': 'Domicilio',
            'pais': 'País',
            'departamento': 'Departamento',
            'telefono': 'Teléfono',
            'celular': 'Celular',
            'contacto': 'Contacto',
            'email': 'Email',
            'forma_pago': 'Forma de Pago',
            'canal_comercial': 'Canal Comercial',
            'observaciones': 'Observaciones',
            'activo': 'Activo',
            'monotributista': 'Monotributista',
        }

