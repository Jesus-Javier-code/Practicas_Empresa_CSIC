import os
import numpy as np
import pandas as pd

# Definir rutas
data_path = "Practica_Empresa_CSIC/data/raw/TIRVolcH_La_Palma_Dataset.xlsx"
output_dir = "Practica_Empresa_CSIC/data/processed/radiance_by_month/"

# Crear la carpeta de salida si no existe
os.makedirs(output_dir, exist_ok=True)

# Constantes de Planck
C1 = 3.7418e-16  # W·m^2
C2 = 1.4388e-2   # m·K
lambda_viirs = 11.45e-6  # Longitud de onda en metros

# Función para calcular temperatura de brillo (TB)
def radiance_to_brightness_temperature(L_lambda, wavelength):
    return C2 / (wavelength * np.log((C1 / (wavelength**5 * L_lambda)) + 1))

# Cargar el archivo Excel
df = pd.read_excel(data_path)

# Asegurar que la columna de fecha está en formato datetime
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

# Extraer año y mes
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# Filtrar solo la columna de interés y la fecha
df_filtered = df[["Date", "Weekly_Max_VRP_TIR (MW)", "Year", "Month"]]

# Convertir radiancia a temperatura de brillo
df_filtered["Brightness_Temperature (K)"] = df_filtered["Weekly_Max_VRP_TIR (MW)"].apply(lambda L: radiance_to_brightness_temperature(L, lambda_viirs))

# Agrupar y guardar los archivos por mes y año
for (year, month), group in df_filtered.groupby(["Year", "Month"]):
    filename = f"radiance_{year}-{month:02d}.csv"
    output_path = os.path.join(output_dir, filename)
    group.drop(columns=["Year", "Month"], inplace=True)
    group.to_csv(output_path, index=False)
    print(f"✅ Archivo guardado: {output_path}")