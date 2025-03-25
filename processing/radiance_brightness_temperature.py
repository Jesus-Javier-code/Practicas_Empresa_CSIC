import os
import numpy as np
import xarray as xr

# Constantes de Planck
C1 = 3.7418e-16  # W·m^2
C2 = 1.4388e-2   # m·K
lambda_viirs = 11.45e-6  # Longitud de onda en metros

# Función para calcular temperatura de brillo (TB)
def radiance_to_brightness_temperature(L_lambda, wavelength):
    return C2 / (wavelength * np.log((C1 / (wavelength**5 * L_lambda)) + 1))

# Cargar archivo NetCDF
archivo_netcdf = "ruta_al_archivo.nc"
ds = xr.open_dataset(archivo_netcdf)

# Obtener la radiancia desde el NetCDF (ajusta el nombre de la variable si es diferente)
L_lambda = ds["radiance"].values  

# Calcular Temperatura de Brillo
TB = radiance_to_brightness_temperature(L_lambda, lambda_viirs)

# Agregar la variable de temperatura de brillo al dataset
ds["brightness_temperature"] = (("lat", "lon"), TB)

# Definir ruta de salida en el repositorio
repo_path = "C:/Users/silve/Practicas_Empresa_CSIC/data/processed/"
os.makedirs(repo_path, exist_ok=True)  # Crea la carpeta si no existe

# Guardar el NetCDF en la carpeta del repositorio
output_path = os.path.join(repo_path, "temperatura_brillo.nc")
ds.to_netcdf(output_path)

print(f"✅ Cálculo completado. Archivo guardado en: {output_path}")