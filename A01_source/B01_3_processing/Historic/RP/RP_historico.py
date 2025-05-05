
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from variables import lat_max, lat_min, lon_max, lon_min

# === CONFIGURATION ===
# Resolve the current script path
script_path = Path(__file__).resolve()

# Locate the root project directory based on its name
project_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")

# Set input and output paths
base_path = project_dir / "A00_data" / "B_processed" / "Lanzarote" / "BT_daily_pixels"
output_nc = project_dir / "A00_data" / "B_processed" / "Lanzarote" / "Radiative_Power_by_Year_Month_Day" / "radiative_power_lanzarote.nc"

# Physical constant: Stefan-Boltzmann constant (W/m²·K⁴)
sigma = 5.67e-8  


# === DATE RANGE TO PROCESS ===
start_date = datetime(2025, 1, 1)       # Start date for processing
cutoff_date = datetime(1900, 2, 1)      # Reference cutoff date (fixed)
end_date = datetime.utcnow()            # End date is the current UTC time

# Initialize results lists
frp_results = []
new_dates = []

print("\n=== GENERATING VOLCANIC COOLING CURVE ===")

# Iterate over each date in the date range
date = start_date
while date <= end_date:
    year = date.year
    julian_day = date.timetuple().tm_yday
    date_str = date.strftime("%Y-%m-%d")

    # Locate the folder corresponding to the current day
    day_folder = base_path / f"{year}_{julian_day:03d}"
    files = sorted(day_folder.glob("*.nc"))

    if not files:
        print(f"{date_str} → No data available")
        date += timedelta(days=1)
        continue

    # Open the first available NetCDF file
    file = files[0]
    ds = xr.open_dataset(file)
    bt = ds["brightness_temperature"] if "brightness_temperature" in ds else ds["BT_I05"]
    lat = ds["latitude"].values
    lon = ds["longitude"].values

    # === APPLY GEOGRAPHIC MASK ===
    geo_mask = (lat >= lat_min) & (lat <= lat_max) & (lon >= lon_min) & (lon <= lon_max)
    bt = bt.where(geo_mask)

    # === CALCULATE AVERAGE BRIGHTNESS TEMPERATURE (BT) ===
    t_mean = float(np.nanmean(bt.values))

    if date > cutoff_date:
        t = (date - cutoff_date).days
        t_floor = 265         # Threshold temperature in Kelvin
        area = 1_250_000      # Area in m²
        scale = 2.5           # Scaling factor for FRP

    # === FRP CALCULATION ===
    if np.isnan(t_mean) or t_mean <= t_floor:
        frp = 0.0
        print(f"{date_str} → BTmean={t_mean:.2f} K <= floor={t_floor:.2f} → FRP=0")
    else:
        frp_raw = sigma * (t_mean**4 - t_floor**4) * area
        frp = (frp_raw / 1e6) * scale  # Convert to MW and scale
        print(f"{date_str} → BTmean={t_mean:.2f} K, FRP={frp:.2f} MW")

    # Save result for this date
    frp_results.append(frp)
    new_dates.append(np.datetime64(date.date()))
    date += timedelta(days=1)

# === SAVE RESULTS TO NETCDF ===
final_ds = xr.Dataset(
    {"FRP": (["time"], frp_results)},
    coords={"time": new_dates}
)
final_ds["FRP"].attrs["units"] = "MW"

# Ensure output directory exists, then save file
output_nc.parent.mkdir(parents=True, exist_ok=True)
final_ds.to_netcdf(output_nc)
print(f"\n✔︎ Final curve saved as: {output_nc.name}")