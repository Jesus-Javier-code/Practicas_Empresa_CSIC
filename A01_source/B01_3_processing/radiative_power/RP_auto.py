import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta

# === CONFIGURATION ===
# Resolve the directory of the current script
script_path = Path(__file__).resolve()

# Locate the root project directory dynamically based on its name
project_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")

# Define paths for input data and output NetCDF file
base_path = project_dir / "00_data" / "processed" / "BT_daily_pixels"
output_nc = project_dir / "00_data" / "processed" / "Radiative_Power_by_Year_Month_Day" / "radiative_power_data.nc"

# Stefan-Boltzmann constant (W/m²·K⁴)
sigma = 5.67e-8  

# Define the geographic bounding box for the region of interest (La Palma)
lat_min, lat_max = 28.54, 28.57
lon_min, lon_max = -17.74, -17.70

# === YESTERDAY'S DATE ===
# Get yesterday's date to process data for the previous day
yesterday = datetime.now() - timedelta(days=1)
year = yesterday.year
julian_day = yesterday.timetuple().tm_yday
date_str = yesterday.strftime("%Y-%m-%d")

print(f"\n=== GENERATING VOLCANIC COOLING CURVE FOR {date_str} ===")

# === SEARCH FOR FILES FROM YESTERDAY ===
# Find the directory corresponding to yesterday's date
day_folder = base_path / f"{year}_{julian_day:03d}"
files = sorted(day_folder.glob("*.nc"))

# If no files are found for the day, exit
if not files:
    print(f"{date_str} → No data available")
    exit()

# === READ FILE AND PROCESS ===
# Open the first file and extract the brightness temperature (BT) data
file = files[0]
ds = xr.open_dataset(file)
bt = ds["brightness_temperature"] if "brightness_temperature" in ds else ds["BT_I05"]
lat = ds["latitude"].values
lon = ds["longitude"].values

# === APPLY GEOGRAPHIC MASK ===
# Filter the data to include only the region within the specified bounding box (La Palma)
geo_mask = (lat >= lat_min) & (lat <= lat_max) & (lon >= lon_min) & (lon <= lon_max)
bt = bt.where(geo_mask)

# === CALCULATE AVERAGE BT (Brightness Temperature) ===
# Calculate the average BT for the masked region
t_mean = float(np.nanmean(bt.values))

# === CALCULATE FRP BASED ON PHASE 2 ===
cutoff_date = datetime(2022, 2, 1)
if yesterday >= cutoff_date:
    # PHASE 2: Slow cooling
    t = (yesterday - cutoff_date).days
    total_phase2 = (datetime.utcnow() - cutoff_date).days
    f2 = t / total_phase2
    t_floor = 275 + 5 * f2
    area = 1_000_000 - 500_000 * f2
    scale = 1.5 - 1.0 * f2
else:
    # If the date is before phase 2, skip processing
    print("The date is before phase 2, no processing will be done.")
    exit()

# If the average BT is less than or equal to the calculated temperature floor, set FRP to 0
if np.isnan(t_mean) or t_mean <= t_floor:
    frp = 0.0
    print(f"{date_str} → BTmean={t_mean:.2f} K <= floor={t_floor:.2f} → FRP=0")
else:
    # Calculate raw FRP and apply scaling factor
    frp_raw = sigma * (t_mean**4 - t_floor**4) * area
    frp = (frp_raw / 1e6) * scale  # Convert to MW and apply scaling factor
    print(f"{date_str} → BTmean={t_mean:.2f} K, FRP={frp:.2f} MW")

# === SAVE RESULTS TO NetCDF ===
# Store the FRP results in a list and save it in a new NetCDF file
frp_results = [frp]
new_dates = [np.datetime64(yesterday.date())]

final_ds = xr.Dataset(
    {"FRP": (["time"], frp_results)},
    coords={"time": new_dates}
)
final_ds["FRP"].attrs["units"] = "MW"

# Ensure the output directory exists and save the NetCDF file
output_nc.parent.mkdir(parents=True, exist_ok=True)

# === SAVE OR APPEND TO NetCDF ===
# Check if the file already exists
if output_nc.exists():
    existing_ds = xr.open_dataset(output_nc)
    
    # Concatenate new data along time dimension
    final_ds = xr.concat([existing_ds, final_ds], dim="time")
    
    # Drop duplicate times if any
    final_ds = final_ds.sel(time=~final_ds.get_index("time").duplicated())

# Save the updated dataset
final_ds.to_netcdf(output_nc)
print(f"\n✔︎ Updated curve saved in: {output_nc.name}")