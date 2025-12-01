import os
import django
from pathlib import Path
import pandas as pd
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_demo.settings')
django.setup()

from configuracion.documentos.models import Documento

def cargar_documentos():
    excel_path = Path(__file__).parent / 'z_database.xlsx'
    
    if not excel_path.exists():
        print("⚠️  Archivo z_database.xlsx no encontrado.")
        return
    
    try:
        df_documentos = pd.read_excel(excel_path, sheet_name='config_documentos_maestro')
        df_documentos.columns = df_documentos.columns.str.lower()  # Normalizar nombres de columna
        
        created_count = 0
        updated_count = 0
        errors = []
        
        with transaction.atomic():
            print(f"📊 Cargando Documentos desde la hoja 'config_documentos_maestro'...")
            for _, row in df_documentos.iterrows():
                try:
                    codigo = str(row.get('codigo', '')).strip()
                    if not codigo:
                        errors.append(f"Fila con código vacío: {row.to_dict()}")
                        continue
                    
                    documento_data = {
                        'nombre': str(row.get('nombre', '')).strip(),
                        'descripcion': str(row.get('descripcion', '')).strip() if pd.notna(row.get('descripcion')) else '',
                        'activo': str(row.get('activo', 'SI')).strip().upper() if pd.notna(row.get('activo')) else 'SI',
                    }
                    
                    # Validar que activo sea SI o NO
                    if documento_data['activo'] not in ['SI', 'NO']:
                        documento_data['activo'] = 'SI'
                    
                    documento, created = Documento.objects.update_or_create(
                        codigo=codigo,
                        defaults=documento_data
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                except Exception as e:
                    errors.append(f"Error procesando fila {row.to_dict()}: {e}")
        
        print(f"✅ Carga de Documentos completada.")
        print(f"   - Registros creados: {created_count}")
        print(f"   - Registros actualizados: {updated_count}")
        if errors:
            print("❌ Errores durante la carga:")
            for error in errors:
                print(f"     - {error}")
        print(f"   Total de registros en config_documentos_maestro: {Documento.objects.count()}")
    
    except KeyError:
        print("❌ Error: La hoja 'config_documentos_maestro' no se encontró en z_database.xlsx")
    except Exception as e:
        print(f"❌ Error general al cargar documentos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    cargar_documentos()
