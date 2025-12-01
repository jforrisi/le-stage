from django.db import models
from configuracion.articulos.models import Moneda


# Lista de Bancos
BANCOS = [
    ('BROU', 'BANCO DE LA REPUBLICA ORIENTAL DEL URUGUAY'),
    ('BHU', 'BANCO HIPOTECARIO DEL URUGUAY'),
    ('BANDES', 'BANCO BANDES URUGUAY S.A.'),
    ('BBVA', 'BANCO BILBAO VIZCAYA ARGENTARIA URUGUAY S.A.'),
    ('BNA', 'BANCO DE LA NACION ARGENTINA (Sucursal Uruguay)'),
    ('ITAU', 'BANCO ITAU URUGUAY S.A.'),
    ('SANTANDER', 'BANCO SANTANDER S.A.'),
    ('HERITAGE', 'BANQUE HERITAGE (URUGUAY) S.A.'),
    ('CITIBANK', 'CITIBANK N.A. (SUCURSAL URUGUAY)'),
    ('HSBC', 'HSBC BANK (URUGUAY) S.A.'),
    ('SCOTIABANK', 'SCOTIABANK URUGUAY S.A.'),
]

# Lista de Instituciones Emisoras de Dinero Electrónico
IEDES = [
    ('MIDINERO', 'Midinero'),
    ('DEANDA', 'Deanda'),
    ('PLUXEE', 'Pluxee'),
    ('EDENRED', 'Edenred'),
    ('PREX', 'Prex'),
    ('BLANICO', 'Blanico'),
    ('CEDEU', 'Cedeu'),
    ('ITAU_EDE', 'Banco Itaú'),
    ('PAGANZA', 'Paganza'),
    ('OCA_BLUE', 'Oca Blue'),
    ('RALTUMY', 'Raltumy S.A.'),
    ('GRIN', 'Grin'),
    ('MERCADOPAGO', 'MercadoPago Uruguay'),
]

# Tipos de Disponibilidad
TIPOS_DISPONIBILIDAD = [
    ('BANCO', 'Banco'),
    ('IEDE', 'Institución Emisora de Dinero Electrónico'),
    ('CAJA', 'Caja'),
]

# Tipos de Cuenta (solo para bancos)
TIPOS_CUENTA = [
    ('CC', 'Cuenta Corriente'),
    ('CA', 'Caja de Ahorro'),
    ('NA', 'N/A'),
]


class Disponibilidad(models.Model):
    """Modelo para representar las disponibilidades (bancos, IEDEs, cajas)"""
    
    codigo = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Código',
        help_text='Formato: BCO000001, IEDE000001, CAJA000001'
    )
    
    tipo = models.CharField(
        max_length=10,
        choices=TIPOS_DISPONIBILIDAD,
        verbose_name='Tipo',
        help_text='Tipo de disponibilidad'
    )
    
    nombre_institucion = models.CharField(
        max_length=200,
        verbose_name='Nombre Institución',
        help_text='Nombre del banco, IEDE o "Caja"'
    )
    
    alias = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Alias',
        help_text='Alias opcional para identificar la disponibilidad'
    )
    
    numero = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Número',
        help_text='Número de cuenta (bancos) o número de IEDE (opcional)'
    )
    
    fecha_creacion = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_ingreso_sistema = models.DateField(
        null=True,  # Temporalmente nullable para migración
        blank=True,  # Temporalmente blank para migración
        verbose_name='Fecha de Ingreso al Sistema',
        help_text='Fecha en que la disponibilidad ingresó al sistema'
    )
    
    saldo_inicial = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Saldo Inicial en Moneda Original',
        help_text='Saldo inicial de la disponibilidad en su moneda original'
    )
    
    moneda = models.ForeignKey(
        Moneda,
        on_delete=models.PROTECT,
        related_name='disponibilidades',
        verbose_name='Moneda'
    )
    
    tipo_cuenta = models.CharField(
        max_length=2,
        choices=TIPOS_CUENTA,
        default='NA',
        verbose_name='Tipo de Cuenta',
        help_text='Solo para bancos: Cuenta Corriente o Caja de Ahorro'
    )
    
    chequera = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No'), ('NA', 'N/A')],
        default='NA',
        verbose_name='Chequera',
        help_text='Solo para bancos: Si tiene chequera o no'
    )
    
    activo = models.CharField(
        max_length=2,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        default='SI',
        verbose_name='Activo',
        help_text='Si la disponibilidad está activa'
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    
    class Meta:
        db_table = 'config_disponibilidades'
        verbose_name = 'Disponibilidad'
        verbose_name_plural = 'Disponibilidades'
        ordering = ['tipo', 'codigo']
    
    def __str__(self):
        alias_text = f" ({self.alias})" if self.alias else ""
        return f"{self.codigo} - {self.nombre_institucion}{alias_text}"
    
    def save(self, *args, **kwargs):
        """Auto-generar código según el tipo"""
        if not self.codigo:
            # Determinar prefijo según tipo
            if self.tipo == 'BANCO':
                prefijo = 'BCO'
            elif self.tipo == 'IEDE':
                prefijo = 'IEDE'
            elif self.tipo == 'CAJA':
                prefijo = 'CAJA'
            else:
                prefijo = 'DISP'
            
            # Buscar último código con ese prefijo
            ultimo = Disponibilidad.objects.filter(
                codigo__startswith=prefijo
            ).order_by('-codigo').first()
            
            if ultimo and ultimo.codigo:
                try:
                    # Extraer número del código (ej: BCO000001 -> 1)
                    ultimo_num = int(ultimo.codigo.replace(prefijo, ''))
                    nuevo_num = ultimo_num + 1
                except:
                    nuevo_num = 1
            else:
                nuevo_num = 1
            
            # Formatear con ceros a la izquierda
            self.codigo = f"{prefijo}{str(nuevo_num).zfill(6)}"
        
        super().save(*args, **kwargs)
