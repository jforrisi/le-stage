from django.db import models


class Documento(models.Model):
    """Modelo para representar los tipos de documentos del sistema."""
    codigo = models.CharField(
        max_length=20,
        unique=True,
        primary_key=True,
        verbose_name='Código',
        help_text='Código único del documento (ej: transbu, valenobr)',
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre',
        help_text='Nombre completo del documento',
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción',
        help_text='Descripción opcional del documento',
    )
    activo = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='SI',
        verbose_name='Activo',
        help_text='Si el documento está activo o no',
    )

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['codigo']
        db_table = 'config_documentos_maestro'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


