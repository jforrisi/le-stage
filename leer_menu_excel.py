import pandas as pd

# Leer el Excel
df = pd.read_excel('config.xlsx', sheet_name='Hoja1')
print("Columnas:", df.columns.tolist())
print("\nPrimeras 20 filas:")
print(df.head(20).to_string())
print("\nForma del DataFrame:", df.shape)

