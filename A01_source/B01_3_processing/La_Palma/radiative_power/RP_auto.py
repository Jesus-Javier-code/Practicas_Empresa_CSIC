import os
import numpy as np
import xarray as xr
from pathlib import Path
from datetime import datetime, timedelta

# === CONFIGURATION ===
# Get the script path and locate the root project directory
script_path = Path(__file__).resolve()
project_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")

# Define paths to input and output directories
bt_dir = project_dir / "A00_data" / "B_processed" / "La_Palma" / "BT_daily_pixels"
output_nc = project_dir / "A00_data" / "B_processed" / "La_Palma" / "Radiative_Power_by_Year_Month_Day" / "radiative_power.nc"
output_nc.parent.mkdir(parents=True, exist_ok=True)

sigma = 5.67e-8  # Stefan-Boltzmann constant

# === REGION OF INTEREST (La Palma) ===
lat_min, lat_max = 28.54, 28.57
lon_min, lon_max = -17.74, -17.70

# === YESTERDAY'S DATE ===
yesterday = datetime.now() - timedelta(days=1)
year = yesterday.year
month = yesterday.month
date_str = yesterday.strftime("%Y-%m-%d")

print(f"\n=== CALCULATING FRP FOR {date_str} ===")

# === LOAD MONTHLY FILE ===
bt_file = bt_dir / f"BT_LaPalma_VJ102IMG_{year}_{month:02d}.nc"
if not bt_file.exists():
    print(f"{date_str} → Monthly file not found: {bt_file.name}")
    exit()

ds = xr.open_dataset(bt_file)

if "BT_I05" not in ds:
    print(f"{date_str} → Variable BT_I05 not found.")
    exit()

# === CHECK IF THE TARGET DATE EXISTS ===
time_target = np.datetime64(yesterday.date())
if time_target not in ds.time.values:
    print(f"{date_str} → No data available for this date in the file.")
    exit()

# === EXTRACT SCENE AND APPLY GEOGRAPHIC MASK ===
bt = ds["BT_I05"].sel(time=time_target)
lat = ds["latitude"]
lon = ds["longitude"]

geo_mask = (lat >= lat_min) & (lat <= lat_max) & (lon >= lon_min) & (lon <= lon_max)
bt = bt.where(geo_mask)

# === FRP CALCULATION ===
t_mean = float(np.nanmean(bt.values))

# Conditional FRP calculation based on "Phase 2" (starting Feb 1, 2022)
cutoff = datetime(2022, 2, 1)
if yesterday >= cutoff:
    t = (yesterday - cutoff).days
    total = (datetime.utcnow() - cutoff).days
    f2 = t / total
    t_floor = 265 + 5 * f2
    area = 1_000_000 - 500_000 * f2
    scale = 1.5 - 1.0 * f2
else:
    print(f"{date_str} → Before Phase 2. FRP not computed.")
    exit()

# Final FRP computation with quality control
if np.isnan(t_mean) or t_mean <= t_floor:
    frp = 0.0
    print(f"{date_str} → BTmean={t_mean:.2f} K <= floor={t_floor:.2f} → FRP=0")
else:
    frp_raw = sigma * (t_mean**4 - t_floor**4) * area
    frp = (frp_raw / 1e6) * scale  # Convert to megawatts and apply scale
    print(f"{date_str} → BTmean={t_mean:.2f} K, FRP={frp:.2f} MW")

# === QUALITY FILTER ===
if frp > 400:
    print(f"✘ {date_str} → FRP exceeds expected range. Value discarded.")
    exit()

# === CREATE AND SAVE DATA ===
new_ds = xr.Dataset(
    {"FRP": (["time"], [frp])},
    coords={"time": [time_target]}
)
new_ds["FRP"].attrs["units"] = "MW"

# Append to existing NetCDF or create a new one
if output_nc.exists():
    existing = xr.open_dataset(output_nc)
    if time_target in existing.time.values:
        print(f"{date_str} → Entry already exists. No overwrite.")
    else:
        combined = xr.concat([existing, new_ds], dim="time").sortby("time")
        existing.close()
        combined.to_netcdf(output_nc, mode="w")
        print(f"✔︎ FRP appended to {output_nc.name}")
else:
    new_ds.to_netcdf(output_nc)
    print(f"✔︎ NetCDF created: {output_nc.name}")