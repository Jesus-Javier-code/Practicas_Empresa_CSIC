import os
import numpy as np
import xarray as xr
import rioxarray
from datetime import datetime, timedelta
from pathlib import Path

# === CONFIGURATION ===
# Get the path of this script and locate the project root
script_path = Path(__file__).resolve()
project_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")

# Define input and output directories
base_path = project_dir / "A00_data" / "B_processed" / "Teide" / "BT_daily_pixels"
output_dir = project_dir / "A00_data" / "B_processed" / "Teide" / "REF"
output_dir.mkdir(parents=True, exist_ok=True)

# === REGION OF INTEREST (Teide Volcano) ===
lat_min, lat_max = 28.2717, 28.2744
lon_min, lon_max = -16.6408, -16.6380

# === CURRENT DATE ===
today = datetime.now()
year_ref = today.year
month_ref = today.month

print(f"\n=== Generating REF for {today.strftime('%Y-%m')} ===")

# === LOAD MONTHLY FILE ===
monthly_file = base_path / f"BT_Teide_VJ102IMG_{year_ref}_{month_ref:02d}.nc"
if not monthly_file.exists():
    print(f"✘ Monthly file not found: {monthly_file.name}")
    exit()

ds_monthly = xr.open_dataset(monthly_file)
print(f"✔︎ Monthly file loaded: {monthly_file.name}")

if "BT_I05" not in ds_monthly:
    print("✘ Variable 'BT_I05' not found.")
    exit()

# === CREATE REPROJECTION TEMPLATE ===
bt_template = ds_monthly["BT_I05"].isel(time=0)
bt_template.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
bt_template.rio.write_crs("EPSG:4326", inplace=True)

# === GENERATE FULL LAT/LON GRIDS ===
lat_vals = ds_monthly["latitude"].values
lon_vals = ds_monthly["longitude"].values
lat_grid, lon_grid = np.meshgrid(lat_vals, lon_vals, indexing="ij")

# === PROCESS EACH SCENE ===
stack_reprojected = []
valid_files = []

for i in range(ds_monthly.sizes["time"]):
    bt = ds_monthly["BT_I05"].isel(time=i)

    # Prepare and reproject the BT scene
    bt_scene = bt
    bt_scene.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
    bt_scene.rio.write_crs("EPSG:4326", inplace=True)
    bt_aligned = bt_scene.rio.reproject_match(bt_template)

    # Apply geographic mask
    mask = (
        (lat_grid >= lat_min) & (lat_grid <= lat_max) &
        (lon_grid >= lon_min) & (lon_grid <= lon_max)
    )

    if not np.any(mask):
        print(f"Scene {i} → Empty region. Skipped.")
        continue

    # Clip scene to the masked area
    y_indices, x_indices = np.where(mask)
    y_min, y_max = y_indices.min(), y_indices.max()
    x_min, x_max = x_indices.min(), x_indices.max()

    y_dim, x_dim = bt_aligned.dims
    bt_clipped = bt_aligned.isel(
        **{y_dim: slice(y_min, y_max + 1), x_dim: slice(x_min, x_max + 1)}
    )

    # Check quality thresholds
    minval = np.nanmin(bt_clipped.values)
    stdval = np.nanstd(bt_clipped.values)

    if stdval > 3 and minval > 210:
        stack_reprojected.append(bt_clipped)
        valid_files.append(str(ds_monthly.time.values[i]))
        print(f"Scene {i} OK (min={minval:.2f}, std={stdval:.2f})")
    else:
        print(f"Scene {i} DISCARDED (min={minval:.2f}, std={stdval:.2f})")

print(f"\nValid scenes: {len(stack_reprojected)} / {ds_monthly.sizes['time']}")

if len(stack_reprojected) == 0:
    print("✘ No valid scenes found. REF not generated.")
    exit()

# === CALCULATE REF (Mean Brightness Temperature) ===
stack = xr.concat(stack_reprojected, dim="time")
stack["time"] = np.arange(len(stack_reprojected))  # Reset time dimension
ref = stack.mean(dim="time", skipna=True)

# Create dataset with metadata
ref_ds = ref.to_dataset(name="brightness_temperature_REF")
ref_ds["brightness_temperature_REF"].attrs["units"] = "K"
ref_ds.attrs["description"] = "Monthly filtered REF over the volcano"
ref_ds.attrs["used_scenes"] = ", ".join(valid_files)

# === SAVE FINAL REF FILE ===
output_filename = f"Ref_{year_ref}_{month_ref:02d}.nc"
output_path = output_dir / output_filename

try:
    if output_path.exists():
        output_path.unlink()
    ref_ds.to_netcdf(output_path, mode="w")
    print(f"\n✔︎ REF saved to: {output_path}")
except PermissionError:
    alt_output = output_dir / f"Ref_{year_ref}_{month_ref:02d}_v2.nc"
    ref_ds.to_netcdf(alt_output, mode="w")
    print(f"\n✔︎ REF saved as alternative version: {alt_output}")