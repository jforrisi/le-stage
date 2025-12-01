from django.db import models


class CanalComercial(models.Model):
    """Modelo para representar un canal comercial"""
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    activo = models.CharField(
        max_length=2, 
        default='SI', 
        choices=[('SI', 'Sí'), ('NO', 'No')], 
        verbose_name='Activo'
    )
    fchhor = models.DateTimeField(auto_now=True, verbose_name='Fecha/Hora')

    class Meta:
        verbose_name = 'Canal Comercial'
        verbose_name_plural = 'Canales Comerciales'
        ordering = ['nombre']
        db_table = 'config_cliente_canalcomercial'

    def __str__(self):
        return self.nombre

