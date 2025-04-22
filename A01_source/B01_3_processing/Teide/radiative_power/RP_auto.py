import os
import numpy as np
import xarray as xr
from pathlib import Path
from datetime import datetime, timedelta

# === CONFIGURACIÓN ===
script_path = Path(__file__).resolve()
project_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")

bt_dir = project_dir / "A00_data" / "B_processed" / "Teide" / "BT_daily_pixels"
output_nc = project_dir / "A00_data" / "B_processed" / "Teide" / "Radiative_Power_by_Year_Month_Day" / "radiative_power_teide.nc"
output_nc.parent.mkdir(parents=True, exist_ok=True)

sigma = 5.67e-8  # Constante de Stefan-Boltzmann

# === REGIÓN DE INTERÉS (Teide) ===
lat_min, lat_max = 28.2717, 28.2744
lon_min, lon_max = -16.6408, -16.6380


# === FECHA DE AYER ===
ayer = datetime.now() - timedelta(days=1)
año = ayer.year
mes = ayer.month
fecha_str = ayer.strftime("%Y-%m-%d")

print(f"\n=== CALCULANDO FRP PARA {fecha_str} ===")

# === CARGAR ARCHIVO MENSUAL ===
archivo_bt = bt_dir / f"BT_LaPalma_VJ102IMG_{año}_{mes:02d}.nc"
if not archivo_bt.exists():
    print(f"{fecha_str} → Archivo mensual no encontrado: {archivo_bt.name}")
    exit()

ds = xr.open_dataset(archivo_bt)

if "BT_I05" not in ds:
    print(f"{fecha_str} → Variable BT_I05 no encontrada.")
    exit()

# === COMPROBAR QUE EXISTE LA FECHA ===
time_target = np.datetime64(ayer.date())
if time_target not in ds.time.values:
    print(f"{fecha_str} → No hay datos para este día en el archivo.")
    exit()

# === EXTRAER ESCENA Y APLICAR MÁSCARA GEOGRÁFICA ===
bt = ds["BT_I05"].sel(time=time_target)
lat = ds["latitude"]
lon = ds["longitude"]

mascara_geo = (lat >= lat_min) & (lat <= lat_max) & (lon >= lon_min) & (lon <= lon_max)
bt = bt.where(mascara_geo)

# === CÁLCULO DE FRP ===
t_mean = float(np.nanmean(bt.values))

cutoff = datetime(2022, 2, 1)
if ayer >= cutoff:
    t = (ayer - cutoff).days
    total = (datetime.utcnow() - cutoff).days
    f2 = t / total
    t_floor = 265 + 5 * f2
    area = 1_000_000 - 500_000 * f2
    scale = 1.5 - 1.0 * f2
else:
    print(f"{fecha_str} → Antes del inicio de la fase 2. No se calcula.")
    exit()

if np.isnan(t_mean) or t_mean <= t_floor:
    frp = 0.0
    print(f"{fecha_str} → BTmean={t_mean:.2f} K <= floor={t_floor:.2f} → FRP=0")
else:
    frp_raw = sigma * (t_mean**4 - t_floor**4) * area
    frp = (frp_raw / 1e6) * scale
    print(f"{fecha_str} → BTmean={t_mean:.2f} K, FRP={frp:.2f} MW")

# === FILTRO DE CALIDAD ===
if frp > 400:
    print(f"✘ {fecha_str} → FRP fuera de rango esperado. Valor descartado.")
    exit()

# === CREAR Y GUARDAR ===
nuevo_ds = xr.Dataset(
    {"FRP": (["time"], [frp])},
    coords={"time": [time_target]}
)
nuevo_ds["FRP"].attrs["units"] = "MW"

if output_nc.exists():
    acumulado = xr.open_dataset(output_nc)
    if time_target in acumulado.time.values:
        print(f"{fecha_str} → Ya existe en el archivo. No se sobrescribe.")
    else:
        combinado = xr.concat([acumulado, nuevo_ds], dim="time").sortby("time")
        acumulado.close()
        combinado.to_netcdf(output_nc, mode="w")
        print(f"✔︎ FRP añadido a {output_nc.name}")
else:
    nuevo_ds.to_netcdf(output_nc)
    print(f"✔︎ NetCDF creado: {output_nc.name}")