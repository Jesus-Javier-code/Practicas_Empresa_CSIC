import os
import pandas as pd

# Definir rutas
data_path = "data/raw/TIRVolcH_La_Palma_Dataset.xlsx"
output_dir = "data/processed//"

# Crear la carpeta de salida si no existe
os.makedirs(output_dir, exist_ok=True)

# Cargar el archivo Excel
df = pd.read_excel(data_path)

# Asegurar que la columna de fecha está en formato datetime
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

# Extraer año y mes
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# Filtrar solo la columna de interés y la fecha
df_filtered = df[["Date", "Weekly_Max_VRP_TIR (MW)", "Year", "Month"]]

# Agrupar y guardar los archivos por mes y año
for (year, month), group in df_filtered.groupby(["Year", "Month"]):
    filename = f"radiance_{year}-{month:02d}.csv"
    output_path = os.path.join(output_dir, filename)
    group.drop(columns=["Year", "Month"], inplace=True)
    group.to_csv(output_path, index=False)
    print(f"✅ Archivo guardado: {output_path}")
