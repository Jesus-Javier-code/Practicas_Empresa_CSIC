import os
import numpy as np
import pandas as pd

# Definir rutas
data_path = "data/processed/radiance_by_Year_Month"
output_dir = "data/processed/brightness_temperature_by_Year_Month"

# Crear la carpeta de salida si no existe
os.makedirs(output_dir, exist_ok=True)

# Constantes de Planck
C1 = 3.7418e-16  # W·m^2
C2 = 1.4388e-2   # m·K
lambda_viirs = 11.45e-6  # Longitud de onda en metros

# Función para calcular temperatura de brillo (TB)
def radiance_to_brightness_temperature(L_lambda, wavelength):
    return C2 / (wavelength * np.log((C1 / (wavelength**5 * L_lambda)) + 1))

# Listar todos los archivos CSV en el directorio
files = [f for f in os.listdir(data_path) if f.endswith('.csv')]

# Procesar cada archivo CSV
for file in files:
    file_path = os.path.join(data_path, file)
    df = pd.read_csv(file_path)

    # Asegurarse de que las columnas existen y se cargan correctamente
    if 'Weekly_Max_VRP_TIR (MW)' not in df.columns:
        print(f"⚠️ La columna 'Weekly_Max_VRP_TIR (MW)' no está en el archivo {file}")
        continue

    # Convertir radiancia a temperatura de brillo
    df["Brightness_Temperature (K)"] = df["Weekly_Max_VRP_TIR (MW)"].apply(lambda L: radiance_to_brightness_temperature(L, lambda_viirs))

    # Guardar el archivo procesado
    output_path = os.path.join(output_dir, file)
    df.to_csv(output_path, index=False)
    print(f"✅ Archivo guardado: {output_path}")
