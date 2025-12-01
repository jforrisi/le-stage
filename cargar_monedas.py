"""
Script temporal para cargar monedas desde z_database.xlsx
"""
import os
import django
from pathlib import Path
import pandas as pd

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_demo.settings')
django.setup()

from configuracion.articulos.models import Moneda
from django.db import transaction

def cargar_monedas():
    """Carga las monedas desde el Excel"""
    
    excel_path = Path(__file__).parent / 'z_database.xlsx'
    
    if not excel_path.exists():
        print("⚠️  Archivo z_database.xlsx no encontrado.")
        return
    
    # Intentar primero con config_monedas (con 's') como mencionó el usuario
    try:
        df_moneda = pd.read_excel(excel_path, sheet_name='config_monedas')
        print(f"✅ Hoja 'config_monedas' encontrada con {len(df_moneda)} filas")
    except:
        # Si no existe, intentar con config_moneda (sin 's')
        try:
            df_moneda = pd.read_excel(excel_path, sheet_name='config_moneda')
            print(f"✅ Hoja 'config_moneda' encontrada con {len(df_moneda)} filas")
        except Exception as e:
            print(f"⚠️  Error: No se encontró ninguna hoja de monedas. {e}")
            return
    
    with transaction.atomic():
        print("\n💰 Cargando Monedas...")
        creadas = 0
        actualizadas = 0
        
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
                    actualizadas += 1
                    print(f"  🔄 Moneda '{moneda.codigo}' actualizada")
                else:
                    creadas += 1
                    print(f"  ✅ Moneda '{moneda.codigo}' creada")
        
        print(f"\n✅ Proceso completado!")
        print(f"  - Creadas: {creadas}")
        print(f"  - Actualizadas: {actualizadas}")
        print(f"  - Total en BD: {Moneda.objects.count()}")

if __name__ == '__main__':
    cargar_monedas()

