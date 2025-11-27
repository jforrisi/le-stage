from django.db import models


class FormaPagoTipo(models.Model):
    """Catálogo de tipos de forma de pago (Contado/Crédito) - Tabla maestra"""
    
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Nombre',
    )
    activo = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='SI',
        verbose_name='Activo',
    )
    
    class Meta:
        verbose_name = 'Tipo de Forma de Pago'
        verbose_name_plural = 'Tipos de Forma de Pago'
        ordering = ['id']
        db_table = 'config_forma_pago'
    
    def __str__(self):
        return self.nombre


class PlazoPago(models.Model):
    """Catálogo de plazos de pago y su lógica de cálculo - Tabla maestra"""
    
    codigo = models.CharField(
        max_length=50,
        primary_key=True,
        unique=True,
        verbose_name='Código',
        help_text='Código interno (ej: 30_DIAS, MES_COMPRA_15_DIAS)'
    )
    descripcion = models.CharField(
        max_length=200,
        verbose_name='Descripción'
    )
    plazo_en_dias = models.IntegerField(
        verbose_name='Plazo en días',
        help_text='Cantidad de días a sumar (0 para contado o no asignada)'
    )
    fin_de_mes = models.BooleanField(
        default=False,
        verbose_name='Desde fin de mes',
        help_text='Si es verdadero, el cálculo se hace desde fin de mes + plazo_en_dias'
    )
    
    class Meta:
        verbose_name = 'Plazo de Pago'
        verbose_name_plural = 'Plazos de Pago'
        ordering = ['codigo']
        db_table = 'config_plazo_pago'
    
    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

