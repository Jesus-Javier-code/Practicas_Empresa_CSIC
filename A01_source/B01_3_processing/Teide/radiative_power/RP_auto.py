import os
import numpy as np
import xarray as xr
from pathlib import Path
from datetime import datetime, timedelta

# === CONFIGURATION ===
# Resolve script path and locate root project directory
script_path = Path(__file__).resolve()
project_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")

# Define input directory for BT data and output path for FRP results
bt_dir = project_dir / "A00_data" / "B_processed" / "Teide" / "BT_daily_pixels"
output_nc = project_dir / "A00_data" / "B_processed" / "Teide" / "Radiative_Power_by_Year_Month_Day" / "radiative_power_teide.nc"
output_nc.parent.mkdir(parents=True, exist_ok=True)

# Stefan-Boltzmann constant
sigma = 5.67e-8  # W/m²·K⁴

# === REGION OF INTEREST (Teide crater) ===
lat_min, lat_max = 28.2717, 28.2744
lon_min, lon_max = -16.6408, -16.6380

# === TARGET DATE: YESTERDAY ===
yesterday = datetime.now() - timedelta(days=1)
year = yesterday.year
month = yesterday.month
date_str = yesterday.strftime("%Y-%m-%d")

print(f"\n=== CALCULATING FRP FOR {date_str} ===")

# === LOAD MONTHLY BT FILE ===
bt_file = bt_dir / f"BT_Teide_VJ102IMG_{year}_{month:02d}.nc"
if not bt_file.exists():
    print(f"{date_str} → Monthly file not found: {bt_file.name}")
    exit()

ds = xr.open_dataset(bt_file)

if "BT_I05" not in ds:
    print(f"{date_str} → Variable 'BT_I05' not found.")
    exit()

# === CHECK THAT THE DATE EXISTS IN THE FILE ===
time_target = np.datetime64(yesterday.date())
if time_target not in ds.time.values:
    print(f"{date_str} → No data for this date in the file.")
    exit()

# === EXTRACT BT SCENE AND APPLY GEOGRAPHIC MASK ===
bt = ds["BT_I05"].sel(time=time_target)
lat = ds["latitude"]
lon = ds["longitude"]

geo_mask = (lat >= lat_min) & (lat <= lat_max) & (lon >= lon_min) & (lon <= lon_max)
bt = bt.where(geo_mask)

# === FRP CALCULATION ===
t_mean = float(np.nanmean(bt.values))

cutoff = datetime(2022, 2, 1)
if yesterday >= cutoff:
    t = (yesterday - cutoff).days
    total = (datetime.utcnow() - cutoff).days
    f2 = t / total
    t_floor = 265 + 5 * f2     # Dynamic temperature threshold
    area = 1_000_000 - 500_000 * f2  # Adjusted area (m²)
    scale = 1.5 - 1.0 * f2     # Scaling factor
else:
    print(f"{date_str} → Before Phase 2 start. Calculation skipped.")
    exit()

# Check if BT is valid and above threshold
if np.isnan(t_mean) or t_mean <= t_floor:
    frp = 0.0
    print(f"{date_str} → BTmean={t_mean:.2f} K <= floor={t_floor:.2f} → FRP=0")
else:
    frp_raw = sigma * (t_mean**4 - t_floor**4) * area
    frp = (frp_raw / 1e6) * scale  # Convert to MW
    print(f"{date_str} → BTmean={t_mean:.2f} K, FRP={frp:.2f} MW")

# === QUALITY FILTER ===
if frp > 400:
    print(f"✘ {date_str} → FRP exceeds expected range. Value discarded.")
    exit()

# === CREATE AND SAVE TO NETCDF ===
new_ds = xr.Dataset(
    {"FRP": (["time"], [frp])},
    coords={"time": [time_target]}
)
new_ds["FRP"].attrs["units"] = "MW"

# Append to existing file or create a new one
if output_nc.exists():
    existing = xr.open_dataset(output_nc)
    if time_target in existing.time.values:
        print(f"{date_str} → Entry already exists. Not overwritten.")
    else:
        combined = xr.concat([existing, new_ds], dim="time").sortby("time")
        existing.close()
        combined.to_netcdf(output_nc, mode="w")
        print(f"✔︎ FRP added to {output_nc.name}")
else:
    new_ds.to_netcdf(output_nc)
    print(f"✔︎ NetCDF created: {output_nc.name}")