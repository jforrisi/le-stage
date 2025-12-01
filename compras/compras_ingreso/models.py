from django.db import models
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from configuracion.transacciones.models import Transaccion
from configuracion.proveedores.models import Proveedor
from configuracion.documentos.models import Documento
from configuracion.articulos.models import Moneda, Articulo
from configuracion.tablas.models import PlazoPago
from configuracion.disponibilidades.models import Disponibilidad


class ComprasCabezal(models.Model):
    """Cabezal de compra/factura de proveedor"""
    
    transaccion = models.CharField(
        max_length=10,
        primary_key=True,
        verbose_name='Transacción',
        help_text='Formato: YYMMXXXXXX (ej: 251100001 para noviembre 2025)',
    )
    
    id_proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='compras',
        verbose_name='Proveedor',
        db_column='id_proveedor',
    )
    
    tipo_documento = models.ForeignKey(
        Documento,
        on_delete=models.PROTECT,
        related_name='compras',
        verbose_name='Tipo de Documento',
        limit_choices_to={'codigo__in': ['facprov', 'factimp', 'movprov']},
    )
    
    serie_documento = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Serie Documento',
    )
    
    numero_documento = models.CharField(
        max_length=50,
        verbose_name='Número Documento',
    )
    
    forma_pago = models.CharField(
        max_length=20,
        choices=[('CONTADO', 'Contado'), ('CREDITO', 'Crédito')],
        verbose_name='Forma de Pago',
    )
    
    fecha_documento = models.DateField(
        verbose_name='Fecha Documento',
    )
    
    fecha_movimiento = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha Movimiento',
    )
    
    moneda = models.ForeignKey(
        Moneda,
        on_delete=models.PROTECT,
        related_name='compras',
        verbose_name='Moneda',
    )
    
    precio_iva_inc = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='NO',
        verbose_name='Precio con IVA Incluido',
        help_text='Indica si los precios están con IVA incluido o no',
    )
    
    plazo = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Plazo',
        help_text='Plazo de pago (solo para crédito). Puede ser el del proveedor, "elegir" o "VENCIMIENTO_PACTADO"',
    )
    
    fecha_vencimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha Vencimiento',
    )
    
    disponibilidad = models.ForeignKey(
        Disponibilidad,
        on_delete=models.PROTECT,
        related_name='compras_contado',
        blank=True,
        null=True,
        verbose_name='Disponibilidad',
        help_text='Solo para forma de pago contado',
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones',
    )
    
    fchhor = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha/Hora',
    )
    
    usuario = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Usuario',
    )
    
    monotributista = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='NO',
        verbose_name='Monotributista',
        help_text='Copiado del maestro del proveedor',
    )
    
    tipo_compra = models.CharField(
        max_length=20,
        choices=[('CONVENCIONAL', 'Convencional'), ('SIMPLIFICADA', 'Simplificada')],
        default='CONVENCIONAL',
        verbose_name='Tipo de Compra',
        help_text='Convencional: con líneas de productos. Simplificada: solo totales manuales',
    )
    
    sub_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Sub Total',
        help_text='Suma de sub_total de las líneas (Convencional) o valor manual (Simplificada)',
    )
    
    iva = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='IVA',
        help_text='Suma de iva de las líneas (Convencional) o valor manual (Simplificada)',
    )
    
    importe_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Importe Total',
        help_text='Suma de total de las líneas (Convencional) o valor manual (Simplificada)',
    )
    
    class Meta:
        verbose_name = 'Compra Cabezal'
        verbose_name_plural = 'Compras Cabezal'
        ordering = ['-fchhor', '-transaccion']
        db_table = 'compras_cabezal'
    
    def __str__(self):
        return f"{self.transaccion} - {self.serie_documento} -{self.numero_documento}"
    
    def save(self, *args, **kwargs):
        # Generar transacción automáticamente si no existe
        if not self.transaccion:
            now = timezone.now()
            año = str(now.year)[-2:]
            mes = str(now.month).zfill(2)
            prefijo = f"{año}{mes}"
            
            # Buscar última transacción del mes
            ultima = Transaccion.objects.filter(
                transaccion__startswith=prefijo
            ).order_by('-transaccion').first()
            
            if ultima and ultima.transaccion:
                try:
                    ultimo_num = int(ultima.transaccion[4:])
                    nuevo_num = ultimo_num + 1
                except ValueError:
                    nuevo_num = 1
            else:
                nuevo_num = 1
            
            self.transaccion = f"{prefijo}{str(nuevo_num).zfill(6)}"
        
        # Asignar tipo_documento siempre como 'facprov' (Factura Compra)
        if not self.tipo_documento_id:
            try:
                documento = Documento.objects.get(codigo='facprov')
                self.tipo_documento = documento
            except Documento.DoesNotExist:
                pass
        
        # Copiar monotributista del proveedor
        if self.id_proveedor:
            self.monotributista = self.id_proveedor.monotributista or 'NO'
            # Si el proveedor es monotributista, forzar precio_iva_inc = 'SI'
            if self.monotributista == 'SI':
                self.precio_iva_inc = 'SI'
        
        # Calcular fecha_vencimiento automáticamente si es crédito y tiene plazo definido
        if self.forma_pago == 'CREDITO' and self.plazo and self.plazo != 'VENCIMIENTO_PACTADO' and self.plazo != 'elegir':
            # Si tiene un plazo definido (del proveedor), calcular automáticamente
            try:
                forma_pago_obj = PlazoPago.objects.get(codigo=self.plazo)
                if forma_pago_obj.fin_de_mes:
                    # Fin de mes + plazo
                    from calendar import monthrange
                    ultimo_dia = monthrange(self.fecha_documento.year, self.fecha_documento.month)[1]
                    fecha_base = timezone.datetime(
                        self.fecha_documento.year,
                        self.fecha_documento.month,
                        ultimo_dia
                    ).date()
                else:
                    # Fecha documento + plazo
                    fecha_base = self.fecha_documento
                
                from datetime import timedelta
                self.fecha_vencimiento = fecha_base + timedelta(days=forma_pago_obj.plazo_en_dias)
            except PlazoPago.DoesNotExist:
                pass
        
        # Si es VENCIMIENTO_PACTADO, dejar fecha_vencimiento en NULL
        if self.plazo == 'VENCIMIENTO_PACTADO':
            self.fecha_vencimiento = None
        
        # Si es "elegir", la fecha_vencimiento la ingresa el usuario manualmente (no se calcula)
        
        super().save(*args, **kwargs)
        
        # Actualizar totales desde las líneas
        self.actualizar_totales()
    
    def actualizar_totales(self):
        """Actualiza sub_total, iva e importe_total desde las líneas"""
        lineas = self.lineas.all()
        self.sub_total = lineas.aggregate(Sum('sub_total'))['sub_total__sum'] or 0
        self.iva = lineas.aggregate(Sum('iva'))['iva__sum'] or 0
        self.importe_total = lineas.aggregate(Sum('total'))['total__sum'] or 0
        # Guardar sin llamar save() para evitar recursión
        ComprasCabezal.objects.filter(transaccion=self.transaccion).update(
            sub_total=self.sub_total,
            iva=self.iva,
            importe_total=self.importe_total
        )


class ComprasLineas(models.Model):
    """Líneas de compra/factura de proveedor"""
    
    transaccion = models.ForeignKey(
        ComprasCabezal,
        on_delete=models.CASCADE,
        related_name='lineas',
        verbose_name='Transacción',
        db_column='transaccion',
    )
    
    linea = models.IntegerField(
        verbose_name='Línea',
        help_text='Número de línea (1, 2, 3...)',
    )
    
    id_articulo = models.ForeignKey(
        Articulo,
        on_delete=models.PROTECT,
        related_name='compras_lineas',
        verbose_name='Artículo',
        db_column='id_articulo',
    )
    
    cantidad = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Cantidad',
    )
    
    precio_original = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Precio Original',
        help_text='Precio con IVA incluido si el cabezal lo indica, sino sin IVA',
    )
    
    descuento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Descuento (%)',
        help_text='Porcentaje de descuento (ej: 5 para 5%)',
    )
    
    precio_neto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Precio Neto',
        help_text='precio_original * (1 - descuento/100)',
    )
    
    sub_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Sub Total',
        help_text='Calculado según si el cabezal tiene IVA incluido o no',
    )
    
    iva = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='IVA',
        help_text='Calculado según si el cabezal tiene IVA incluido o no',
    )
    
    total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Total',
        help_text='sub_total + iva',
    )
    
    class Meta:
        verbose_name = 'Compra Línea'
        verbose_name_plural = 'Compras Líneas'
        ordering = ['transaccion', 'linea']
        unique_together = [['transaccion', 'linea']]
        db_table = 'compras_lineas'
    
    def __str__(self):
        return f"{self.transaccion.transaccion} - Línea {self.linea}"
    
    def save(self, *args, **kwargs):
        # Validar que precio_original no sea None
        if self.precio_original is None:
            self.precio_original = Decimal('0')
        
        # Calcular descuento decimal
        descuento_decimal = Decimal(str(self.descuento)) / Decimal('100') if self.descuento else Decimal('0')
        
        # Verificar si el proveedor es monotributista o el tipo de documento
        es_monotributista = self.transaccion.monotributista == 'SI'
        es_movprov = self.transaccion.tipo_documento and self.transaccion.tipo_documento.codigo == 'movprov'
        es_factimp = self.transaccion.tipo_documento and self.transaccion.tipo_documento.codigo == 'factimp'
        
        # Obtener IVA del artículo (pero si es monotributista, movprov o factimp, el IVA será 0)
        if es_monotributista or es_movprov or es_factimp:
            # Monotributista, Movimiento Proveedor o Factura Importación: no cobra IVA, siempre es 0
            iva_valor = Decimal('0')
        elif self.id_articulo and self.id_articulo.iva:
            iva_valor = Decimal(str(self.id_articulo.iva.valor))
        else:
            iva_valor = Decimal('0')
        
        # Calcular precio_neto, sub_total e iva según precio_iva_inc del cabezal
        # IMPORTANTE: Los cálculos se hacen por unidad y luego se multiplican por cantidad
        # Si es monotributista, precio_iva_inc siempre es 'SI', pero el IVA es 0
        if self.transaccion.precio_iva_inc == 'SI':
            # IVA incluido: primero dividir precio_original por (1+IVA), luego aplicar descuento
            # Orden correcto: precio_original / (1+IVA) * (1-descuento)
            if iva_valor > 0:
                # Primero quitar IVA del precio original
                precio_sin_iva = self.precio_original / (Decimal('1') + iva_valor)
                # Luego aplicar descuento
                sub_total_unitario = precio_sin_iva * (Decimal('1') - descuento_decimal)
                # Calcular IVA sobre el sub_total
                iva_unitario = sub_total_unitario * iva_valor
            else:
                # Sin IVA (monotributista, movprov, factimp o artículo sin IVA)
                # Solo aplicar descuento
                sub_total_unitario = self.precio_original * (Decimal('1') - descuento_decimal)
                iva_unitario = Decimal('0')
            
            # precio_neto es el precio después de quitar IVA y aplicar descuento
            self.precio_neto = sub_total_unitario
            
            # Multiplicar por cantidad para sub_total e iva
            self.sub_total = sub_total_unitario * self.cantidad
            self.iva = iva_unitario * self.cantidad
        else:
            # IVA no incluido: aplicar descuento directamente, luego calcular IVA
            # precio_neto = precio_original * (1 - descuento)
            precio_neto_unitario = self.precio_original * (Decimal('1') - descuento_decimal)
            self.precio_neto = precio_neto_unitario
            
            # sub_total = precio_neto (sin IVA)
            sub_total_unitario = precio_neto_unitario
            # iva = precio_neto * IVA%
            iva_unitario = precio_neto_unitario * iva_valor
            
            # Multiplicar por cantidad para sub_total e iva
            self.sub_total = sub_total_unitario * self.cantidad
            self.iva = iva_unitario * self.cantidad
        
        # Calcular total
        self.total = self.sub_total + self.iva
        
        super().save(*args, **kwargs)
        
        # Actualizar totales del cabezal
        if self.transaccion:
            self.transaccion.actualizar_totales()
    