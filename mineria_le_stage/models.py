from django.db import models
from django.utils import timezone
from decimal import Decimal
from configuracion.articulos.models import Familia, Articulo


class Equipo(models.Model):
    """Equipos de minería"""
    
    id_equipo = models.AutoField(
        primary_key=True,
        verbose_name='ID Equipo',
        db_column='id_equipo',
    )
    
    nombre_equipo = models.CharField(
        max_length=200,
        verbose_name='Nombre Equipo',
    )
    
    responsable = models.CharField(
        max_length=200,
        verbose_name='Responsable',
    )
    
    class Meta:
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['nombre_equipo']
        db_table = 'mineria_equipos'
    
    def __str__(self):
        return f"{self.nombre_equipo} - {self.responsable}"


class EquipoCorte(models.Model):
    """Equipos de corte de minería"""
    
    id_equipo = models.AutoField(
        primary_key=True,
        verbose_name='ID Equipo',
        db_column='id_equipo',
    )
    
    nombre_equipo = models.CharField(
        max_length=200,
        verbose_name='Nombre Equipo',
    )
    
    responsable = models.CharField(
        max_length=200,
        verbose_name='Responsable',
    )
    
    class Meta:
        verbose_name = 'Equipo Corte'
        verbose_name_plural = 'Equipos Corte'
        ordering = ['nombre_equipo']
        db_table = 'mineria_equipos_corte'
    
    def __str__(self):
        return f"{self.nombre_equipo} - {self.responsable}"


class PiedrasCanteras(models.Model):
    """Tabla maestra de piedras/canteras con KPI y puntos por defecto"""
    
    id = models.AutoField(
        primary_key=True,
        verbose_name='ID',
    )
    
    familia_producto = models.ForeignKey(
        Familia,
        on_delete=models.PROTECT,
        related_name='piedras_canteras',
        verbose_name='Familia de Producto',
    )
    
    producto = models.ForeignKey(
        Articulo,
        on_delete=models.PROTECT,
        related_name='piedras_canteras',
        verbose_name='Producto (Piedra)',
    )
    
    kpi = models.CharField(
        max_length=20,
        choices=[('Kg', 'Kilogramos'), ('Valuación', 'Valuación')],
        verbose_name='KPI',
        help_text='Indica si el puntaje se calcula por kilos o por valuación',
    )
    
    puntos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Puntos',
        help_text='Puntos por defecto (sugerencia para equipos)',
    )
    
    class Meta:
        verbose_name = 'Piedra/Cantera'
        verbose_name_plural = 'Piedras/Canteras'
        ordering = ['familia_producto', 'producto']
        unique_together = [['familia_producto', 'producto']]
        db_table = 'mineria_piedras_canteras'
    
    def __str__(self):
        return f"{self.producto.nombre} ({self.familia_producto.nombre}) - {self.kpi}"


class ProduccionEquipo(models.Model):
    """Producción por equipo, mes y piedra - Tabla única"""
    
    id = models.AutoField(
        primary_key=True,
        verbose_name='ID',
    )
    
    # Identificadores (equipo + mes + piedra)
    mes_año = models.DateField(
        verbose_name='Mes/Año',
        help_text='Primer día del mes (ej: 2025-11-01 para noviembre 2025)',
    )
    
    id_equipo = models.ForeignKey(
        Equipo,
        on_delete=models.PROTECT,
        related_name='producciones',
        verbose_name='Equipo',
        db_column='id_equipo',
    )
    
    piedra_cantera = models.ForeignKey(
        PiedrasCanteras,
        on_delete=models.PROTECT,
        related_name='producciones_equipos',
        verbose_name='Piedra/Cantera',
    )
    
    # Datos editables
    puntos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Puntos',
        help_text='Puntos editables (por defecto de PiedrasCanteras, pero el usuario puede cambiarlos)',
    )
    
    valuacion = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Valor Monetario',
        help_text='Valuación en dinero',
    )
    
    kilos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Kilos',
    )
    
    # Calculado automáticamente
    puntos_calculados = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Puntos Calculados',
        help_text='Calculado automáticamente: kilos × puntos (si KPI es Kg) o valuacion × puntos (si KPI es Valuación)',
    )
    
    class Meta:
        verbose_name = 'Producción Equipo'
        verbose_name_plural = 'Producciones Equipos'
        ordering = ['id_equipo', '-mes_año', 'piedra_cantera']
        unique_together = [['mes_año', 'id_equipo', 'piedra_cantera']]
        db_table = 'mineria_produccion_equipos'
    
    def __str__(self):
        return f"{self.id_equipo.nombre_equipo} - {self.piedra_cantera.producto.nombre} - {self.mes_año.strftime('%m/%Y')}"
    
    def calcular_puntos(self):
        """Calcula los puntos según KPI de la piedra"""
        if self.piedra_cantera.kpi == 'Kg':
            self.puntos_calculados = self.kilos * self.puntos
        elif self.piedra_cantera.kpi == 'Valuación':
            self.puntos_calculados = self.valuacion * self.puntos
        else:
            self.puntos_calculados = Decimal('0')
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para calcular puntos automáticamente"""
        # Si es nuevo registro y no tiene puntos, usar los de PiedrasCanteras
        if not self.pk and not self.puntos:
            self.puntos = self.piedra_cantera.puntos
        
        self.calcular_puntos()
        super().save(*args, **kwargs)


class Costos(models.Model):
    """Costos por equipo, fecha y rubro"""
    
    RUBROS_CHOICES = [
        ('Producciones', 'Producciones'),
        ('Sueldos', 'Sueldos'),
        ('Combustible', 'Combustible'),
        ('Insumos', 'Insumos'),
        ('Apoyo', 'Apoyo'),
        ('Explosivos', 'Explosivos'),
        ('Otros', 'Otros'),
    ]
    
    id = models.AutoField(
        primary_key=True,
        verbose_name='ID',
    )
    
    id_equipo = models.ForeignKey(
        Equipo,
        on_delete=models.PROTECT,
        related_name='costos',
        verbose_name='Equipo',
        db_column='id_equipo',
    )
    
    fecha = models.DateField(
        verbose_name='Fecha',
        help_text='Primer día del mes (ej: 2025-11-01 para noviembre 2025)',
    )
    
    rubro = models.CharField(
        max_length=50,
        choices=RUBROS_CHOICES,
        verbose_name='Rubro',
    )
    
    costo_dolares = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Costo en Dólares',
    )
    
    class Meta:
        verbose_name = 'Costo'
        verbose_name_plural = 'Costos'
        ordering = ['id_equipo', '-fecha', 'rubro']
        unique_together = [['id_equipo', 'fecha', 'rubro']]
        db_table = 'mineria_costos'
    
    def __str__(self):
        return f"{self.id_equipo.nombre_equipo} - {self.fecha.strftime('%m/%Y')} - {self.rubro}"


class PiezasCorteCantera(models.Model):
    """Piezas de corte en cantera - Datos de minería e industria"""
    
    id = models.AutoField(
        primary_key=True,
        verbose_name='ID',
    )
    
    # Campos básicos
    nombre_piedra = models.CharField(
        max_length=200,
        verbose_name='Nombre Piedra',
        blank=True,
    )
    
    numero = models.CharField(
        max_length=100,
        verbose_name='Número',
        blank=True,
    )
    
    # Campos de Extracción (Usuario 1: Minería)
    fecha_extraccion = models.DateField(
        verbose_name='Fecha Extracción',
        null=True,
        blank=True,
    )
    
    equipo_minero = models.ForeignKey(
        Equipo,
        on_delete=models.PROTECT,
        related_name='piezas_corte_cantera_minero',
        verbose_name='Equipo Minero',
        null=True,
        blank=True,
    )
    
    equipo_corte = models.ForeignKey(
        EquipoCorte,
        on_delete=models.PROTECT,
        related_name='piezas_corte_cantera_corte',
        verbose_name='Equipo de Corte',
        null=True,
        blank=True,
    )
    
    kilos_en_cantera = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Kilos en Cantera',
    )
    
    valuacion_cantera = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Valuación Cantera',
    )
    
    porcentaje_valuacion_corte = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='% de Valuación para Equipo de Corte',
        help_text='Porcentaje (ej: 15.50 para 15.5%)',
    )
    
    ganancia_equipo_corte = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Ganancia Equipo de Corte',
    )
    
    # Campos de Industria (Usuario 2: Industria)
    fecha_industria = models.DateField(
        verbose_name='Fecha Industria',
        null=True,
        blank=True,
    )
    
    kilos_recepcion_industria = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Kilos en Recepción Industria',
    )
    
    tipo_piedra = models.CharField(
        max_length=200,
        choices=[('Ágata', 'Ágata'), ('Amatista', 'Amatista')],
        verbose_name='Tipo de Piedra',
        blank=True,
    )
    
    tipo_proceso = models.ForeignKey(
        'industria_le_stage.TipoPulidoPiezas',
        on_delete=models.PROTECT,
        related_name='piezas_corte_cantera',
        verbose_name='Tipos de Pulido Piezas',
        null=True,
        blank=True,
    )
    
    kilos_despues_tallado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Kilos después del Tallado',
    )
    
    precio_por_kilo_tallado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Precio por Kilo de Tallado',
    )
    
    pulido_por_kilo = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Pulido por Kilo',
    )
    
    extra_carlos = models.CharField(
        max_length=200,
        verbose_name='Extra Carlos',
        blank=True,
    )
    
    # Auditoría
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación',
    )
    
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Modificación',
    )
    
    class Meta:
        verbose_name = 'Pieza Corte Cantera'
        verbose_name_plural = 'Piezas Corte Cantera'
        ordering = ['-fecha_creacion']
        db_table = 'mineria_piezas_corte_cantera'
    
    def __str__(self):
        nombre = self.nombre_piedra or f"Pieza {self.id}"
        return f"{nombre} - {self.numero or ''}"
    
    def calcular_ganancia_corte(self):
        """Calcula la ganancia del equipo de corte automáticamente"""
        if self.valuacion_cantera > 0 and self.porcentaje_valuacion_corte > 0:
            self.ganancia_equipo_corte = (self.valuacion_cantera * self.porcentaje_valuacion_corte) / 100
        else:
            self.ganancia_equipo_corte = Decimal('0')
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para calcular ganancia automáticamente"""
        self.calcular_ganancia_corte()
        super().save(*args, **kwargs)

