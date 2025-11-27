from django import forms
from .models import Proveedor
from configuracion.clientes.models import PAISES, DEPARTAMENTOS_URUGUAY, FORMAS_PAGO


class ProveedorForm(forms.ModelForm):
    """Formulario para crear y editar proveedores"""
    
    razon = forms.CharField(
        required=True,
        max_length=200,
        label='Razón Social',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nombre_comercial = forms.CharField(
        required=True,
        max_length=200,
        label='Nombre Comercial',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    rut = forms.IntegerField(
        required=True,
        label='RUT',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
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
        model = Proveedor
        fields = ['codigo', 'razon', 'nombre_comercial', 'rut', 'domicilio', 'pais',
                  'departamento', 'telefono', 'celular', 'contacto', 'email', 'formadepago',
                  'observaciones', 'activo', 'monotributista']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'domicilio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pais': forms.Select(attrs={'class': 'form-control', 'id': 'id_pais'}, choices=PAISES),
            'departamento': forms.Select(attrs={'class': 'form-control'}, choices=[('', '---------')] + DEPARTAMENTOS_URUGUAY),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'formadepago': forms.Select(attrs={'class': 'form-control'}, choices=FORMAS_PAGO),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.Select(attrs={'class': 'form-control'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
            'monotributista': forms.Select(attrs={'class': 'form-control'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
        }
        labels = {
            'codigo': 'Código',
            'razon': 'Razón Social',
            'nombre_comercial': 'Nombre Comercial',
            'rut': 'RUT',
            'domicilio': 'Domicilio',
            'pais': 'País',
            'departamento': 'Departamento',
            'telefono': 'Teléfono',
            'celular': 'Celular',
            'contacto': 'Contacto',
            'email': 'Email',
            'formadepago': 'Forma de Pago',
            'observaciones': 'Observaciones',
            'activo': 'Activo',
            'monotributista': 'Monotributista',
        }

