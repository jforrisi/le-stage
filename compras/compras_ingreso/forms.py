from django import forms
from django.forms import inlineformset_factory
from decimal import Decimal
from datetime import date
from .models import ComprasCabezal, ComprasLineas
from configuracion.proveedores.models import Proveedor
from configuracion.documentos.models import Documento
from configuracion.articulos.models import Moneda, Articulo
from configuracion.tablas.models import PlazoPago
from configuracion.disponibilidades.models import Disponibilidad


class ComprasCabezalForm(forms.ModelForm):
    """Formulario para el cabezal de compra"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar tipo_documento - permitir facprov, factimp y movprov
        if 'tipo_documento' in self.fields:
            self.fields['tipo_documento'].queryset = Documento.objects.filter(
                codigo__in=['facprov', 'factimp', 'movprov']
            )
            # Si es nueva compra, establecer 'facprov' por defecto
            if not self.instance.pk:
                try:
                    doc_default = Documento.objects.get(codigo='facprov')
                    self.fields['tipo_documento'].initial = doc_default
                except Documento.DoesNotExist:
                    pass
        
        # Eliminar fecha_movimiento del formulario - se guarda automáticamente
        if 'fecha_movimiento' in self.fields:
            del self.fields['fecha_movimiento']
        
        # Establecer fecha_documento por defecto a la fecha actual si es nueva compra
        if 'fecha_documento' in self.fields and not self.instance.pk:
            self.fields['fecha_documento'].initial = date.today()
        
        # Monedas activas
        self.fields['moneda'].queryset = Moneda.objects.filter(activo='SI')
        
        # Disponibilidades activas (solo para contado)
        self.fields['disponibilidad'].queryset = Disponibilidad.objects.filter(activo='SI')
        self.fields['disponibilidad'].required = False
        
        # Configurar campos de totales según tipo de compra
        # Por defecto, los totales son readonly (se calculan desde líneas)
        self.fields['sub_total'].required = False
        self.fields['sub_total'].widget.attrs['readonly'] = True
        self.fields['iva'].required = False
        self.fields['iva'].widget.attrs['readonly'] = True
        self.fields['importe_total'].required = False
        self.fields['importe_total'].widget.attrs['readonly'] = True
        
        # Si es edición, cargar datos del proveedor
        if self.instance and self.instance.pk and self.instance.id_proveedor:
            proveedor = self.instance.id_proveedor
            # Cargar forma de pago del proveedor como opción por defecto
            if proveedor.formadepago and proveedor.formadepago != 'NO_ASIGNADA':
                try:
                    forma_pago_obj = PlazoPago.objects.get(codigo=proveedor.formadepago)
                    # Agregar opciones de plazo
                    opciones_plazo = [
                        (proveedor.formadepago, forma_pago_obj.descripcion),
                        ('elegir', 'Elegir'),
                        ('VENCIMIENTO_PACTADO', 'Vencimiento Pactado'),
                    ]
                    self.fields['plazo'].widget.choices = opciones_plazo
                except PlazoPago.DoesNotExist:
                    pass
    
    def clean(self):
        cleaned_data = super().clean()
        forma_pago = cleaned_data.get('forma_pago')
        plazo = cleaned_data.get('plazo')
        disponibilidad = cleaned_data.get('disponibilidad')
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')
        id_proveedor = cleaned_data.get('id_proveedor')
        tipo_compra = cleaned_data.get('tipo_compra', 'CONVENCIONAL')
        sub_total = cleaned_data.get('sub_total', 0)
        iva = cleaned_data.get('iva', 0)
        importe_total = cleaned_data.get('importe_total', 0)
        
        # Si el proveedor es monotributista, forzar precio_iva_inc = 'SI'
        if id_proveedor and id_proveedor.monotributista == 'SI':
            cleaned_data['precio_iva_inc'] = 'SI'
        
        # Validar disponibilidad solo si es contado
        if forma_pago == 'CONTADO' and not disponibilidad:
            raise forms.ValidationError({
                'disponibilidad': 'Debe seleccionar una disponibilidad para forma de pago contado.'
            })
        
        # Validar plazo solo si es crédito
        if forma_pago == 'CREDITO':
            if not plazo:
                raise forms.ValidationError({
                    'plazo': 'Debe seleccionar un plazo para forma de pago crédito.'
                })
            # Si es "elegir", fecha_vencimiento es obligatoria
            if plazo == 'elegir' and not fecha_vencimiento:
                raise forms.ValidationError({
                    'fecha_vencimiento': 'Debe ingresar una fecha de vencimiento cuando elige "elegir".'
                })
            # Si es VENCIMIENTO_PACTADO, fecha_vencimiento debe ser NULL (se limpia en el save del modelo)
            # No validar aquí porque se calcula automáticamente
        
        # Validaciones específicas para compra simplificada
        if tipo_compra == 'SIMPLIFICADA':
            if not sub_total or sub_total < 0:
                raise forms.ValidationError({
                    'sub_total': 'El sub total es obligatorio y debe ser mayor o igual a 0 para compras simplificadas.'
                })
            
            # Verificar si debe ser IVA = 0 (movprov o monotributista)
            tipo_documento = cleaned_data.get('tipo_documento')
            es_movprov = tipo_documento and tipo_documento.codigo == 'movprov'
            es_monotributista = id_proveedor and id_proveedor.monotributista == 'SI'
            
            if es_movprov or es_monotributista:
                # Forzar IVA = 0
                cleaned_data['iva'] = Decimal('0')
                iva = Decimal('0')
            else:
                if iva is None or iva < 0:
                    raise forms.ValidationError({
                        'iva': 'El IVA es obligatorio y debe ser mayor o igual a 0 para compras simplificadas.'
                    })
                
                # Validar que el IVA no supere el 22% del Sub Total
                if sub_total > 0:
                    iva_maximo = sub_total * Decimal('0.22')
                    if iva > iva_maximo:
                        raise forms.ValidationError({
                            'iva': f'El IVA no puede ser mayor al 22% del Sub Total. Máximo permitido: {iva_maximo:.2f}'
                        })
            
            # Calcular automáticamente importe_total = sub_total + iva
            importe_total_calculado = sub_total + iva
            cleaned_data['importe_total'] = importe_total_calculado
        
        return cleaned_data
    
    class Meta:
        model = ComprasCabezal
        fields = [
            'id_proveedor', 'tipo_documento', 'serie_documento', 'numero_documento',
            'forma_pago', 'fecha_documento', 'moneda',
            'precio_iva_inc', 'plazo', 'fecha_vencimiento', 'disponibilidad',
            'tipo_compra', 'sub_total', 'iva', 'importe_total',
            'observaciones'
        ]
        widgets = {
            'id_proveedor': forms.HiddenInput(attrs={'id': 'id_proveedor'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-control form-control-sm', 'id': 'id_tipo_documento'}),
            'serie_documento': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'forma_pago': forms.Select(attrs={'class': 'form-control form-control-sm', 'id': 'id_forma_pago'}),
            'fecha_documento': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date', 'id': 'id_fecha_documento'}),
            'moneda': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'precio_iva_inc': forms.Select(attrs={'class': 'form-control form-control-sm', 'id': 'id_precio_iva_inc'}, choices=[('SI', 'Sí'), ('NO', 'No')]),
            'plazo': forms.Select(attrs={'class': 'form-control form-control-sm', 'id': 'id_plazo'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date', 'id': 'id_fecha_vencimiento'}),
            'disponibilidad': forms.Select(attrs={'class': 'form-control form-control-sm', 'id': 'id_disponibilidad', 'style': 'width: 100%; min-width: 350px;'}),
            'tipo_compra': forms.Select(attrs={'class': 'form-control form-control-sm', 'id': 'id_tipo_compra'}),
            'sub_total': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0', 'id': 'id_sub_total'}),
            'iva': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0', 'id': 'id_iva'}),
            'importe_total': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0', 'id': 'id_importe_total'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2}),
        }
        labels = {
            'id_proveedor': 'Proveedor',
            'tipo_documento': 'Tipo de Documento',
            'serie_documento': 'Serie Documento',
            'numero_documento': 'Número Documento',
            'forma_pago': 'Forma de Pago',
            'fecha_documento': 'Fecha Documento',
            'moneda': 'Moneda',
            'precio_iva_inc': 'Precio con IVA Incluido',
            'plazo': 'Plazo',
            'fecha_vencimiento': 'Fecha Vencimiento (Predefinida)',
            'disponibilidad': 'Disponibilidad',
            'observaciones': 'Observaciones',
        }


class ComprasLineasForm(forms.ModelForm):
    """Formulario para cada línea de compra"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Artículos activos para compras
        self.fields['id_articulo'].queryset = Articulo.objects.filter(
            ACTIVO_COMPRAS='SI'
        ).select_related('iva')
        # Hacer campos opcionales inicialmente (se validarán en clean si hay datos parciales)
        # Esto permite que las líneas vacías no generen errores
        if not self.instance.pk:
            self.fields['linea'].required = False  # Se calculará automáticamente
            self.fields['id_articulo'].required = False
            self.fields['cantidad'].required = False
            self.fields['precio_original'].required = False
            self.fields['descuento'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        id_articulo = cleaned_data.get('id_articulo')
        cantidad = cleaned_data.get('cantidad')
        precio_original = cleaned_data.get('precio_original')
        
        # Si no hay artículo o cantidad, la línea está vacía y se ignorará
        if not id_articulo or not cantidad:
            # No validar campos requeridos si la línea está vacía
            # Limpiar los datos para que no se guarden
            cleaned_data.pop('id_articulo', None)
            cleaned_data.pop('cantidad', None)
            cleaned_data.pop('precio_original', None)
            return cleaned_data
        
        # Si tiene artículo y cantidad, validar que ambos estén completos
        if id_articulo and not cantidad:
            raise forms.ValidationError({'cantidad': 'La cantidad es obligatoria cuando se selecciona un artículo.'})
        if cantidad and not id_articulo:
            raise forms.ValidationError({'id_articulo': 'El artículo es obligatorio cuando se ingresa una cantidad.'})
        
        # Validar que cantidad sea mayor a 0
        if cantidad and cantidad <= 0:
            raise forms.ValidationError({'cantidad': 'La cantidad debe ser mayor a 0.'})
        
        # Validar que precio_original sea mayor o igual a 0
        if precio_original is not None and precio_original < 0:
            raise forms.ValidationError({'precio_original': 'El precio original no puede ser negativo.'})
        
        # Si tiene artículo y cantidad, precio_original es obligatorio
        if id_articulo and cantidad and (precio_original is None or precio_original == ''):
            raise forms.ValidationError({'precio_original': 'El precio original es obligatorio.'})
        
        return cleaned_data
    
    class Meta:
        model = ComprasLineas
        fields = ['linea', 'id_articulo', 'cantidad', 'precio_original', 'descuento']
        widgets = {
            'linea': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'readonly': True, 'min': 1, 'style': 'width: 50px;'}),
            'id_articulo': forms.HiddenInput(),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control form-control-sm cantidad-input', 'step': '0.01', 'min': '0.01', 'style': 'width: 80px;'}),
            'precio_original': forms.NumberInput(attrs={'class': 'form-control form-control-sm precio-original-input', 'step': '0.01', 'min': '0', 'style': 'width: 100px;'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control form-control-sm descuento-input', 'step': '0.01', 'min': '0', 'max': '100', 'style': 'width: 70px;'}),
        }
        labels = {
            'linea': 'Línea',
            'id_articulo': 'Artículo',
            'cantidad': 'Cantidad',
            'precio_original': 'Precio Original',
            'descuento': 'Descuento (%)',
        }


# Formset para manejar múltiples líneas
class ComprasLineasFormSetBase(inlineformset_factory(
    ComprasCabezal,
    ComprasLineas,
    form=ComprasLineasForm,
    extra=1,  # Una línea por defecto
    can_delete=True,
    min_num=0,  # Permitir 0 líneas inicialmente (se validará en clean)
    validate_min=False,  # Validar manualmente en clean
)):
    """Formset personalizado para líneas de compra"""
    
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
                precio_original = form.cleaned_data.get('precio_original')
                # Contar solo líneas completas con todos los datos requeridos
                if id_articulo and cantidad and cantidad > 0 and precio_original is not None and precio_original >= 0:
                    lineas_validas += 1
        
        if lineas_validas == 0:
            raise forms.ValidationError('Debe agregar al menos una línea con artículo, cantidad y precio válidos.')

ComprasLineasFormSet = ComprasLineasFormSetBase


