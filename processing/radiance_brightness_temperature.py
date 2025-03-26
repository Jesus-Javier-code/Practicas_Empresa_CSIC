import os
import numpy as np
import pandas as pd

# Definir rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Carpeta raíz del proyecto
data_path = os.path.join(base_dir, 'data', 'processed', 'radiance_by_Year_Month')
output_dir = os.path.join(base_dir, 'data', 'processed', 'brightness_temperature_by_Year_Month')

# Constantes de Planck
C1 = 3.7418e-16  # W·m^2
C2 = 1.4388e-2   # m·K
lambda_viirs = 11.45e-6  # Longitud de onda en metros

# Función para calcular temperatura de brillo (TB) usando la ley de Planck
def radiance_to_brightness_temperature(L_lambda, wavelength):
    return C2 / (wavelength * np.log((C1 / (wavelength**5 * L_lambda)) + 1))

# Crear la carpeta de salida si no existe
os.makedirs(output_dir, exist_ok=True)

# Listar todos los archivos CSV en el directorio de radiancia
files = [f for f in os.listdir(data_path) if f.endswith('.csv')]

# Procesar cada archivo CSV
for file in files:
    file_path = os.path.join(data_path, file)
    df = pd.read_csv(file_path)

    # Verificar que la columna 'Weekly_Max_VRP_TIR (MW)' existe en los datos
    if 'Weekly_Max_VRP_TIR (MW)' not in df.columns:
        print(f"⚠️ La columna 'Weekly_Max_VRP_TIR (MW)' no está en el archivo {file}")
        continue

    # Seleccionar solo la columna de radiancia 'Weekly_Max_VRP_TIR (MW)' y calcular la temperatura de brillo
    df['Brightness_Temperature (K)'] = df['Weekly_Max_VRP_TIR (MW)'].apply(lambda L: radiance_to_brightness_temperature(L, lambda_viirs))

    # Guardar el archivo procesado
    output_path = os.path.join(output_dir, f"brightness_temperature_{file}")
    df.to_csv(output_path, columns=['Weekly_Max_VRP_TIR (MW)', 'Brightness_Temperature (K)'], index=False)
    print(f"✅ Archivo guardado: {output_path}")

