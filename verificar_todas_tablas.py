"""
Script para verificar el estado de las tablas iniciales
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_demo.settings')
django.setup()

from configuracion.articulos.models import IVA, Moneda
from configuracion.documentos.models import Documento

print("="*50)
print("ESTADO ACTUAL DE LAS TABLAS")
print("="*50)

print(f"\n📊 IVAs: {IVA.objects.count()}")
if IVA.objects.count() > 0:
    for iva in IVA.objects.all()[:10]:
        print(f"  - {iva.codigo}: {iva.nombre} ({iva.valor*100:.2f}%)")
    if IVA.objects.count() > 10:
        print(f"  ... y {IVA.objects.count() - 10} más")

print(f"\n💰 Monedas: {Moneda.objects.count()}")
if Moneda.objects.count() > 0:
    for moneda in Moneda.objects.all()[:10]:
        print(f"  - {moneda.codigo}: {moneda.nombre}")
    if Moneda.objects.count() > 10:
        print(f"  ... y {Moneda.objects.count() - 10} más")

print(f"\n📄 Documentos: {Documento.objects.count()}")
if Documento.objects.count() > 0:
    for doc in Documento.objects.all()[:10]:
        print(f"  - {doc.codigo}: {doc.nombre}")
    if Documento.objects.count() > 10:
        print(f"  ... y {Documento.objects.count() - 10} más")

print("\n" + "="*50)

