from django.db import models
from configuracion.documentos.models import Documento


class Transaccion(models.Model):
    """Modelo para representar una transacción en el sistema"""
    
    transaccion = models.CharField(  # Cambiar de 'codigo' a 'transaccion'
        max_length=10,
        primary_key=True,  # ← Agregar esto
        verbose_name='Transacción',
        help_text='Formato: AAMMXXXXXX (ej: 251100001 para noviembre 2025)'
    )
    
    documento_id = models.CharField(  # ← Agregar este campo
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Documento ID',
        db_column='documento_id'
    )
    
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación',
        help_text='Fecha y hora en que se creó la transacción'
    )
    
    usuario = models.IntegerField(  # ← Agregar este campo
        null=True,
        blank=True,
        verbose_name='Usuario'
    )
    
    # activo = ...  ← ELIMINAR este campo, no existe en la tabla
    
    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['-fecha', '-transaccion']  # Cambiar '-codigo' por '-transaccion'
        db_table = 'config_transacciones'
    
    def __str__(self):
        return self.transaccion  # Cambiar de self.codigo
    
    def save(self, *args, **kwargs):
        # Generar transaccion automáticamente si no existe
        if not self.transaccion:  # Cambiar de self.codigo
            from datetime import datetime
            now = datetime.now()
            año_mes = f"{now.year % 100:02d}{now.month:02d}"
            
            # Obtener el último número correlativo del mes
            ultima = Transaccion.objects.filter(
                transaccion__startswith=año_mes  # Cambiar codigo__ por transaccion__
            ).order_by('-transaccion').first()  # Cambiar -codigo por -transaccion
            
            if ultima and ultima.transaccion:  # Cambiar codigo por transaccion
                try:
                    ultimo_num = int(ultima.transaccion[4:])  # Cambiar codigo por transaccion
                    nuevo_num = ultimo_num + 1
                except:
                    nuevo_num = 1
            else:
                nuevo_num = 1
            
            # Formatear con ceros a la izquierda
            self.transaccion = f"{año_mes}{str(nuevo_num).zfill(6)}"  # Cambiar codigo por transaccion
        
        super().save(*args, **kwargs)
        
class TransaccionDocumento(models.Model):
    """Modelo para vincular una transacción con un documento específico"""
    
    transaccion = models.ForeignKey(
        Transaccion,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='Transacción'
    )
    documento = models.ForeignKey(
        Documento,
        on_delete=models.PROTECT,
        related_name='transacciones',
        verbose_name='Documento',
        help_text='Tipo de documento (ej: Orden Compra, Factura Venta)'
    )
    referencia_id = models.IntegerField(
        verbose_name='ID de Referencia',
        help_text='ID del documento en su tabla específica (ej: ID de la orden de compra)'
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    class Meta:
        verbose_name = 'Transacción Documento'
        verbose_name_plural = 'Transacciones Documentos'
        ordering = ['-fecha']
        unique_together = (('documento', 'referencia_id'),)
        db_table = 'config_transacciondocumento'

    def __str__(self):
        return f"{self.transaccion.transaccion} - {self.documento.nombre} #{self.referencia_id}"

