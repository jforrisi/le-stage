from django.db import models
from configuracion.proveedores.models import Proveedor


# Unidades de medida
UNIDADES_MEDIDA = [
    ('BIDON', 'Bidón'),
    ('BOLSA', 'Bolsa'),
    ('CAJA', 'Caja'),
    ('FRASCO', 'Frasco'),
    ('GRAMOS', 'Gramos'),
    ('HECTAREAS', 'Hectáreas'),
    ('HORAS', 'Horas'),
    ('KILOMETROS', 'Kilómetros'),
    ('KILOS', 'Kilos'),
    ('LITROS', 'Litros'),
    ('METROS', 'Metros'),
    ('METROS_CUADRADOS', 'Metros cuadrados'),
    ('METROS_CUBICOS', 'Metros cúbicos'),
    ('TONELADAS', 'Toneladas'),
    ('UNITARIO', 'Unitario'),
]

# Monedas - Mantener para compatibilidad temporal
MONEDAS = [
    ('UYU', 'Peso Uruguayo'),
    ('USD', 'Dólar Estadounidense'),
    ('EUR', 'Euro'),
]


class Moneda(models.Model):
    """Modelo para representar las monedas"""
    codigo = models.CharField(
        max_length=3,
        unique=True,
        primary_key=True,
        verbose_name='Código',
        help_text='Código de 3 letras (ej: UYU, USD, EUR)'
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Nombre completo de la moneda'
    )
    activo = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='SI',
        verbose_name='Activo',
        help_text='Si la moneda está activa o no'
    )

    class Meta:
        verbose_name = 'Moneda'
        verbose_name_plural = 'Monedas'
        ordering = ['codigo']
        db_table = 'config_moneda'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class TipoArticulo(models.Model):
    """Modelo para representar el tipo de artículo"""
    codigo = models.CharField(
        max_length=3,
        unique=True,
        primary_key=True,
        verbose_name='Código',
        help_text='3 letras representativas (ej: SER, INS, PRO)'
    )
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    stockeable = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='NO',
        verbose_name='Stockeable',
        help_text='Si computa stock o no'
    )
    se_compra = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='SI',
        verbose_name='Se Compra',
        help_text='Si se puede comprar este tipo de artículo'
    )
    loteable = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='NO',
        verbose_name='Loteable',
        help_text='Si este tipo de artículo puede tener lotes'
    )
    
    class Meta:
        verbose_name = 'Tipo de Artículo'
        verbose_name_plural = 'Tipos de Artículo'
        ordering = ['codigo']
        db_table = 'config_articulos_tipoarticulo'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class IVA(models.Model):
    """Tabla de tipos de IVA para Uruguay"""
    codigo = models.CharField(
        max_length=10,
        unique=True,
        primary_key=True,
        verbose_name='Código',
        help_text='Código interno del IVA (ej: iva_b, iva_m, exento)'
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Nombre del IVA (ej: IVA Básico, IVA Mínimo, Exento)'
    )
    valor = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        verbose_name='Valor',
        help_text='Valor como proporción (ej: 0.22 para 22%)'
    )
    activo = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='SI',
        verbose_name='Activo',
        help_text='Si la tasa de IVA está activa o no'
    )

    class Meta:
        verbose_name = 'IVA'
        verbose_name_plural = 'IVAs'
        ordering = ['codigo']
        db_table = 'config_iva'

    def __str__(self):
        return f"{self.nombre} ({int(self.valor * 100)}%)"


class Familia(models.Model):
    """Modelo para representar una familia de artículos"""
    codigo = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Código',
        help_text='Formato: FAM001'
    )
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    
    class Meta:
        verbose_name = 'Familia'
        verbose_name_plural = 'Familias'
        ordering = ['codigo']
        db_table = 'config_articulos_familia'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}" if self.codigo else self.nombre
    
    def save(self, *args, **kwargs):
        # Generar código automáticamente si no existe
        if not self.codigo:
            ultima_familia = Familia.objects.order_by('-id').first()
            if ultima_familia and ultima_familia.codigo:
                try:
                    # Extraer el número del último código (ej: FAM001 -> 1)
                    ultimo_num = int(ultima_familia.codigo.replace('FAM', ''))
                    nuevo_num = ultimo_num + 1
                except:
                    nuevo_num = 1
            else:
                nuevo_num = 1
            
            # Formatear con ceros a la izquierda (FAM001, FAM002, etc.)
            self.codigo = f"FAM{str(nuevo_num).zfill(3)}"
        
        super().save(*args, **kwargs)


class SubFamilia(models.Model):
    """Modelo para representar una subfamilia de artículos"""
    codigo = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Código',
        help_text='Formato: SUBFAM001'
    )
    familia = models.ForeignKey(
        Familia,
        on_delete=models.CASCADE,
        related_name='subfamilias',
        verbose_name='Familia'
    )
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    
    class Meta:
        verbose_name = 'Sub Familia'
        verbose_name_plural = 'Sub Familias'
        ordering = ['codigo']
        unique_together = ['familia', 'nombre']
        db_table = 'config_articulos_subfamilia'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}" if self.codigo else f"{self.familia.nombre} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        # Generar código automáticamente si no existe
        if not self.codigo:
            ultima_subfamilia = SubFamilia.objects.order_by('-id').first()
            if ultima_subfamilia and ultima_subfamilia.codigo:
                try:
                    # Extraer el número del último código (ej: SUBFAM001 -> 1)
                    ultimo_num = int(ultima_subfamilia.codigo.replace('SUBFAM', ''))
                    nuevo_num = ultimo_num + 1
                except:
                    nuevo_num = 1
            else:
                nuevo_num = 1
            
            # Formatear con ceros a la izquierda (SUBFAM001, SUBFAM002, etc.)
            self.codigo = f"SUBFAM{str(nuevo_num).zfill(3)}"
        
        super().save(*args, **kwargs)


class Articulo(models.Model):
    """Modelo para representar un artículo/producto en el ERP"""
    producto_id = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        verbose_name='ID Producto',
        help_text='Formato: XXX000001 (3 letras del tipo + 6 números)'
    )
    nombre = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nombre')
    tipo_articulo = models.ForeignKey(
        TipoArticulo,
        on_delete=models.PROTECT,
        related_name='articulos',
        null=True,
        blank=True,
        verbose_name='Tipo de Artículo'
    )
    idsubfamilia = models.ForeignKey(
        SubFamilia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articulos',
        verbose_name='Sub Familia'
    )
    precio_venta = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Precio de Venta'
    )
    moneda_venta = models.ForeignKey(
        Moneda,
        on_delete=models.PROTECT,
        related_name='articulos',
        null=True,  # Temporalmente nullable para migración
        blank=True,  # Temporalmente blank para migración
        verbose_name='Moneda de Venta'
    )
    UNIDAD_VENTA = models.CharField(
        max_length=20,
        choices=UNIDADES_MEDIDA,
        default='UNITARIO',
        verbose_name='Unidad de Venta'
    )
    UNIDAD_STOCK = models.CharField(
        max_length=20,
        choices=UNIDADES_MEDIDA,
        default='UNITARIO',
        verbose_name='Unidad de Stock'
    )
    UNIDAD_COMPRA = models.CharField(
        max_length=20,
        choices=UNIDADES_MEDIDA,
        default='UNITARIO',
        verbose_name='Unidad de Compra'
    )
    ACTIVO_COMERCIAL = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='SI',
        verbose_name='Activo Comercial'
    )
    ACTIVO_STOCK = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='SI',
        verbose_name='Activo Stock'
    )
    ACTIVO_COMPRAS = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='SI',
        verbose_name='Activo Compras'
    )
    ACTIVO_PRODUCCION = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='NO',
        verbose_name='Activo Producción'
    )
    LOTEABLE = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='NO',
        verbose_name='Loteable'
    )
    UNIDAD_PESO = models.CharField(
        max_length=20,
        choices=UNIDADES_MEDIDA,
        blank=True,
        null=True,
        verbose_name='Unidad de Peso'
    )
    PESO = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        blank=True,
        null=True,
        verbose_name='Peso'
    )
    UNIDAD_VOLUMEN = models.CharField(
        max_length=20,
        choices=UNIDADES_MEDIDA,
        blank=True,
        null=True,
        verbose_name='Unidad de Volumen'
    )
    VOLUMEN = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        blank=True,
        null=True,
        verbose_name='Volumen'
    )
    iva = models.ForeignKey(
        'IVA',
        on_delete=models.PROTECT,
        related_name='articulos',
        null=True,
        blank=True,
        verbose_name='IVA'
    )
    fchhor = models.DateTimeField(auto_now=True, verbose_name='Fecha/Hora')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    
    class Meta:
        verbose_name = 'Artículo'
        verbose_name_plural = 'Artículos'
        ordering = ['producto_id']
        db_table = 'config_articulos_maestro'
    
    def __str__(self):
        return f"{self.producto_id} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        # Generar producto_id automáticamente si no existe
        if not self.producto_id and self.tipo_articulo:
            # Obtener el último número correlativo para este tipo
            ultimo_articulo = Articulo.objects.filter(
                tipo_articulo=self.tipo_articulo
            ).order_by('-id').first()
            
            if ultimo_articulo and ultimo_articulo.producto_id:
                try:
                    # Extraer el número del último código (ej: SER000001 -> 1)
                    ultimo_num = int(ultimo_articulo.producto_id[3:])
                    nuevo_num = ultimo_num + 1
                except:
                    nuevo_num = 1
            else:
                nuevo_num = 1
            
            # Formatear con ceros a la izquierda (SER000001, INS000001, etc.)
            codigo_tipo = self.tipo_articulo.codigo
            self.producto_id = f"{codigo_tipo}{str(nuevo_num).zfill(6)}"
        
        super().save(*args, **kwargs)


class CodigoProveedorCompra(models.Model):
    """Modelo para almacenar los códigos de proveedor asociados a un artículo"""
    articulo = models.ForeignKey(
        Articulo,
        on_delete=models.CASCADE,
        related_name='codigos_proveedor',
        verbose_name='Artículo'
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        related_name='codigos_articulos',
        verbose_name='Proveedor'
    )
    codigo_proveedor = models.CharField(
        max_length=100,
        verbose_name='Código Proveedor',
        help_text='Código que el proveedor usa para este artículo'
    )
    
    class Meta:
        verbose_name = 'Código Proveedor Compra'
        verbose_name_plural = 'Códigos Proveedor Compra'
        ordering = ['proveedor', 'codigo_proveedor']
        unique_together = [['articulo', 'proveedor']]  # Un proveedor solo puede aparecer una vez por artículo
        db_table = 'config_codigoproveedorcompra'

    def __str__(self):
        return f"{self.articulo.producto_id} - {self.proveedor.razon} - {self.codigo_proveedor}"
