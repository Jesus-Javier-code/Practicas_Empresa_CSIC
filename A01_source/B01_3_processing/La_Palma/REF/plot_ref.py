import xarray as xr
import matplotlib.pyplot as plt

# === CONFIGURACIÓN ===
ruta_ref = '/Users/moni/Desktop/Practicas_Empresa_CSIC-1/A00_data/B_processed/La_Palma/REF/Ref_2022_04.nc'

# Coordenadas de interés (La Palma)
lat_min = 28.45
lat_max = 28.85
lon_min = -18.10
lon_max = -17.75

# === CARGAR REF ===
ds = xr.open_dataset(ruta_ref)
print(ds)

# Comprobamos la variable
if "brightness_temperature_REF" not in ds.variables:
    raise ValueError("No se encontró la variable 'brightness_temperature_REF' en el archivo.")

ref = ds["brightness_temperature_REF"]

# === MOSTRAR INFORMACIÓN GENERAL ===
print("\n=== Estadísticas ===")
print(f"Min: {ref.min().values:.2f} K")
print(f"Max: {ref.max().values:.2f} K")
print(f"Mean: {ref.mean().values:.2f} K")
print(f"Std: {ref.std().values:.2f} K")
print("\n=== Coordenadas ===")
print(f"Latitudes: {ref.y.values.min():.4f} to {ref.y.values.max():.4f}")
print(f"Longitudes: {ref.x.values.min():.4f} to {ref.x.values.max():.4f}")

# === RECORTE DE LA ZONA DE INTERÉS ===
ref_clip = ref.sel(
    y=slice(lat_max, lat_min),  # OJO: latitudes suelen ir de norte a sur
    x=slice(lon_min, lon_max)
)

# === MAPA ZOOM ===
plt.figure(figsize=(8, 8))
plt.pcolormesh(ref_clip.x, ref_clip.y, ref_clip.values, shading='auto', cmap='turbo')
plt.colorbar(label='Brightness Temperature REF [K]')
plt.xlabel('Longitude [degrees_east]')
plt.ylabel('Latitude [degrees_north]')
plt.title('REF Mensual - Zona La Palma')
plt.gca().invert_yaxis()
plt.show()

