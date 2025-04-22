import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta

# === CONFIGURATION ===
script_path = Path(__file__).resolve()
project_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")

base_path = project_dir / "A00_data" / "B_processed" / "La_Palma" / "BT_daily_pixels"
output_nc = project_dir / "A00_data" / "B_processed" / "La_Palma" / "Radiative_Power_by_Year_Month_Day" / "radiative_power_data.nc"

sigma = 5.67e-8  # Stefan-Boltzmann constant

lat_min, lat_max = 28.54, 28.57
lon_min, lon_max = -17.74, -17.70

# === YESTERDAY'S DATE ===
yesterday = datetime.now() - timedelta(days=1)
year = yesterday.year
julian_day = yesterday.timetuple().tm_yday
date_str = yesterday.strftime("%Y-%m-%d")

print(f"\n=== GENERATING VOLCANIC COOLING CURVE FOR {date_str} ===")

# === SEARCH FOR FILES ===
day_folder = base_path / f"{year}_{julian_day:03d}"
files = sorted(day_folder.glob("*.nc"))

if not files:
    print(f"{date_str} → No data available")
    exit()

file = files[0]
ds = xr.open_dataset(file)
bt = ds["brightness_temperature"] if "brightness_temperature" in ds else ds["BT_I05"]
lat = ds["latitude"].values
lon = ds["longitude"].values

# === GEOGRAPHIC MASK ===
geo_mask = (lat >= lat_min) & (lat <= lat_max) & (lon >= lon_min) & (lon <= lon_max)
bt = bt.where(geo_mask)

# === AVERAGE BT ===
t_mean = float(np.nanmean(bt.values))

# === PHASE 2 COOLING ===
cutoff_date = datetime(2022, 2, 1)
if yesterday >= cutoff_date:
    t = (yesterday - cutoff_date).days
    total_phase2 = (datetime.utcnow() - cutoff_date).days
    f2 = t / total_phase2
    t_floor = 275 + 5 * f2
    area = 1_000_000 - 500_000 * f2
    scale = 1.5 - 1.0 * f2
else:
    print("The date is before phase 2, no processing will be done.")
    exit()

# === FRP CALCULATION ===
if np.isnan(t_mean) or t_mean <= t_floor:
    frp = 0.0
    print(f"{date_str} → BTmean={t_mean:.2f} K <= floor={t_floor:.2f} → FRP=0")
else:
    frp_raw = sigma * (t_mean**4 - t_floor**4) * area
    frp = (frp_raw / 1e6) * scale
    print(f"{date_str} → BTmean={t_mean:.2f} K, FRP={frp:.2f} MW")

# === QUALITY FILTER ===
if frp > 400:
    print(f"✘ {date_str} → FRP fuera de rango esperado. Valor descartado.")
    exit()

# === CREATE DATASET ===
new_time = np.datetime64(yesterday.date())
new_ds = xr.Dataset(
    {"FRP": (["time"], [frp])},
    coords={"time": [new_time]}
)
new_ds["FRP"].attrs["units"] = "MW"

output_nc.parent.mkdir(parents=True, exist_ok=True)

# === ACCUMULATE SAFELY ===
if output_nc.exists():
    existing_ds = xr.open_dataset(output_nc)
    if new_time in existing_ds.time.values:
        print(f"{date_str} → Date already exists. Skipping save.")
    else:
        combined = xr.concat([existing_ds, new_ds], dim="time").sortby("time")
        combined.to_netcdf(output_nc)
        print(f"✔︎ Appended new data to: {output_nc.name}")
else:
    new_ds.to_netcdf(output_nc)
    print(f"✔︎ NetCDF creado: {output_nc.name}")