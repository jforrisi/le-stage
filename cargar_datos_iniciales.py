"""
Script para cargar datos iniciales del sistema (IVA, Monedas, Documentos)
Lee los datos desde z_database.xlsx
Ejecutar con: python cargar_datos_iniciales.py
"""
import os
import django
from pathlib import Path
import pandas as pd

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_demo.settings')
django.setup()

from configuracion.articulos.models import IVA, Moneda
from configuracion.documentos.models import Documento
from django.db import transaction

def cargar_datos_iniciales():
    """Carga los datos iniciales del sistema desde el Excel"""
    
    excel_path = Path(__file__).parent / 'z_database.xlsx'
    
    if not excel_path.exists():
        print("⚠️  Archivo z_database.xlsx no encontrado. Usando datos por defecto.")
        return cargar_datos_por_defecto()
    
    with transaction.atomic():
        # 1. Cargar IVAs desde Excel
        print("📊 Cargando IVAs desde Excel...")
        try:
            df_iva = pd.read_excel(excel_path, sheet_name='config_iva')
            print(f"   Encontradas {len(df_iva)} filas en config_iva")
            
            for _, row in df_iva.iterrows():
                # Mapear columnas del Excel a los campos del modelo
                iva_data = {
                    'codigo': str(row.get('codigo', '')).strip(),
                    'nombre': str(row.get('nombre', '')).strip(),
                    'valor': float(row.get('valor', 0)),
                    'activo': str(row.get('activo', 'SI')).strip().upper()[:2] if pd.notna(row.get('activo')) else 'SI'
                }
                
                if iva_data['codigo']:
                    iva, created = IVA.objects.get_or_create(
                        codigo=iva_data['codigo'],
                        defaults=iva_data
                    )
                    if not created:
                        # Actualizar si ya existe
                        for key, value in iva_data.items():
                            setattr(iva, key, value)
                        iva.save()
                        print(f"  🔄 IVA '{iva.codigo}' actualizado")
                    else:
                        print(f"  ✅ IVA '{iva.codigo}' creado")
        except Exception as e:
            print(f"  ⚠️  Error cargando IVAs: {e}")
        
        # 2. Cargar Monedas desde Excel
        print("\n💰 Cargando Monedas desde Excel...")
        try:
            df_moneda = pd.read_excel(excel_path, sheet_name='config_moneda')
            print(f"   Encontradas {len(df_moneda)} filas en config_moneda")
            
            for _, row in df_moneda.iterrows():
                moneda_data = {
                    'codigo': str(row.get('codigo', '')).strip(),
                    'nombre': str(row.get('nombre', '')).strip(),
                    'activo': str(row.get('activo', 'SI')).strip().upper()[:2] if pd.notna(row.get('activo')) else 'SI'
                }
                
                if moneda_data['codigo']:
                    moneda, created = Moneda.objects.get_or_create(
                        codigo=moneda_data['codigo'],
                        defaults=moneda_data
                    )
                    if not created:
                        # Actualizar si ya existe
                        for key, value in moneda_data.items():
                            setattr(moneda, key, value)
                        moneda.save()
                        print(f"  🔄 Moneda '{moneda.codigo}' actualizada")
                    else:
                        print(f"  ✅ Moneda '{moneda.codigo}' creada")
        except Exception as e:
            print(f"  ⚠️  Error cargando Monedas: {e}")
        
        # 3. Cargar Documentos desde Excel
        print("\n📄 Cargando Documentos desde Excel...")
        try:
            df_doc = pd.read_excel(excel_path, sheet_name='config_documentos_maestro')
            print(f"   Encontradas {len(df_doc)} filas en config_documentos_maestro")
            
            for _, row in df_doc.iterrows():
                doc_data = {
                    'codigo': str(row.get('codigo', '')).strip(),
                    'nombre': str(row.get('nombre', '')).strip(),
                    'descripcion': str(row.get('descripcion', '')).strip() if pd.notna(row.get('descripcion')) else '',
                    'activo': str(row.get('activo', 'SI')).strip().upper()[:2] if pd.notna(row.get('activo')) else 'SI'
                }
                
                if doc_data['codigo']:
                    documento, created = Documento.objects.get_or_create(
                        codigo=doc_data['codigo'],
                        defaults=doc_data
                    )
                    if not created:
                        # Actualizar si ya existe
                        for key, value in doc_data.items():
                            setattr(documento, key, value)
                        documento.save()
                        print(f"  🔄 Documento '{documento.codigo}' actualizado")
                    else:
                        print(f"  ✅ Documento '{documento.codigo}' creado")
        except Exception as e:
            print(f"  ⚠️  Error cargando Documentos: {e}")
        
        print("\n✅ Datos iniciales cargados exitosamente!")
        print("\nResumen:")
        print(f"  - IVAs: {IVA.objects.count()}")
        print(f"  - Monedas: {Moneda.objects.count()}")
        print(f"  - Documentos: {Documento.objects.count()}")

def cargar_datos_por_defecto():
    """Carga datos por defecto si no existe el Excel"""
    print("📊 Cargando datos por defecto...")
    # Datos mínimos por defecto
    pass

if __name__ == '__main__':
    cargar_datos_iniciales()

