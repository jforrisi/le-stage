from django.db import models


class TipoPulidoPiezas(models.Model):
    """Tipos de pulido para piezas"""
    
    id = models.AutoField(
        primary_key=True,
        verbose_name='ID',
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre',
        unique=True,
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones',
    )
    
    class Meta:
        verbose_name = 'Tipo de Pulido Piezas'
        verbose_name_plural = 'Tipos de Pulido Piezas'
        ordering = ['nombre']
        db_table = 'industria_tipo_pulido_piezas'
    
    def __str__(self):
        return self.nombre
