import os
import glob
import numpy as np
import xarray as xr
import rioxarray
from datetime import datetime, timedelta
from pathlib import Path
import calendar

# === CONFIGURATION ===
script_path = Path(__file__).resolve()
project_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")

base_path = project_dir / "A00_data" / "B_processed" / "La_Palma" / "BT_daily_pixels"
output_dir = project_dir / "A00_data" / "B_processed" / "La_Palma" / "REF"
output_dir.mkdir(parents=True, exist_ok=True)

# === VOLCANO REGION ===
lat_min = 28.55
lat_max = 28.65
lon_min = -17.93
lon_max = -17.80

# === FECHA ACTUAL ===
hoy = datetime.now()
year_ref = hoy.year
month_ref = hoy.month
julian_start = datetime(year_ref, month_ref, 1).timetuple().tm_yday
julian_end = (datetime(year_ref, month_ref + 1, 1) - timedelta(days=1)).timetuple().tm_yday

print(f"\n=== Generando REF para {hoy.strftime('%Y-%m')} (días julianos {julian_start}-{julian_end}) ===")

# === FIND FILES FROM CURRENT MONTH ===
files = []
for julian_day in range(julian_start, julian_end + 1):
    folder = base_path / f"{year_ref}_{julian_day:03d}"
    # Buscar todos los archivos que coincidan con el patrón
    files += glob.glob(str(folder / f"BT_LaPalma_VJ102IMG_{year_ref}_*.nc"))

print(f"Archivos encontrados: {len(files)}")

if len(files) == 0:
    print("No hay archivos para procesar.")
    exit()

# === CREATE TEMPLATE GRID FROM FIRST FILE ===
ds_ref = xr.open_dataset(files[0])
bt = ds_ref["BT_I05"]
bt_template = xr.DataArray(
    data=bt.data,
    dims=("y", "x"),
    coords={"y": np.arange(bt.shape[0]), "x": np.arange(bt.shape[1])},
    name="brightness_temperature"
)
bt_template.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
bt_template.rio.write_crs("EPSG:4326", inplace=True)

# === PROCESS FILES ===
stack_reprojected = []
valid_files = []

for file in files:
    ds = xr.open_dataset(file)
    bt = ds["BT_I05"]
    lat = ds["latitude"]
    lon = ds["longitude"]

    bt_scene = xr.DataArray(
        data=bt.data,
        dims=("y", "x"),
        coords={"y": np.arange(bt.shape[0]), "x": np.arange(bt.shape[1])},
        name="brightness_temperature"
    )
    bt_scene.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
    bt_scene.rio.write_crs("EPSG:4326", inplace=True)

    bt_aligned = bt_scene.rio.reproject_match(bt_template)

    mask = (
        (lat.values >= lat_min) & (lat.values <= lat_max) &
        (lon.values >= lon_min) & (lon.values <= lon_max)
    )

    if not np.any(mask):
        print(f"{os.path.basename(file)} → Área vacía. Se omite.")
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
        valid_files.append(os.path.basename(file))
        print(f"{os.path.basename(file)} OK (min={minval:.2f}, std={stdval:.2f})")
    else:
        print(f"{os.path.basename(file)} DESCARTADO (min={minval:.2f}, std={stdval:.2f})")

print(f"Escenas válidas: {len(stack_reprojected)} / {len(files)}")

if len(stack_reprojected) == 0:
    print("No hay escenas válidas para generar REF.")
    exit()

# === COMPUTE MONTHLY REF ===
stack = xr.concat(stack_reprojected, dim="time")
stack["time"] = np.arange(len(stack_reprojected))
ref = stack.mean(dim="time", skipna=True)

ref_ds = ref.to_dataset(name="brightness_temperature_REF")
ref_ds["brightness_temperature_REF"].attrs["units"] = "K"
ref_ds.attrs["description"] = "Referencia mensual sobre el volcán (std > 3 y min > 210)"
ref_ds.attrs["used_files"] = ", ".join(valid_files)

# === SAVE FILE ===
output_filename = f"Ref_{year_ref}_{month_ref:02d}.nc"
output_path_final = output_dir / output_filename

try:
    if output_path_final.exists():
        output_path_final.unlink()
    ref_ds.to_netcdf(output_path_final, mode="w")
    print(f"REF guardado en: {output_path_final}")
except PermissionError:
    alt_path = output_dir / f"Ref_{year_ref}_{month_ref:02d}_v2.nc"
    ref_ds.to_netcdf(alt_path, mode="w")
    print(f"REF guardado como versión alternativa: {alt_path}")