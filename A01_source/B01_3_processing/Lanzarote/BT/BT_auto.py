import os
import numpy as np
import xarray as xr
from netCDF4 import Dataset
from pathlib import Path
from datetime import datetime, timedelta

# === PATH SETUP ===
# Resolve script location and locate root project directory
script_path = Path(__file__).resolve()
project_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")

# Define input and output paths for Teide data
input_base_path = project_dir / "A00_data" / "B_raw" / "Teide"
output_dir_bt = project_dir / "A00_data" / "B_processed" / "Teide" / "BT_daily_pixels"
output_dir_bt.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist

# === PHYSICAL CONSTANTS ===
wavelength = 11.45  # µm (channel wavelength)
c1 = 1.191042e8     # First radiation constant [W·µm⁴/m²/sr]
c2 = 1.4387752e4    # Second radiation constant [µm·K]

def radiance_to_bt(radiance):
    """
    Converts radiance values to brightness temperature using Planck's inverse function.
    Filters out invalid or non-positive radiance values.
    """
    with np.errstate(divide='ignore', invalid='ignore'):
        bt = c2 / (wavelength * np.log((c1 / (radiance * wavelength**5)) + 1))
        bt = np.where((radiance > 0) & np.isfinite(bt), bt, np.nan)
    return bt

def process_to_monthly(nc_file, file_date):
    """
    Extracts and processes brightness temperature (BT) data from a NetCDF file.
    Returns a DataArray containing the BT scene and associated coordinates.
    """
    with Dataset(nc_file) as nc:
        obs = nc.groups['observation_data']
        i05 = obs["I05"][:]
        bt_i05 = radiance_to_bt(i05.filled(np.nan))

        # Get bounding box coordinates
        south = nc.getncattr('SouthBoundingCoordinate')
        north = nc.getncattr('NorthBoundingCoordinate')
        west = nc.getncattr('WestBoundingCoordinate')
        east = nc.getncattr('EastBoundingCoordinate')

        # Define lat/lon grid
        n_lines, n_pixels = bt_i05.shape
        latitudes = np.linspace(north, south, n_lines)
        longitudes = np.linspace(west, east, n_pixels)

    # Create xarray DataArray with metadata
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

# === TARGET DATE: YESTERDAY ===
yesterday = datetime.now() - timedelta(days=1)
year = yesterday.year
month = yesterday.month
julian_day = yesterday.timetuple().tm_yday

print(f"\n=== Processing BT for {yesterday.strftime('%Y-%m-%d')} ===")

# === DELETE PREVIOUS MONTH FILE IF TODAY IS THE 1ST ===
if yesterday.day == 1:
    previous_month = (yesterday - timedelta(days=1)).strftime("%Y_%m")
    previous_file = output_dir_bt / f"BT_Lanzarote_VJ102IMG_{previous_month}.nc"
    if previous_file.exists():
        previous_file.unlink()
        print(f"→ Previous monthly file deleted: {previous_file.name}")

# === PROCESS BT FILE FOR THE DAY ===
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

# === SAVE OR APPEND TO MONTHLY NETCDF FILE ===
nc_filename = f"BT_Teide_VJ102IMG_{year}_{month:02d}.nc"
nc_path = output_dir_bt / nc_filename

# Compression and encoding settings for NetCDF
encoding = {
    "BT_I05": {"zlib": True, "complevel": 4, "dtype": "float32"},
    "latitude": {"zlib": True, "dtype": "float32"},
    "longitude": {"zlib": True, "dtype": "float32"},
}

# If the file already exists, append the new data
if nc_path.exists():
    existing = xr.open_dataset(nc_path)
    combined = xr.concat([existing, bt_da.to_dataset()], dim="time")
    combined = combined.sortby("time")
    existing.close()  # Important to avoid file lock issues
else:
    combined = bt_da.to_dataset()

# Attempt to save to NetCDF file
try:
    combined.to_netcdf(nc_path, encoding=encoding)
    print(f"✔︎ Updated: {nc_path.name}")
except PermissionError:
    # Save alternative version if file is locked or in use
    alt_path = nc_path.parent / f"{nc_path.stem}_v2.nc"
    combined.to_netcdf(alt_path, encoding=encoding)
    print(f"✔︎ Saved as alternative version: {alt_path.name}")