import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_demo.settings')
django.setup()

from configuracion.articulos.models import Moneda

print(f"Total de monedas: {Moneda.objects.count()}")
print("\nMonedas en la base de datos:")
for m in Moneda.objects.all():
    print(f"  - {m.codigo}: {m.nombre} ({m.activo})")

