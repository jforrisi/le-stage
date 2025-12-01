"""Script temporal para leer el Excel y ver qué datos tiene"""
import pandas as pd

xl = pd.ExcelFile('z_database.xlsx')
print("Hojas disponibles:")
for sheet in xl.sheet_names:
    print(f"  - {sheet}")

# Buscar hojas relacionadas con iva, moneda, documentos
print("\n" + "="*50)
for sheet in xl.sheet_names:
    if any(keyword in sheet.lower() for keyword in ['iva', 'moneda', 'mon', 'doc', 'documento']):
        print(f"\n📄 Hoja: {sheet}")
        try:
            df = pd.read_excel(xl, sheet_name=sheet)
            print(f"   Columnas: {list(df.columns)}")
            print(f"   Filas: {len(df)}")
            print(f"   Primeras filas:")
            print(df.head().to_string())
        except Exception as e:
            print(f"   Error: {e}")



