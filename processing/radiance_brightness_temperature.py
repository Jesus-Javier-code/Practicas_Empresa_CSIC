import os
import numpy as np
import pandas as pd

# Definir rutas
data_path = "data/processed/radiance_by_Year_Month"  # Asegúrate de que esta ruta contenga los archivos correctos
output_dir = "data/processed/brightness_temperature_Year_Month"  # Carpeta de salida para las temperaturas de brillo

# Crear la carpeta de salida si no existe
os.makedirs(output_dir, exist_ok=True)

# Constantes de Planck
C1 = 3.7418e-16  # W·m^2
C2 = 1.4388e-2   # m·K
lambda_viirs = 11.45e-6  # Longitud de onda en metros

# Función para calcular temperatura de brillo (TB)
def radiance_to_brightness_temperature(L_lambda, wavelength):
    """Convierte radiancia a temperatura de brillo usando la ley de Planck"""
    try:
        return C2 / (wavelength * np.log((C1 / (wavelength**5 * L_lambda)) + 1))
    except Exception as e:
        print(f"Error calculando la temperatura de brillo: {e}")
        return np.nan  # Si ocurre un error, devuelve NaN

# Verificar los archivos en la carpeta de radiancia por mes
if not os.path.exists(data_path):
    print(f"ERROR: La carpeta {data_path} no existe.")
else:
    files = os.listdir(data_path)
    print(f"Archivos en {data_path}: {files}")

# Función para procesar cada archivo
def process_file(file_path):
    # Cargar el archivo Excel
    df = pd.read_excel(file_path)

    # Verificar que las columnas son correctas
    print("Columnas disponibles:", df.columns)

    # Asegurar que la columna de fecha está en formato datetime
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

    # Convertir la columna 'Weekly_Max_VRP_TIR (MW)' a valores numéricos
    df["Weekly_Max_VRP_TIR (MW)"] = pd.to_numeric(df["Weekly_Max_VRP_TIR (MW)"], errors='coerce')

    # Verificar si hay valores NaN y mostrarlos
    if df["Weekly_Max_VRP_TIR (MW)"].isnull().any():
        print("Hay valores NaN en 'Weekly_Max_VRP_TIR (MW)', verificando filas con NaN:")
        print(df[df["Weekly_Max_VRP_TIR (MW)"].isnull()])

    # Extraer año y mes
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month

    # Filtrar solo las columnas de interés
    df_filtered = df[["Date", "Weekly_Max_VRP_TIR (MW)", "Year", "Month"]]

    # Convertir radiancia a temperatura de brillo
    df_filtered["Brightness_Temperature (K)"] = df_filtered["Weekly_Max_VRP_TIR (MW)"].apply(lambda L: radiance_to_brightness_temperature(L, lambda_viirs))

    # Agrupar y guardar los archivos por mes y año
    for (year, month), group in df_filtered.groupby(["Year", "Month"]):
        filename = f"brightness_temperature_{year}-{month:02d}.csv"
        output_path = os.path.join(output_dir, filename)
        group.drop(columns=["Year", "Month"], inplace=True)
        group.to_csv(output_path, index=False)
        print(f"✅ Archivo guardado: {output_path}")

# Procesar cada archivo en la carpeta de radiancia
for file in files:
    file_path = os.path.join(data_path, file)
    process_file(file_path)

print("🎉 ¡Proceso completado con éxito!")
