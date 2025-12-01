from django import forms
from django.forms import inlineformset_factory
from decimal import Decimal
from datetime import date
from .models import VentasDevolucionesCabezal, VentasDevolucionesLineas
from configuracion.clientes.models import Cliente
from configuracion.documentos.models import Documento
from configuracion.articulos.models import Moneda, Articulo
from configuracion.tablas.models import FormaPagoTipo
from configuracion.disponibilidades.models import Disponibilidad


class VentasDevolucionesCabezalForm(forms.ModelForm):
    """Formulario para el cabezal de devolución de venta"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar tipo_documento - permitir devmovcli, tncredit y ncreexpo
        if 'tipo_documento' in self.fields:
            self.fields['tipo_documento'].queryset = Documento.objects.filter(
                codigo__in=['devmovcli', 'tncredit', 'ncreexpo']
            )
            # Si es nueva devolución, establecer 'devmovcli' por defecto
            if not self.instance.pk:
                try:
                    doc_default = Documento.objects.get(codigo='devmovcli')
                    self.fields['tipo_documento'].initial = doc_default
                except Documento.DoesNotExist:
                    pass
        
        # Eliminar fecha_movimiento del formulario - se guarda automáticamente
        if 'fecha_movimiento' in self.fields:
            del self.fields['fecha_movimiento']
        
        # Establecer fecha_documento por defecto a la fecha actual si es nueva devolución
        if 'fecha_documento' in self.fields and not self.instance.pk:
            self.fields['fecha_documento'].initial = date.today()
        
        # Monedas activas
        self.fields['moneda'].queryset = Moneda.objects.filter(activo='SI')
        
        # Formas de pago activas
        if 'forma_pago' in self.fields:
            self.fields['forma_pago'].queryset = FormaPagoTipo.objects.filter(activo='SI')
        
        # Disponibilidades activas (solo para contado)
        self.fields['disponibilidad'].queryset = Disponibilidad.objects.filter(activo='SI')
        self.fields['disponibilidad'].required = False
        
        # En devoluciones de ventas, precio_iva_inc siempre es 'SI' (no editable)
        if 'precio_iva_inc' in self.fields:
            self.fields['precio_iva_inc'].initial = 'SI'
            self.fields['precio_iva_inc'].required = False  # No requerido porque siempre se fuerza a 'SI'
            self.fields['precio_iva_inc'].widget.attrs['disabled'] = True
            self.fields['precio_iva_inc'].widget.attrs['readonly'] = True
        
        # Establecer tipo_venta siempre a CONVENCIONAL y ocultarlo
        if 'tipo_venta' in self.fields:
            self.fields['tipo_venta'].initial = 'CONVENCIONAL'
            # Ocultar el campo
            self.fields['tipo_venta'].widget = forms.HiddenInput()
        
        # Configurar campos de totales según tipo de venta
        # Por defecto, los totales son readonly (se calculan desde líneas)
        self.fields['sub_total'].required = False
        self.fields['sub_total'].widget.attrs['readonly'] = True
        self.fields['iva'].required = False
        self.fields['iva'].widget.attrs['readonly'] = True
        self.fields['importe_total'].required = False
        self.fields['importe_total'].widget.attrs['readonly'] = True
        
    
    def clean(self):
        cleaned_data = super().clean()
        
        # En devoluciones de ventas, precio_iva_inc siempre es 'SI'
        cleaned_data['precio_iva_inc'] = 'SI'
        
        forma_pago = cleaned_data.get('forma_pago')
        disponibilidad = cleaned_data.get('disponibilidad')
        id_cliente = cleaned_data.get('id_cliente')
        sub_total = cleaned_data.get('sub_total', 0)
        iva = cleaned_data.get('iva', 0)
        importe_total = cleaned_data.get('importe_total', 0)
        
        # Forzar tipo_venta siempre a CONVENCIONAL
        cleaned_data['tipo_venta'] = 'CONVENCIONAL'
        
        # Validar disponibilidad solo si es contado
        if forma_pago and forma_pago.nombre == 'Contado' and not disponibilidad:
            raise forms.ValidationError({
                'disponibilidad': 'Debe seleccionar una disponibilidad para forma de pago contado.'
            })
        
        return cleaned_data
    
    class Meta:
        model = VentasDevolucionesCabezal
        fields = [ 'id_cliente', 'tipo_documento',
                    'serie_documento', 'numero_documento', 'forma_pago',
                    'fecha_documento', 'moneda',
                     'precio_iva_inc', 'tipo_venta', 'disponibilidad',
                    'observaciones', 'sub_total', 'iva', 'importe_total']
        
        widgets = {
            'id_cliente': forms.HiddenInput(attrs={'id': 'id_cliente'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-control form-control-sm', 'id': 'id_tipo_documento'}),
            'serie_documento': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'forma_pago': forms.Select(attrs={'class': 'form-control form-control-sm', 'id': 'id_forma_pago'}),
            'fecha_documento': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date', 'id': 'id_fecha_documento'}),
            'moneda': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'precio_iva_inc': forms.Select(attrs={'class': 'form-control form-control-sm', 'id': 'id_precio_iva_inc'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
            'disponibilidad': forms.Select(attrs={'class': 'form-control form-control-sm', 'id': 'id_disponibilidad', 'style': 'width: 100%; min-width: 350px;'}),
            'tipo_venta': forms.Select(attrs={'class': 'form-control form-control-sm', 'id': 'id_tipo_venta'}),
            'sub_total': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0', 'id': 'id_sub_total'}),
            'iva': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0', 'id': 'id_iva'}),
            'importe_total': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0', 'id': 'id_importe_total'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2}),
        }
        labels = {
            'id_cliente': 'Cliente',
            'tipo_documento': 'Tipo de Documento',
            'serie_documento': 'Serie Documento',
            'numero_documento': 'Número Documento',
            'forma_pago': 'Forma de Pago',
            'fecha_documento': 'Fecha Documento',
            'moneda': 'Moneda',
            'precio_iva_inc': 'Precio con IVA Incluido',
            'disponibilidad': 'Disponibilidad',
            'observaciones': 'Observaciones',
             'tipo_venta': 'Tipo de venta', 
             'sub_total': 'Sub total', 
             'iva':'IVA' , 
             'importe_total': 'Total'
        }

class VentasDevolucionesLineasForm(forms.ModelForm):
    """Formulario para cada línea de devolución de venta"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Artículos activos para ventas (ACTIVO_COMERCIAL)
        self.fields['id_articulo'].queryset = Articulo.objects.filter(
            ACTIVO_COMERCIAL='SI'
        ).select_related('iva')
        # Hacer campos opcionales inicialmente (se validarán en clean si hay datos parciales)
        # Esto permite que las líneas vacías no generen errores
        if not self.instance.pk:
            self.fields['linea'].required = False  # Se calculará automáticamente
            self.fields['id_articulo'].required = False
            self.fields['cantidad'].required = False
            self.fields['precio'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        id_articulo = cleaned_data.get('id_articulo')
        cantidad = cleaned_data.get('cantidad')
        precio = cleaned_data.get('precio')
        
        # Si no hay artículo o cantidad, la línea está vacía y se ignorará
        if not id_articulo or not cantidad:
            # No validar campos requeridos si la línea está vacía
            # Limpiar los datos para que no se guarden
            cleaned_data.pop('id_articulo', None)
            cleaned_data.pop('cantidad', None)
            cleaned_data.pop('precio', None)
            return cleaned_data
        
        # Si tiene artículo y cantidad, validar que ambos estén completos
        if id_articulo and not cantidad:
            raise forms.ValidationError({'cantidad': 'La cantidad es obligatoria cuando se selecciona un artículo.'})
        if cantidad and not id_articulo:
            raise forms.ValidationError({'id_articulo': 'El artículo es obligatorio cuando se ingresa una cantidad.'})
        
        # Validar que cantidad sea mayor a 0
        if cantidad and cantidad <= 0:
            raise forms.ValidationError({'cantidad': 'La cantidad debe ser mayor a 0.'})
        
        # Validar que precio sea mayor o igual a 0
        if precio is not None and precio < 0:
            raise forms.ValidationError({'precio': 'El precio no puede ser negativo.'})
        
        # Si tiene artículo y cantidad, precio es obligatorio
        if id_articulo and cantidad and (precio is None or precio == ''):
            raise forms.ValidationError({'precio': 'El precio es obligatorio.'})
        
        return cleaned_data
    
    class Meta:
        model = VentasDevolucionesLineas
        fields = ['linea', 'id_articulo', 'id_venta_linea', 'serie_doc_afectado', 'numero_doc_afectado', 'cantidad', 'precio']
        widgets = {
            'linea': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'readonly': True, 'min': 1, 'style': 'width: 50px;'}),
            'id_articulo': forms.HiddenInput(attrs={'id': 'id_articulo', 'class': 'articulo-hidden',}),
            'id_venta_linea': forms.HiddenInput(attrs={'id': 'id_venta_linea', 'class': 'id-linea-venta-hidden',}),
            'serie_doc_afectado': forms.HiddenInput(attrs={'id': 'serie_doc_afectado',}),
            'numero_doc_afectado': forms.HiddenInput(attrs={'id': 'numero_doc_afectado',}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control form-control-sm cantidad-input', 'step': '0.01', 'min': '0.01', 'style': 'width: 80px;'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control form-control-sm precio-input', 'step': '0.01', 'min': '0', 'style': 'width: 100px;'}),
        }
        labels = {
            'linea': 'Línea',
            'id_articulo': 'Artículo',
            'id_venta_linea': 'ID de Línea de Venta',
            'cantidad': 'Cantidad',
            'precio': 'Precio',
        }


# Formset para manejar múltiples líneas
class VentasDevolucionesLineasFormSetBase(inlineformset_factory(
    VentasDevolucionesCabezal,
    VentasDevolucionesLineas,
    form=VentasDevolucionesLineasForm,
    extra=1,  # Una línea por defecto
    can_delete=True,
    min_num=0,  # Permitir 0 líneas inicialmente (se validará en clean)
    validate_min=False,  # Validar manualmente en clean
)):
    """Formset personalizado para líneas de devolución de venta"""
    
    def clean(self):
        """Validar que haya al menos una línea con datos completos"""
        # Si hay errores en formularios individuales, no continuar
        if any(self.errors):
            return
        
        # Contar líneas con datos válidos completos (ignorar líneas marcadas para eliminar)
        lineas_validas = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                id_articulo = form.cleaned_data.get('id_articulo')
                cantidad = form.cleaned_data.get('cantidad')
                precio = form.cleaned_data.get('precio')
                # Contar solo líneas completas con todos los datos requeridos
                if id_articulo and cantidad and cantidad > 0 and precio is not None and precio >= 0:
                    lineas_validas += 1
        
        if lineas_validas == 0:
            raise forms.ValidationError('Debe agregar al menos una línea con artículo, cantidad y precio válidos.')

VentasDevolucionesLineasFormSet = VentasDevolucionesLineasFormSetBase

