from django.db import models
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from configuracion.transacciones.models import Transaccion
from configuracion.proveedores.models import Proveedor
from configuracion.documentos.models import Documento
from configuracion.articulos.models import Moneda, Articulo
from configuracion.tablas.models import FormaPagoTipo
from configuracion.disponibilidades.models import Disponibilidad



class ComprasDevolucionesCabezal(models.Model):
    """Cabezal de devolución de compra/nota de crédito"""
    
    transaccion = models.CharField(
        max_length=10,
        primary_key=True,
        verbose_name='Transacción',
        help_text='Formato: YYMMXXXXXX (ej: 251100001 para noviembre 2025)',
    )
    
    id_proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='devoluciones',
        verbose_name='Proveedor',
        db_column='id_proveedor',
    )
    
    tipo_documento = models.ForeignKey(
        Documento,
        on_delete=models.PROTECT,
        related_name='devoluciones',
        verbose_name='Tipo de Documento',
        limit_choices_to={'codigo__in': ['ncimpo', 'ncprov' ,'devmovprov']},
    )
    
    serie_documento = models.CharField(
        max_length=5,
        null=True,
        verbose_name='Serie Documento',
    )
    
    numero_documento = models.CharField(
        max_length=20,
        verbose_name='Número Documento',
    )
    
    forma_pago = models.ForeignKey(
        FormaPagoTipo,
        on_delete=models.PROTECT,
        related_name='devoluciones',
        verbose_name='Forma de Pago',
        db_column='forma_pago',
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
        related_name='devoluciones',
        verbose_name='Moneda',
    )
    
    precio_iva_inc = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='NO',
        verbose_name='Precio con IVA Incluido',
        help_text='Indica si los precios están con IVA incluido o no',
    )    
    
    tipo_compra = models.CharField(
        max_length=20,
        choices=[('CONVENCIONAL', 'Convencional'), ('SIMPLIFICADA', 'Simplificada')],
        default='CONVENCIONAL',
        verbose_name='Tipo de Compra',
        help_text='Convencional: con líneas de productos. Simplificada: solo totales manuales',
    )
    
    disponibilidad = models.ForeignKey(
        Disponibilidad,
        on_delete=models.PROTECT,
        related_name='devoluciones_contado',
        blank=True,
        null=True,
        verbose_name='Disponibilidad',
        help_text='Solo para devoluciones de facturas contado',
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones',
    )

    monotributista = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='NO',
        verbose_name='Monotributista',
        help_text='Copiado del maestro del proveedor',
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
    
    sub_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Sub Total',
        help_text='Suma de sub_total de las líneas',
    )

    iva = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='IVA',
        help_text='Suma de iva de las líneas',
    )
    
    importe_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Importe Total',
        help_text='Suma de total de las líneas',
    )
    
    
    class Meta:
        verbose_name = 'Devolución Compra Cabezal'
        verbose_name_plural = 'Devoluciones Compra Cabezal'
        ordering = ['-fchhor', '-transaccion']
        db_table = 'compras_devoluciones_cabezal'
    
    def __str__(self):
        return f"{self.transaccion} - {self.serie_documento} - {self.numero_documento}"
    
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
        
        # Asignar tipo_documento por defecto como 'ncprov' si no está definido
        if not self.tipo_documento_id:
            try:
                documento = Documento.objects.get(codigo='ncprov')
                self.tipo_documento = documento
            except Documento.DoesNotExist:
                pass
        
        # Copiar monotributista del proveedor
        if self.id_proveedor:
            self.monotributista = self.id_proveedor.monotributista or 'NO'
            # Si el proveedor es monotributista, forzar precio_iva_inc = 'SI'
            if self.monotributista == 'SI':
                self.precio_iva_inc = 'SI'
        
        # Validar disponibilidad según forma_pago
        if self.forma_pago and self.forma_pago.nombre == 'Contado':
            # Si es contado, debe tener disponibilidad
            if not self.disponibilidad_id:
                raise ValueError('Las devoluciones de contado deben tener una disponibilidad asignada.')
        elif self.forma_pago and self.forma_pago.nombre == 'Crédito':
            # Si es crédito, no debe tener disponibilidad
            if self.disponibilidad_id:
                self.disponibilidad = None
        
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
        ComprasDevolucionesCabezal.objects.filter(transaccion=self.transaccion).update(
            sub_total=self.sub_total,
            iva=self.iva,
            importe_total=self.importe_total
        )


class ComprasDevolucionesLineas(models.Model):
    """Líneas de compra/factura de proveedor"""
    
    transaccion = models.ForeignKey(
        ComprasDevolucionesCabezal,
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
        related_name='devoluciones_lineas',
        verbose_name='Artículo',
        db_column='id_articulo',
    )
    
    # Referencia a la línea de compra afectada (opcional)
    id_compra_linea = models.ForeignKey(
        'compras_ingreso.ComprasLineas',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='devoluciones',
        verbose_name='Línea de Compra',
        help_text='Línea específica de la factura de compra afectada (opcional)',
    )
    
    # Campos de display (se calculan desde id_compra_linea, pero se guardan para referencia)
    serie_doc_afectado = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Serie Doc Afectado',
        help_text='Serie del documento de compra afectado (calculado desde id_compra_linea)',
    )
    
    numero_doc_afectado = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Número Doc Afectado',
        help_text='Número del documento de compra afectado (calculado desde id_compra_linea)',
    )
    
    cantidad = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Cantidad',
    )
    
    precio = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Precio Original',
        help_text='Precio con IVA incluido si el cabezal lo indica, sino sin IVA',
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
        db_table = 'compras_devoluciones_lineas'
    
    def __str__(self):
        return f"{self.transaccion.transaccion} - Línea {self.linea}"
    
    def save(self, *args, **kwargs):
        # Si hay id_compra_linea, calcular serie y numero desde la factura
        if self.id_compra_linea:
            compra = self.id_compra_linea.transaccion
            self.serie_doc_afectado = compra.serie_documento or ''
            self.numero_doc_afectado = compra.numero_documento or ''
            
            # Si hay id_compra_linea, usar su precio_neto como precio inicial
            if not self.precio or self.precio == 0:
                self.precio = self.id_compra_linea.precio_neto
        else:
            # Si no hay id_compra_linea, limpiar campos de documento afectado
            self.serie_doc_afectado = ''
            self.numero_doc_afectado = ''
        
        # Validar que precio no sea None
        if self.precio is None:
            self.precio = Decimal('0')
        
        # Variable local para trabajar con el precio
        precio = self.precio

        # Verificar si el proveedor es monotributista o si es devolución movimiento proveedor (devmovprov)
        es_monotributista = self.transaccion.monotributista == 'SI'
        es_movprov = self.transaccion.tipo_documento and self.transaccion.tipo_documento.codigo == 'devmovprov'
        
        # Obtener IVA del artículo (pero si es monotributista o movprov, el IVA será 0)
        if es_monotributista or es_movprov:
            # Monotributista o Movimiento Proveedor: no cobra IVA, siempre es 0
            iva_valor = Decimal('0')
        elif self.id_articulo and self.id_articulo.iva:
            iva_valor = Decimal(str(self.id_articulo.iva.valor))
        else:
            iva_valor = Decimal('0')
        
        # Calcular sub_total e iva según precio_iva_inc del cabezal
        # IMPORTANTE: Los cálculos se hacen por unidad y luego se multiplican por cantidad
        # Si es monotributista, precio_iva_inc siempre es 'SI', pero el IVA es 0
        if self.transaccion.precio_iva_inc == 'SI':
            # IVA incluido: precio_neto_unitario ya incluye IVA, hay que desglosarlo
            # precio_neto_unitario = sub_total_unitario + iva_unitario = sub_total_unitario * (1 + iva)
            # sub_total_unitario = precio_neto_unitario / (1 + iva)
            # iva_unitario = precio_neto_unitario - sub_total_unitario
            # Si es monotributista, iva_valor = 0, entonces sub_total = precio_neto y iva = 0
            if iva_valor > 0:
                sub_total_unitario = precio / (Decimal('1') + iva_valor)
                iva_unitario = precio - sub_total_unitario
            else:
                # Sin IVA (monotributista o artículo sin IVA)
                sub_total_unitario = precio
                iva_unitario = Decimal('0')
            
            # Multiplicar por cantidad para sub_total e iva
            self.sub_total = sub_total_unitario * self.cantidad
            self.iva = iva_unitario * self.cantidad
        else:
            # IVA no incluido: precio_neto_unitario es la base, hay que sumarle IVA
            # Si es monotributista, iva_valor = 0, entonces sub_total = precio_neto y iva = 0
            sub_total_unitario = precio
            iva_unitario = precio * iva_valor
            
            # Multiplicar por cantidad para sub_total e iva
            self.sub_total = sub_total_unitario * self.cantidad
            self.iva = iva_unitario * self.cantidad
        
        # Calcular total
        self.total = self.sub_total + self.iva
        
        super().save(*args, **kwargs)
        
        # Actualizar totales del cabezal
        if self.transaccion:
            self.transaccion.actualizar_totales()