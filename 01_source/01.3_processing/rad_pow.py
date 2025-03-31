import os
import numpy as np
import pandas as pd
import xarray as xr

# Definir rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Carpeta raíz del proyecto
data_path = os.path.join(base_dir, '00_data', 'processed', 'BT_by_Year_Month_Day', 'TB_By_Year_Month_Day.nc')
output_dir = os.path.join(base_dir, '00_data', 'processed', 'Radiative_Power')
os.makedirs(output_dir, exist_ok=True)

# Constantes de Planck y área del píxel VIIRS
C1 = 3.7418e-16  # W·m^2
C2 = 1.4388e-2   # m·K
lambda_viirs = 11.45e-6  # Longitud de onda en metros
pixel_area = 140.625  # Área en km²

# Función para calcular radiancia a partir de Temperatura de Brillo (TB)
def brightness_temperature_to_radiance(TB, wavelength):
    return (C1 / (wavelength**5)) / (np.exp(C2 / (wavelength * TB)) - 1)

# Leer el archivo NetCDF
dataset = xr.open_dataset(data_path)

# Asumiendo que la variable de temperatura de brillo se llama 'Brightness_Temperature'
if 'Brightness_Temperature' not in dataset.variables:
    raise KeyError("⚠️ La variable 'Brightness_Temperature' no está en el archivo NetCDF")

TB = dataset['Brightness_Temperature']  # Extraer los datos de temperatura de brillo

# Calcular la radiancia
radiance = brightness_temperature_to_radiance(TB, lambda_viirs)

# Calcular la potencia radiativa
radiative_power = radiance * pixel_area  # W/km²

# Guardar los resultados en un nuevo archivo NetCDF
output_path = os.path.join(output_dir, 'Radiative_Power.nc')
radiative_power.to_netcdf(output_path)

dataset.close()
print(f"✅ Archivo de Potencia Radiativa guardado en: {output_path}")
