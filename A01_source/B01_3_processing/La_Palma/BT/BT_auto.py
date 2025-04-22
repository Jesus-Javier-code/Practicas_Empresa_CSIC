import os
import glob
import numpy as np
import xarray as xr
from netCDF4 import Dataset
from pathlib import Path
import re
from datetime import datetime, timedelta


# Ruta base relativa al script
script_path = Path(__file__).resolve()
proyecto_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")

# Define rutas relativas a la ubicación del proyecto
input_base_path = proyecto_dir / "A00_data" / "B_raw" / "La_Palma" 
output_base_path = proyecto_dir / "A00_data" / "B_processed" / "La_Palma" / "BT_daily_pixels"

# Create output directory if it doesn't exist
output_base_path.mkdir(parents=True, exist_ok=True)

# === VOLCANO REGION ===
lat_min = 28.55
lat_max = 28.65
lon_min = -17.93
lon_max = -17.80

# === FUNCTIONS ===
def radiance_to_bt(radiance, wavelength_um):
    """
    Converts radiance values to brightness temperature (BT) using Planck's law.
    
    Parameters:
        radiance (ndarray): Radiance values.
        wavelength_um (float): Wavelength in micrometers.
        
    Returns:
        ndarray: Brightness temperature in Kelvin.
    """
    c1 = 1.191042e8   # W·µm⁴/m²/sr
    c2 = 1.4387752e4  # µm·K
    with np.errstate(divide='ignore', invalid='ignore'):
        bt = c2 / (wavelength_um * np.log((c1 / (radiance * wavelength_um**5)) + 1))
        bt = np.where((radiance > 0) & np.isfinite(bt), bt, np.nan)
    return bt

def process_nc_file(nc_file, output_base_path):
    """
    Processes a NetCDF file, extracts radiance from I05 channel,
    converts it to brightness temperature (BT), and saves the output.

    Parameters:
        nc_file (Path): Path to the input NetCDF file.
        output_base_path (Path): Base path for output files.
    """
    with Dataset(nc_file) as nc:
        # Acceder al grupo 'observation_data'
        obs = nc.groups['observation_data']

        # Acceder a la variable 'I05' dentro del grupo 'observation_data'
        i05 = obs["I05"][:]
        bt_i05 = radiance_to_bt(i05.filled(np.nan), 11.45)

        bt_min = np.nanmin(bt_i05)
        bt_max = np.nanmax(bt_i05)
        bt_mean = np.nanmean(bt_i05)
        print(f"\nFile: {nc_file.name}")
        print(f"BT min: {bt_min:.2f} K")
        print(f"BT max: {bt_max:.2f} K")
        print(f"BT mean: {bt_mean:.2f} K")

        south = nc.getncattr('SouthBoundingCoordinate')
        north = nc.getncattr('NorthBoundingCoordinate')
        west = nc.getncattr('WestBoundingCoordinate')
        east = nc.getncattr('EastBoundingCoordinate')

        n_lines, n_pixels = i05.shape
        latitudes = np.linspace(north, south, n_lines)
        longitudes = np.linspace(west, east, n_pixels)
        lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)

    # Extract date from filename
    match = re.search(r"A(\d{4})(\d{3})", nc_file.name)
    if not match:
        print(f"Could not extract date from {nc_file.name}")
        return
    yyyy, ddd = match.groups()
    file_date = datetime.strptime(f"{yyyy}{ddd}", "%Y%j")

    # Create output folder and filename
    output_folder = output_base_path / f"{yyyy}_{ddd}"
    output_folder.mkdir(parents=True, exist_ok=True)
    output_nc = output_folder / f"BT_LaPalma_VJ102IMG_{yyyy}_{ddd}.nc"

    # Write output NetCDF
    with Dataset(output_nc, "w", format="NETCDF4") as dst:
        dst.createDimension("rows", bt_i05.shape[0])
        dst.createDimension("cols", bt_i05.shape[1])

        bt_var = dst.createVariable("BT_I05", "f4", ("rows", "cols"), fill_value=np.nan)
        bt_var.units = "K"
        bt_var.long_name = "Brightness Temperature - Channel I05 (11.45 µm)"
        bt_var[:, :] = bt_i05

        lat_var = dst.createVariable("latitude", "f4", ("rows", "cols"))
        lon_var = dst.createVariable("longitude", "f4", ("rows", "cols"))
        lat_var.units = "degrees_north"
        lon_var.units = "degrees_east"
        lat_var[:, :] = lat_grid
        lon_var[:, :] = lon_grid

        dst.title = f"Daily Brightness Temperature - {yyyy}_{ddd}"
        dst.source_file = nc_file.name

    print(f"Saved: {output_nc}")

# === YESTERDAY'S DATE ===
yesterday = datetime.now() - timedelta(days=1)
year_yesterday = yesterday.strftime("%Y")
julian_day_yesterday = yesterday.strftime("%j")  # Julian day (001–366)

print(f"\n=== Processing files for {yesterday.strftime('%Y-%m-%d')} (Julian day {julian_day_yesterday}) ===")

# === FIND FILES FROM YESTERDAY ===
# Use the absolute path for the folder corresponding to yesterday's date
yesterday_folder = input_base_path / f"{year_yesterday}_{julian_day_yesterday}"
files = glob.glob(str(yesterday_folder / "VJ102IMG.A*.nc"))

print(f"Files found: {len(files)}")

if len(files) == 0:
    print(f"No data for {yesterday.strftime('%Y-%m-%d')} ({yesterday_folder})")
    exit()

# Convert the file paths from string to Path objects
files = [Path(file) for file in files]  # Convert each file path to a Path object

# === PROCESS FILES ===
for file in files:
    print(f"\nFile: {file.name}")  # Now file is a Path object, so this works correctly
    process_nc_file(file, output_base_path)