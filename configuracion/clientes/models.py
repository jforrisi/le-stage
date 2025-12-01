from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
import os

# Importar configuración de empresa
try:
    from erp_demo.config import EMPRESA_NOMBRE, EMPRESA_CODIGO
except ImportError:
    EMPRESA_NOMBRE = "Le Stage"
    EMPRESA_CODIGO = 1

# Importar CanalComercial (importación diferida para evitar circular)
# from .canal_comercial.models import CanalComercial

# Lista de países
PAISES = [
    ('UY', 'Uruguay'),
    ('AR', 'Argentina'),
    ('BR', 'Brasil'),
    ('PY', 'Paraguay'),
    ('BO', 'Bolivia'),
    ('CL', 'Chile'),
    ('PE', 'Perú'),
    ('EC', 'Ecuador'),
    ('CO', 'Colombia'),
    ('VE', 'Venezuela'),
    ('MX', 'México'),
    ('US', 'Estados Unidos'),
    ('ES', 'España'),
    ('IT', 'Italia'),
    ('FR', 'Francia'),
    ('DE', 'Alemania'),
    ('CN', 'China'),
    ('JP', 'Japón'),
    ('OTRO', 'Otro'),
]

# Departamentos de Uruguay
DEPARTAMENTOS_URUGUAY = [
    ('1', 'Artigas'),
    ('2', 'Canelones'),
    ('3', 'Cerro Largo'),
    ('4', 'Colonia'),
    ('5', 'Durazno'),
    ('6', 'Flores'),
    ('7', 'Florida'),
    ('8', 'Lavalleja'),
    ('9', 'Maldonado'),
    ('10', 'Montevideo'),
    ('11', 'Paysandú'),
    ('12', 'Río Negro'),
    ('13', 'Rivera'),
    ('14', 'Rocha'),
    ('15', 'Salto'),
    ('16', 'San José'),
    ('17', 'Soriano'),
    ('18', 'Tacuarembó'),
    ('19', 'Treinta y Tres'),
]

class FormaPago(models.Model):
    """Catálogo de formas de pago y su lógica de cálculo."""
    codigo = models.CharField(
        max_length=50,
        primary_key=True,
        unique=True,
        verbose_name='ID Forma de Pago',
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
        verbose_name = 'Forma de Pago'
        verbose_name_plural = 'Formas de Pago'
        ordering = ['codigo']
        db_table = 'config_formapago'

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


# Formas de pago (constante usada solo como respaldo / compatibilidad)
FORMAS_PAGO = [
    ('30_DIAS', '30 DIAS'),
    ('45_DIAS', '45 DIAS'),
    ('60_DIAS', '60 Dias'),
    ('A_35_DIAS', 'A 35 días'),
    ('CONTADO', 'Contado'),
    ('CREDITO_15_DIAS', 'Credito 15 dias'),
    ('CREDITO_2_DIAS', 'Crédito 2 Días'),
    ('CREDITO_8_DIAS', 'Credito 8 Dias'),
    ('MES_COMPRA_15_DIAS', 'Mes de Compra y 15 Dias'),
    ('MES_COMPRA_30_DIAS', 'Mes de Compra y 30 Dias'),
    ('MES_COMPRA_45_DIAS', 'Mes de Compra y 45 Dias'),
    ('MES_COMPRA_60_DIAS', 'Mes de Compra y 60 dias'),
    ('NO_ASIGNADA', 'No Asignada'),
    ('VENCIMIENTO_PACTADO', 'Vencimiento Pactado'),
]


class Cliente(models.Model):
    """Modelo para representar un cliente en el ERP"""
    
    # Código con prefijo CLI y correlativo
    codigo = models.CharField(
        max_length=20, 
        unique=True,
        null=True,
        blank=True,
        verbose_name='Código',
        help_text='Formato: CLI000001'
    )
    nombre_comercial = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name='Nombre Comercial'
    )
    razon_social = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name='Razón Social'
    )
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
    forma_pago = models.CharField(
        max_length=30,
        choices=FORMAS_PAGO,
        default='NO_ASIGNADA',
        verbose_name='Forma de Pago'
    )
    canal_comercial = models.ForeignKey(
        'canal_comercial.CanalComercial',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Canal Comercial',
        related_name='clientes'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    activo = models.CharField(
        max_length=2, 
        default='SI', 
        choices=[('SI', 'Sí'), ('NO', 'No')], 
        verbose_name='Activo'
    )
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
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre_comercial']
        db_table = 'config_cliente_maestro'

    def __str__(self):
        return f"{self.codigo} - {self.nombre_comercial or 'Sin nombre'}"

    def save(self, *args, **kwargs):
        # Generar código automáticamente si no existe
        if not self.codigo:
            # Obtener el último número correlativo
            ultimo_cliente = Cliente.objects.order_by('-id').first()
            if ultimo_cliente and ultimo_cliente.codigo:
                try:
                    # Extraer el número del último código
                    ultimo_num = int(ultimo_cliente.codigo.replace('CLI', ''))
                    nuevo_num = ultimo_num + 1
                except:
                    nuevo_num = 1
            else:
                nuevo_num = 1
            
            # Formatear con ceros a la izquierda (CLI000001, CLI000002, etc.)
            self.codigo = f"CLI{str(nuevo_num).zfill(6)}"
        
        super().save(*args, **kwargs)

    @property
    def nombre_completo(self):
        return self.nombre_comercial or self.razon_social or ''

