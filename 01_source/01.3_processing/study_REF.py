from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np

# Ruta al archivo REF
ruta_ref = '/Users/moni/Desktop/Practicas_Empresa_CSIC/00_data/processed/REF/REF_LaPalma_2025_03.nc'

# Abrir el archivo
with Dataset(ruta_ref, 'r') as ds:
    print("=== Variables ===")
    print(ds.variables.keys())

    ref = ds.variables['brightness_temperature_REF'][:]
    print("\n=== Forma del array REF ===", ref.shape)

    print("\n=== Atributos globales ===")
    for attr in ds.ncattrs():
        print(f"{attr}: {getattr(ds, attr)}")

# Mostrar resumen estadístico
print("\nResumen estadístico:")
print(f"  Min:  {np.nanmin(ref):.2f} K")
print(f"  Max:  {np.nanmax(ref):.2f} K")
print(f"  Mean: {np.nanmean(ref):.2f} K")

# Visualizar como mapa
plt.figure(figsize=(7, 6))
plt.imshow(ref, cmap='inferno')
plt.colorbar(label='TB REF (K)')
plt.title('Referencia mensual La Palma')
plt.axis('off')
plt.tight_layout()
plt.show()