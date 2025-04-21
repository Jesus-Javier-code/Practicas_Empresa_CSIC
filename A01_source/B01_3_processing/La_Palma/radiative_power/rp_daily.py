import numpy as np
import xarray as xr
from datetime import datetime, timedelta
from pathlib import Path

# === CONFIGURACIÓN ===
script_path = Path(__file__).resolve()
proyecto_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")

ruta_bt = proyecto_dir / "A00_data" / "B_processed" / "La_Palma" / "BT_daily_pixels"
ruta_ref = proyecto_dir / "A00_data" / "B_processed" / "La_Palma" / "REF"
salida_nc = proyecto_dir / "A00_data" / "B_processed" / "La_Palma" / "Radiative_Power_by_Year_Month_Day" / "radiative_power.nc"

area_pixel = 140625  # m²
sigma = 5.67e-8      # W/m²·K⁴

# === DÍA ANTERIOR
ayer = datetime.utcnow().date() - timedelta(days=1)
año = ayer.year
mes = ayer.month
dia_juliano = ayer.timetuple().tm_yday
fecha_str = ayer.strftime("%Y-%m-%d")

# === ARCHIVOS
archivo_bt = ruta_bt / f"{año}_{dia_juliano:03d}" / f"BT_LaPalma_VJ102IMG_{año}_{dia_juliano:03d}.nc"
archivo_ref = ruta_ref / f"Ref_{año}_{mes:02d}.nc"

# === VALIDACIÓN
if not archivo_bt.exists():
    print(f"{fecha_str} → No existe archivo BT.")
    exit()

if not archivo_ref.exists():
    print(f"{fecha_str} → No existe REF mensual.")
    exit()

# === CARGAR DATOS
bt_ds = xr.open_dataset(archivo_bt)
ref_ds = xr.open_dataset(archivo_ref)

bt = bt_ds["brightness_temperature"]
ref = ref_ds["brightness_temperature_REF"]

# === Alinear si hace falta
if bt.shape != ref.shape:
    bt = bt.interp_like(ref, method="linear")
    print(f"{fecha_str}: Interpolación aplicada.")

# === Cálculo FRP
t_obs = bt.values
t_ref = ref.values
valid = np.isfinite(t_obs) & np.isfinite(t_ref)

if np.sum(valid) == 0:
    frp_total = 0.0
else:
    frp_px = sigma * (t_obs[valid]**4 - t_ref[valid]**4) * area_pixel
    frp_px = np.where(frp_px > 0, frp_px, 0)
    frp_total = np.nansum(frp_px) / 1e6  # MW

print(f"\n→ {fecha_str}: FRP = {frp_total:.2f} MW")

# === FILTRO DE CALIDAD ===
if frp_total > 500 or frp_total < 10:
    print(f"✘ {fecha_str}: FRP fuera de rango esperado. Valor descartado.")
    exit()

# === GUARDAR A NetCDF ACUMULATIVO
nuevo_ds = xr.Dataset(
    {"FRP": (["time"], [frp_total])},
    coords={"time": [np.datetime64(ayer)]}
)
nuevo_ds["FRP"].attrs["units"] = "MW"

if salida_nc.exists():
    ds_existente = xr.open_dataset(salida_nc)
    if np.datetime64(ayer) in ds_existente.time.values:
        print("Ya existe esta fecha en el archivo. No se sobrescribe.")
    else:
        combinado = xr.concat([ds_existente, nuevo_ds], dim="time")
        combinado = combinado.sortby("time")
        combinado.to_netcdf(salida_nc)
        print("✔︎ Día añadido al NetCDF existente.")
else:
    salida_nc.parent.mkdir(parents=True, exist_ok=True)
    nuevo_ds.to_netcdf(salida_nc)
    print("✔︎ NetCDF nuevo creado.")