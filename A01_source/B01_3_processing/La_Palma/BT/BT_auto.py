import os
import numpy as np
import xarray as xr
from netCDF4 import Dataset
from pathlib import Path
from datetime import datetime, timedelta

# === PATHS ===
# Get the path to this script and locate the project root directory
script_path = Path(__file__).resolve()
proyecto_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC-1")

# Define input and output directories
input_base_path = proyecto_dir / "A00_data" / "B_raw" / "La_Palma"
output_dir_bt = proyecto_dir / "A00_data" / "B_processed" / "La_Palma" / "BT_daily_pixels"
output_dir_bt.mkdir(parents=True, exist_ok=True)  # Create output directory if it doesn't exist

# === CONSTANTS ===
wavelength = 11.45  # µm
c1 = 1.191042e8   # First radiation constant (W·µm⁴/m²/sr)
c2 = 1.4387752e4  # Second radiation constant (µm·K)

def radiance_to_bt(radiance):
    """
    Converts radiance to brightness temperature using the inverse Planck function.
    Filters invalid or non-positive radiance values.
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        bt = c2 / (wavelength * np.log((c1 / (radiance * wavelength**5)) + 1))
        bt = np.where((radiance > 0) & np.isfinite(bt), bt, np.nan)
    return bt

def process_to_monthly(nc_file, file_date):
    """
    Processes a NetCDF file to extract brightness temperature and returns it as a DataArray.
    Includes spatial coordinates and time.
    """
    with Dataset(nc_file) as nc:
        obs = nc.groups['observation_data']
        i05 = obs["I05"][:]
        bt_i05 = radiance_to_bt(i05.filled(np.nan))

        # Extract spatial coordinates from global attributes
        south = nc.getncattr('SouthBoundingCoordinate')
        north = nc.getncattr('NorthBoundingCoordinate')
        west = nc.getncattr('WestBoundingCoordinate')
        east = nc.getncattr('EastBoundingCoordinate')

        n_lines, n_pixels = bt_i05.shape
        latitudes = np.linspace(north, south, n_lines)
        longitudes = np.linspace(west, east, n_pixels)

    # Create an xarray DataArray
    da = xr.DataArray(
        bt_i05[np.newaxis, :, :],
        dims=("time", "y", "x"),
        coords={
            "time": [np.datetime64(file_date.date())],
            "y": np.arange(n_lines),
            "x": np.arange(n_pixels),
            "latitude": ("y", latitudes),
            "longitude": ("x", longitudes),
        },
        name="BT_I05"
    )
    return da

# === YESTERDAY'S DATE ===
yesterday = datetime.now() - timedelta(days=1)
year = yesterday.year
month = yesterday.month
julian_day = yesterday.timetuple().tm_yday

print(f"\n=== Processing BT for {yesterday.strftime('%Y-%m-%d')} ===")

# === DELETE PREVIOUS MONTH FILE IF TODAY IS THE 1ST ===
if yesterday.day == 1:
    previous_month = (yesterday - timedelta(days=1)).strftime("%Y_%m")
    previous_file = output_dir_bt / f"BT_LaPalma_VJ102IMG_{previous_month}.nc"
    if previous_file.exists():
        previous_file.unlink()
        print(f"→ Previous monthly file deleted: {previous_file.name}")

# === PROCESS FILE FOR THE DAY ===
input_folder = input_base_path / f"{year}_{julian_day:03d}"
files = list(input_folder.glob("VJ102IMG.A*.nc"))

if not files:
    print("No files found to process.")
    exit()

bt_file = files[0]
print(f"→ Processing file: {bt_file.name}")
bt_da = process_to_monthly(bt_file, yesterday)
bt_mean = float(np.nanmean(bt_da.values))
print(f"→ Mean BT for {yesterday.strftime('%Y-%m-%d')}: {bt_mean:.2f} K")

# === SAVE / APPEND TO MONTHLY FILE ===
output_filename = f"BT_LaPalma_VJ102IMG_{year}_{month:02d}.nc"
output_path = output_dir_bt / output_filename

# Compression settings for output NetCDF
encoding = {
    "BT_I05": {"zlib": True, "complevel": 4, "dtype": "float32"},
    "latitude": {"zlib": True, "dtype": "float32"},
    "longitude": {"zlib": True, "dtype": "float32"},
}

# If the file exists, append new data; otherwise, create a new file
if output_path.exists():
    existing = xr.open_dataset(output_path)
    combined = xr.concat([existing, bt_da.to_dataset()], dim="time")
    combined = combined.sortby("time")
    existing.close()  # Important to avoid file lock issues
else:
    combined = bt_da.to_dataset()

# Attempt to save the output, handle permission errors by saving a backup version
try:
    combined.to_netcdf(output_path, encoding=encoding)
    print(f"✔︎ Updated: {output_path.name}")
except PermissionError:
    alt_path = output_path.parent / f"{output_path.stem}_v2.nc"
    combined.to_netcdf(alt_path, encoding=encoding)
    print(f"✔︎ Saved as alternative version: {alt_path.name}")