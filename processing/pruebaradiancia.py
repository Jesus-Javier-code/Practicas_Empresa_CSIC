import numpy as np
import xarray as xr

# Crear datos de ejemplo de radiancia (simulados para una región con 5x5 píxeles)
# Dimensiones: latitud (5), longitud (5)
latitudes = np.linspace(27.5, 28.0, 5)  # Latitudes de ejemplo
longitudes = np.linspace(-17.0, -16.5, 5)  # Longitudes de ejemplo

# Simulación de radiancia (en unidades de W·m^−2·sr^−1·μm^−1)
# Los valores son arbitrarios para el ejemplo
radiance_data = np.random.uniform(0.01, 0.1, size=(5, 5))

# Crear un Dataset de xarray con los datos
ds_example = xr.Dataset(
    {
        "radiance": (["lat", "lon"], radiance_data)
    },
    coords={
        "lat": latitudes,
        "lon": longitudes
    }
)

# Guardar el Dataset de ejemplo en un archivo NetCDF
ds_example.to_netcdf("radiance_example.nc")

print("✅ Archivo NetCDF de radiancia de ejemplo creado.")
