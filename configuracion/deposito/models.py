from django.db import models


class Deposito(models.Model):
    """Modelo para representar un depósito."""
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre',
        help_text='Nombre del depósito'
    )
    explicacion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Explicación',
        help_text='Descripción o explicación del depósito'
    )

    class Meta:
        verbose_name = 'Depósito'
        verbose_name_plural = 'Depósitos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

