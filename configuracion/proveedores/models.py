from django.db import models
from configuracion.clientes.models import PAISES, DEPARTAMENTOS_URUGUAY, FORMAS_PAGO


class Proveedor(models.Model):
    """Modelo para representar un proveedor en el ERP"""
    empresa = models.IntegerField(default=1, verbose_name='Empresa')
    codigo = models.CharField(
        max_length=20, 
        unique=True,
        null=True,
        blank=True,
        verbose_name='Código',
        help_text='Formato: PROV000001'
    )
    razon = models.CharField(max_length=200, null=True, blank=True, verbose_name='Razón Social')
    nombre_comercial = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nombre Comercial')
    rut = models.BigIntegerField(null=True, blank=True, verbose_name='RUT')
    domicilio = models.CharField(max_length=200, blank=True, null=True, verbose_name='Domicilio')
    pais = models.CharField(
        max_length=10,
        choices=PAISES,
        default='UY',
        verbose_name='País'
    )
    departamento = models.CharField(
        max_length=2, 
        choices=DEPARTAMENTOS_URUGUAY, 
        blank=True, 
        null=True, 
        verbose_name='Departamento'
    )
    telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name='Teléfono')
    celular = models.CharField(max_length=50, blank=True, null=True, verbose_name='Celular')
    contacto = models.CharField(max_length=200, blank=True, null=True, verbose_name='Contacto')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    formadepago = models.CharField(
        max_length=30,
        choices=FORMAS_PAGO,
        default='NO_ASIGNADA',
        verbose_name='Forma de Pago'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    activo = models.CharField(max_length=2, default='SI', choices=[('SI', 'Sí'), ('NO', 'No')], verbose_name='Activo')
    fchhor = models.DateTimeField(auto_now=True, verbose_name='Fecha/Hora')
    usuario = models.IntegerField(blank=True, null=True, verbose_name='Usuario')
    monotributista = models.CharField(
        max_length=2, 
        null=True,
        blank=True,
        choices=[('SI', 'Sí'), ('NO', 'No')], 
        verbose_name='Monotributista',
        default='NO'
    )

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['razon']
        db_table = 'config_proveedores_maestro'

    def __str__(self):
        return f"{self.codigo} - {self.razon}"
    
    def save(self, *args, **kwargs):
        # Generar código automáticamente si no existe
        if not self.codigo:
            # Obtener el último número correlativo
            ultimo_proveedor = Proveedor.objects.order_by('-id').first()
            if ultimo_proveedor and ultimo_proveedor.codigo:
                try:
                    # Extraer el número del último código (PROV000001)
                    ultimo_num = int(ultimo_proveedor.codigo.replace('PROV', ''))
                    nuevo_num = ultimo_num + 1
                except:
                    nuevo_num = 1
            else:
                nuevo_num = 1
            
            # Formatear con ceros a la izquierda (PROV000001, PROV000002, etc.)
            self.codigo = f"PROV{str(nuevo_num).zfill(6)}"
        
        super().save(*args, **kwargs)
