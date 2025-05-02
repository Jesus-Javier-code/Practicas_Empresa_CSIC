import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# === CONFIGURATION ===
# Resolve the directory of the current script
script_path = Path(__file__).resolve()

# Locate the root project directory dynamically based on its name
project_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC-1")

# Define paths for input data and output NetCDF file
base_path = project_dir / "A00_data" / "B_processed" / "Lanzarote" / "BT_daily_pixels"
output_nc = project_dir / "A00_data" / "B_processed" / "Lanzarote" / "Radiative_Power_by_Year_Month_Day" / "radiative_power_lanzarote.nc"

# Stefan-Boltzmann constant (W/m²·K⁴)
sigma = 5.67e-8  

# Define the geographic bounding box for the region of interest (Lanzarote)
lat_min, lat_max = 28.95, 29.01
lon_min, lon_max = -13.76, -13.70



# === DATE RANGE TO PROCESS ===
# Set the start, cutoff, and end dates for processing
start_date = datetime(2025, 1, 1)
cutoff_date = datetime(1900, 2, 1)
end_date = datetime.utcnow()


# Initialize lists to store results
frp_results = []
new_dates = []

print("\n=== GENERATING VOLCANIC COOLING CURVE ===")

# Loop through each date within the specified range
date = start_date
while date <= end_date:
    year = date.year
    julian_day = date.timetuple().tm_yday
    date_str = date.strftime("%Y-%m-%d")

    # Define the folder for the current day and get the corresponding files
    day_folder = base_path / f"{year}_{julian_day:03d}"
    files = sorted(day_folder.glob("*.nc"))
    
    # If no files are found for the current day, skip this date
    if not files:
        print(f"{date_str} → No data available")
        date += timedelta(days=1)
        continue

    # Open the first available file and extract relevant data
    file = files[0]
    ds = xr.open_dataset(file)
    bt = ds["brightness_temperature"] if "brightness_temperature" in ds else ds["BT_I05"]
    lat = ds["latitude"].values
    lon = ds["longitude"].values

    # === APPLY GEOGRAPHIC MASK ===
    # Filter the data to include only the region within the specified bounding box
    geo_mask = (lat >= lat_min) & (lat <= lat_max) & (lon >= lon_min) & (lon <= lon_max)
    bt = bt.where(geo_mask)

    # === CALCULATE AVERAGE BT (Brightness Temperature) ===
    t_mean = float(np.nanmean(bt.values))

    if date > cutoff_date:
        t = (date - cutoff_date).days
        t_floor = 270 
        area = 750_000 
        scale = 1.5 

    # If the average BT is less than or equal to the calculated temperature floor, set FRP to 0
    if np.isnan(t_mean) or t_mean <= t_floor:
        frp = 0.0
        print(f"{date_str} → BTmean={t_mean:.2f} K <= floor={t_floor:.2f} → FRP=0")
    else:
        # Calculate raw FRP and apply scaling factor
        frp_raw = sigma * (t_mean**4 - t_floor**4) * area
        frp = (frp_raw / 1e6) * scale  # Convert to MW and apply scaling factor
        print(f"{date_str} → BTmean={t_mean:.2f} K, FRP={frp:.2f} MW")

    # Store the results for later saving
    frp_results.append(frp)
    new_dates.append(np.datetime64(date.date()))
    date += timedelta(days=1)

# === SAVE RESULTS TO NetCDF ===
# Create a new dataset for the FRP results and save it to a NetCDF file
final_ds = xr.Dataset(
    {"FRP": (["time"], frp_results)},
    coords={"time": new_dates}
)
final_ds["FRP"].attrs["units"] = "MW"

# Ensure the output directory exists and save the NetCDF file
output_nc.parent.mkdir(parents=True, exist_ok=True)
final_ds.to_netcdf(output_nc)
print(f"\n✔︎ Final curve saved as: {output_nc.name}")

