import numpy as np
from netCDF4 import Dataset
from pathlib import Path
import re
from datetime import datetime, timedelta

# === CONFIGURE YOUR DATE RANGE HERE ===
start_date = datetime(2021, 12, 1)
end_date = datetime(2025, 4, 20)

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
    Processes a NetCDF file: extracts radiance data, converts it to
    brightness temperature, and saves the result as a new NetCDF.

    Parameters:
        nc_file (Path): Input NetCDF file path.
        output_base_path (Path): Output directory base path.
    """
    with Dataset(nc_file) as nc:
        obs = nc.groups['observation_data']

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

    # Create output folder and file
    output_folder = output_base_path / f"{yyyy}_{ddd}"
    output_folder.mkdir(parents=True, exist_ok=True)
    output_nc = output_folder / f"BT_Teide_VJ102IMG_{yyyy}_{ddd}.nc"

    # Write the NetCDF file
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

# === PATH CONFIGURATION ===
script_path = Path(__file__).resolve().parent
input_base_path = script_path / "A00_data/B_raw/data_VJ"
output_path = script_path / "A00_data/B_processed/Teide/BT_daily_pixels"

# === LOOP THROUGH FILES AND FILTER BY DATE ===
for folder in sorted(input_base_path.glob("20*_???")):
    for file in folder.glob("VJ102IMG.A*.nc"):
        match = re.search(r"A(\d{4})(\d{3})", file.name)
        if match:
            yyyy, ddd = match.groups()
            file_date = datetime.strptime(f"{yyyy}{ddd}", "%Y%j")
            if start_date <= file_date <= end_date:
                process_nc_file(file, output_path)