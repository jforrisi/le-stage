"""
Script para cargar todas las tablas iniciales desde z_database.xlsx
Carga: IVA, Monedas, Documentos
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

def cargar_todas_tablas():
    """Carga todas las tablas desde el Excel"""
    
    excel_path = Path(__file__).parent / 'z_database.xlsx'
    
    if not excel_path.exists():
        print("⚠️  Archivo z_database.xlsx no encontrado.")
        return
    
    with transaction.atomic():
        # 1. Cargar IVAs
        print("📊 Cargando IVAs desde Excel...")
        try:
            df_iva = pd.read_excel(excel_path, sheet_name='config_iva')
            print(f"   Encontradas {len(df_iva)} filas en config_iva")
            
            creadas_iva = 0
            actualizadas_iva = 0
            
            for _, row in df_iva.iterrows():
                iva_data = {
                    'codigo': str(row.get('codigo', '')).strip(),
                    'nombre': str(row.get('nombre', '')).strip(),
                    'valor': float(row.get('valor', 0)) if pd.notna(row.get('valor')) else 0,
                    'activo': str(row.get('activo', 'SI')).strip().upper()[:2] if pd.notna(row.get('activo')) else 'SI'
                }
                
                if iva_data['codigo']:
                    iva, created = IVA.objects.get_or_create(
                        codigo=iva_data['codigo'],
                        defaults=iva_data
                    )
                    if not created:
                        for key, value in iva_data.items():
                            setattr(iva, key, value)
                        iva.save()
                        actualizadas_iva += 1
                        print(f"  🔄 IVA '{iva.codigo}' actualizado")
                    else:
                        creadas_iva += 1
                        print(f"  ✅ IVA '{iva.codigo}' creado")
            
            print(f"   ✅ IVAs: {creadas_iva} creadas, {actualizadas_iva} actualizadas")
        except Exception as e:
            print(f"  ⚠️  Error cargando IVAs: {e}")
            import traceback
            traceback.print_exc()
        
        # 2. Cargar Monedas
        print("\n💰 Cargando Monedas desde Excel...")
        try:
            # Intentar primero con config_monedas (con 's'), luego con config_moneda (sin 's')
            try:
                df_moneda = pd.read_excel(excel_path, sheet_name='config_monedas')
                print(f"   Encontradas {len(df_moneda)} filas en config_monedas")
            except:
                df_moneda = pd.read_excel(excel_path, sheet_name='config_moneda')
                print(f"   Encontradas {len(df_moneda)} filas en config_moneda")
            
            creadas_moneda = 0
            actualizadas_moneda = 0
            
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
                        for key, value in moneda_data.items():
                            setattr(moneda, key, value)
                        moneda.save()
                        actualizadas_moneda += 1
                        print(f"  🔄 Moneda '{moneda.codigo}' actualizada")
                    else:
                        creadas_moneda += 1
                        print(f"  ✅ Moneda '{moneda.codigo}' creada")
            
            print(f"   ✅ Monedas: {creadas_moneda} creadas, {actualizadas_moneda} actualizadas")
        except Exception as e:
            print(f"  ⚠️  Error cargando Monedas: {e}")
            import traceback
            traceback.print_exc()
        
        # 3. Cargar Documentos
        print("\n📄 Cargando Documentos desde Excel...")
        try:
            df_doc = pd.read_excel(excel_path, sheet_name='config_documentos_maestro')
            print(f"   Encontradas {len(df_doc)} filas en config_documentos_maestro")
            
            creadas_doc = 0
            actualizadas_doc = 0
            
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
                        for key, value in doc_data.items():
                            setattr(documento, key, value)
                        documento.save()
                        actualizadas_doc += 1
                        print(f"  🔄 Documento '{documento.codigo}' actualizado")
                    else:
                        creadas_doc += 1
                        print(f"  ✅ Documento '{documento.codigo}' creado")
            
            print(f"   ✅ Documentos: {creadas_doc} creados, {actualizadas_doc} actualizados")
        except Exception as e:
            print(f"  ⚠️  Error cargando Documentos: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*50)
        print("✅ PROCESO COMPLETADO!")
        print("="*50)
        print("\n📊 Resumen final:")
        print(f"  - IVAs: {IVA.objects.count()} totales")
        print(f"  - Monedas: {Moneda.objects.count()} totales")
        print(f"  - Documentos: {Documento.objects.count()} totales")
        print("\n" + "="*50)

if __name__ == '__main__':
    cargar_todas_tablas()

