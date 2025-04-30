import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path

# === CONFIGURACIÓN ===
ruta_refs = Path('/Users/moni/Desktop/Practicas_Empresa_CSIC-1/A00_data/B_processed/Teide/REF')
ruta_salida = ruta_refs / "plots"
ruta_salida.mkdir(parents=True, exist_ok=True)

# Coordenadas de interés (La Palma)
lat_min, lat_max = 28, 29.28
lon_min, lon_max = -16, -15

# Colormap para los plots
colormap = 'turbo'

# === PROCESAR TODOS LOS REF ===
for ref_file in sorted(ruta_refs.glob('Ref_*.nc')):
    print(f"\nProcesando: {ref_file.name}")

    # Cargar dataset
    ds = xr.open_dataset(ref_file)

    # Comprobar variable
    if "brightness_temperature_REF" not in ds.variables:
        print(f"✘ No se encontró la variable brightness_temperature_REF en {ref_file.name}")
        continue

    ref = ds["brightness_temperature_REF"]

    # Estadísticas básicas
    print(f"Min: {ref.min().values:.2f} K, Max: {ref.max().values:.2f} K, Mean: {ref.mean().values:.2f} K, Std: {ref.std().values:.2f} K")

    # Recorte zona de interés
    try:
        ref_clip = ref.sel(
            y=slice(lat_max, lat_min),
            x=slice(lon_min, lon_max)
        )
    except Exception as e:
        print(f"✘ Error recortando {ref_file.name}: {e}")
        continue

    # Si no hay datos, saltar
    if ref_clip.size == 0:
        print(f"✘ No hay datos en la zona de interés para {ref_file.name}")
        continue

    # === MAPA Y GUARDADO ===
    fig, ax = plt.subplots(figsize=(8, 8))
    mesh = ax.pcolormesh(ref_clip.x, ref_clip.y, ref_clip.values, shading='auto', cmap=colormap)
    plt.colorbar(mesh, ax=ax, label='Brightness Temperature REF [K]')
    ax.set_xlabel('Longitude [degrees_east]')
    ax.set_ylabel('Latitude [degrees_north]')
    ax.set_title(f'REF {ref_file.stem.replace("Ref_", "")}')
    ax.invert_yaxis()

    # Nombre del plot
    plot_name = ruta_salida / f"{ref_file.stem}.jpg"
    plt.savefig(plot_name, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✔︎ Plot guardado: {plot_name.name}")