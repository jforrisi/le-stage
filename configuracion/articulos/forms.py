from django import forms
from .models import TipoArticulo, Familia, SubFamilia, Articulo, CodigoProveedorCompra
from configuracion.proveedores.models import Proveedor


class TipoArticuloForm(forms.ModelForm):
    """Formulario para crear y editar tipos de artículo"""
    
    codigo = forms.CharField(
        max_length=3,
        required=True,
        label='Código',
        help_text='3 letras representativas (ej: SER, INS, PRO)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'style': 'text-transform:uppercase',
            'maxlength': '3',
            'pattern': '[A-Z]{3}',
            'title': 'Debe ser exactamente 3 letras mayúsculas'
        })
    )
    
    class Meta:
        model = TipoArticulo
        fields = ['codigo', 'nombre', 'stockeable', 'se_compra', 'loteable']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'stockeable': forms.Select(attrs={'class': 'form-control'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
            'se_compra': forms.Select(attrs={'class': 'form-control'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
            'loteable': forms.Select(attrs={'class': 'form-control'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
        }
        labels = {
            'codigo': 'Código',
            'nombre': 'Nombre',
            'stockeable': 'Stockeable',
            'se_compra': 'Se Compra',
            'loteable': 'Loteable',
        }
    
    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo', '').upper().strip()
        if len(codigo) != 3:
            raise forms.ValidationError('El código debe tener exactamente 3 letras.')
        if not codigo.isalpha():
            raise forms.ValidationError('El código debe contener solo letras.')
        return codigo


class FamiliaForm(forms.ModelForm):
    """Formulario para crear y editar familias"""
    
    class Meta:
        model = Familia
        fields = ['codigo', 'nombre', 'observaciones']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'codigo': 'Código',
            'nombre': 'Nombre',
            'observaciones': 'Observaciones',
        }


class SubFamiliaForm(forms.ModelForm):
    """Formulario para crear y editar subfamilias"""
    
    class Meta:
        model = SubFamilia
        fields = ['codigo', 'familia', 'nombre', 'observaciones']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'familia': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'codigo': 'Código',
            'familia': 'Familia',
            'nombre': 'Nombre',
            'observaciones': 'Observaciones',
        }


class CodigoProveedorForm(forms.ModelForm):
    """Formulario para códigos de proveedor"""
    
    class Meta:
        model = CodigoProveedorCompra
        fields = ['proveedor', 'codigo_proveedor']
        widgets = {
            'proveedor': forms.Select(attrs={'class': 'form-control proveedor-select'}),
            'codigo_proveedor': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'proveedor': 'Proveedor',
            'codigo_proveedor': 'Código Proveedor',
        }


class ArticuloForm(forms.ModelForm):
    """Formulario para crear y editar artículos"""
    
    nombre = forms.CharField(
        required=True,
        max_length=200,
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    tipo_articulo = forms.ModelChoiceField(
        queryset=TipoArticulo.objects.all(),
        required=True,
        label='Tipo de Artículo',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo monedas activas
        from .models import Moneda, IVA
        self.fields['moneda_venta'] = forms.ModelChoiceField(
            queryset=Moneda.objects.filter(activo='SI'),
            required=True,
            label='Moneda de Venta',
            widget=forms.Select(attrs={'class': 'form-control'})
        )
        # Filtrar solo IVAs activos
        self.fields['iva'] = forms.ModelChoiceField(
            queryset=IVA.objects.filter(activo='SI'),
            required=False,
            label='IVA',
            widget=forms.Select(attrs={'class': 'form-control'}),
            empty_label='Seleccione un IVA...'
        )
    
    class Meta:
        model = Articulo
        fields = [
            'producto_id', 'nombre', 'tipo_articulo', 'idsubfamilia',
            'precio_venta', 'moneda_venta', 'UNIDAD_VENTA', 'UNIDAD_STOCK',
            'UNIDAD_COMPRA', 'ACTIVO_COMERCIAL', 'ACTIVO_STOCK', 'ACTIVO_COMPRAS',
            'ACTIVO_PRODUCCION', 'LOTEABLE', 'UNIDAD_PESO', 'PESO',
            'UNIDAD_VOLUMEN', 'VOLUMEN', 'iva', 'observaciones'
        ]
        widgets = {
            'producto_id': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_articulo': forms.Select(attrs={'class': 'form-control'}),
            'idsubfamilia': forms.Select(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'moneda_venta': forms.Select(attrs={'class': 'form-control'}),
            'UNIDAD_VENTA': forms.Select(attrs={'class': 'form-control'}),
            'UNIDAD_STOCK': forms.Select(attrs={'class': 'form-control'}),
            'UNIDAD_COMPRA': forms.Select(attrs={'class': 'form-control'}),
            'ACTIVO_COMERCIAL': forms.Select(attrs={'class': 'form-control'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
            'ACTIVO_STOCK': forms.Select(attrs={'class': 'form-control'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
            'ACTIVO_COMPRAS': forms.Select(attrs={'class': 'form-control'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
            'ACTIVO_PRODUCCION': forms.Select(attrs={'class': 'form-control'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
            'LOTEABLE': forms.Select(attrs={'class': 'form-control'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
            'UNIDAD_PESO': forms.Select(attrs={'class': 'form-control'}),
            'PESO': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'UNIDAD_VOLUMEN': forms.Select(attrs={'class': 'form-control'}),
            'VOLUMEN': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'iva': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'producto_id': 'ID Producto',
            'nombre': 'Nombre',
            'tipo_articulo': 'Tipo de Artículo',
            'idsubfamilia': 'Sub Familia',
            'precio_venta': 'Precio de Venta',
            'moneda_venta': 'Moneda de Venta',
            'UNIDAD_VENTA': 'Unidad de Venta',
            'UNIDAD_STOCK': 'Unidad de Stock',
            'UNIDAD_COMPRA': 'Unidad de Compra',
            'ACTIVO_COMERCIAL': 'Activo Comercial',
            'ACTIVO_STOCK': 'Activo Stock',
            'ACTIVO_COMPRAS': 'Activo Compras',
            'ACTIVO_PRODUCCION': 'Activo Producción',
            'LOTEABLE': 'Loteable',
            'UNIDAD_PESO': 'Unidad de Peso',
            'PESO': 'Peso',
            'UNIDAD_VOLUMEN': 'Unidad de Volumen',
            'VOLUMEN': 'Volumen',
            'iva': 'IVA',
            'observaciones': 'Observaciones',
        }
