import os
import numpy as np
import xarray as xr
import rioxarray
from datetime import datetime, timedelta
from pathlib import Path

# === CONFIGURACIÓN ===
script_path = Path(__file__).resolve()
project_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")

base_path = project_dir / "A00_data" / "B_processed" / "Teide" / "BT_daily_pixels"
output_dir = project_dir / "A00_data" / "B_processed" / "Teide" / "REF"
output_dir.mkdir(parents=True, exist_ok=True)

# === REGIÓN DEL VOLCÁN (La Palma) ===
lat_min = 28.55
lat_max = 28.65
lon_min = -17.93
lon_max = -17.80

# === FECHA ACTUAL ===
hoy = datetime.now()
year_ref = hoy.year
month_ref = hoy.month

print(f"\n=== Generando REF para {hoy.strftime('%Y-%m')} ===")

# === CARGAR ARCHIVO MENSUAL BT ===
archivo_mensual = base_path / f"BT_Teide_VJ102IMG_{year_ref}_{month_ref:02d}.nc"
if not archivo_mensual.exists():
    print(f"✘ No se encontró el archivo mensual: {archivo_mensual.name}")
    exit()

ds_mensual = xr.open_dataset(archivo_mensual)
print(f"✔︎ Archivo mensual cargado: {archivo_mensual.name}")

if "BT_I05" not in ds_mensual:
    print("✘ Variable BT_I05 no encontrada.")
    exit()

# === PLANTILLA DE REPROYECCIÓN ===
bt_template = ds_mensual["BT_I05"].isel(time=0)
bt_template.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
bt_template.rio.write_crs("EPSG:4326", inplace=True)

# === PROCESAR ESCENAS ===
stack_reprojected = []
valid_files = []

for i in range(ds_mensual.dims["time"]):
    bt = ds_mensual["BT_I05"].isel(time=i)
    lat = ds_mensual["latitude"]
    lon = ds_mensual["longitude"]

    bt_scene = bt
    bt_scene.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
    bt_scene.rio.write_crs("EPSG:4326", inplace=True)

    bt_aligned = bt_scene.rio.reproject_match(bt_template)

    mask = (
        (lat.values >= lat_min) & (lat.values <= lat_max) &
        (lon.values >= lon_min) & (lon.values <= lon_max)
    )

    if not np.any(mask):
        print(f"Escena {i} → Área vacía. Se omite.")
        continue

    y_indices, x_indices = np.where(mask)
    y_min, y_max = y_indices.min(), y_indices.max()
    x_min, x_max = x_indices.min(), x_indices.max()

    y_dim, x_dim = bt_aligned.dims
    bt_clipped = bt_aligned.isel(
        **{y_dim: slice(y_min, y_max + 1), x_dim: slice(x_min, x_max + 1)}
    )

    minval = np.nanmin(bt_clipped.values)
    stdval = np.nanstd(bt_clipped.values)

    if stdval > 3 and minval > 210:
        stack_reprojected.append(bt_clipped)
        valid_files.append(str(ds_mensual.time.values[i]))
        print(f"Escena {i} OK (min={minval:.2f}, std={stdval:.2f})")
    else:
        print(f"Escena {i} DESCARTADA (min={minval:.2f}, std={stdval:.2f})")

print(f"\nEscenas válidas: {len(stack_reprojected)} / {ds_mensual.dims['time']}")

if len(stack_reprojected) == 0:
    print("✘ No hay escenas válidas. No se genera REF.")
    exit()

# === CALCULAR REF ===
stack = xr.concat(stack_reprojected, dim="time")
stack["time"] = np.arange(len(stack_reprojected))
ref = stack.mean(dim="time", skipna=True)

ref_ds = ref.to_dataset(name="brightness_temperature_REF")
ref_ds["brightness_temperature_REF"].attrs["units"] = "K"
ref_ds.attrs["description"] = "REF mensual filtrada sobre el volcán"
ref_ds.attrs["used_scenes"] = ", ".join(valid_files)

# === GUARDAR ARCHIVO FINAL ===
output_filename = f"Ref_{year_ref}_{month_ref:02d}.nc"
output_path = output_dir / output_filename

try:
    if output_path.exists():
        output_path.unlink()
    ref_ds.to_netcdf(output_path, mode="w")
    print(f"\n✔︎ REF guardada en: {output_path}")
except PermissionError:
    alt_output = output_dir / f"Ref_{year_ref}_{month_ref:02d}_v2.nc"
    ref_ds.to_netcdf(alt_output, mode="w")
    print(f"\n✔︎ REF guardada como versión alternativa: {alt_output}")