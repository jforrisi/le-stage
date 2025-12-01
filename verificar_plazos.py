import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_demo.settings')
django.setup()

from configuracion.tablas.models import PlazoPago

print("=" * 60)
print("VERIFICACIÓN DE PLAZOS DE PAGO")
print("=" * 60)

count = PlazoPago.objects.count()
print(f"\nTotal de registros: {count}\n")

if count > 0:
    print("Códigos disponibles:")
    for p in PlazoPago.objects.all():
        print(f"  - {p.codigo}: {p.descripcion} (días: {p.plazo_en_dias}, fin_mes: {p.fin_de_mes})")
    
    # Buscar específicamente CREDITO_15_DIAS
    credito = PlazoPago.objects.filter(codigo='CREDITO_15_DIAS').first()
    if credito:
        print(f"\n✅ CREDITO_15_DIAS encontrado: {credito.descripcion}")
    else:
        print(f"\n❌ CREDITO_15_DIAS NO encontrado")
        print("   Buscando códigos similares...")
        similares = PlazoPago.objects.filter(codigo__icontains='15').values_list('codigo', flat=True)
        if similares:
            print(f"   Códigos con '15': {list(similares)}")
else:
    print("❌ No hay registros en la tabla")

print("=" * 60)

