import os
import numpy as np
import xarray as xr
from netCDF4 import Dataset
from pathlib import Path
from datetime import datetime, timedelta

# === RUTAS ===
script_path = Path(__file__).resolve()
proyecto_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")

input_base_path = proyecto_dir / "A00_data" / "B_raw" / "La_Palma"
output_dir_bt = proyecto_dir / "A00_data" / "B_processed" / "La_Palma" / "BT_daily_pixels"
output_dir_bt.mkdir(parents=True, exist_ok=True)

# === CONSTANTES ===
wavelength = 11.45
c1 = 1.191042e8   # W·µm⁴/m²/sr
c2 = 1.4387752e4  # µm·K

def radiance_to_bt(radiance):
    with np.errstate(divide='ignore', invalid='ignore'):
        bt = c2 / (wavelength * np.log((c1 / (radiance * wavelength**5)) + 1))
        bt = np.where((radiance > 0) & np.isfinite(bt), bt, np.nan)
    return bt

def process_to_monthly(nc_file, file_date):
    with Dataset(nc_file) as nc:
        obs = nc.groups['observation_data']
        i05 = obs["I05"][:]
        bt_i05 = radiance_to_bt(i05.filled(np.nan))

        south = nc.getncattr('SouthBoundingCoordinate')
        north = nc.getncattr('NorthBoundingCoordinate')
        west = nc.getncattr('WestBoundingCoordinate')
        east = nc.getncattr('EastBoundingCoordinate')

        n_lines, n_pixels = bt_i05.shape
        latitudes = np.linspace(north, south, n_lines)
        longitudes = np.linspace(west, east, n_pixels)

    da = xr.DataArray(
        bt_i05[np.newaxis, :, :],
        dims=("time", "y", "x"),
        coords={
            "time": [np.datetime64(file_date.date())],
            "y": np.arange(n_lines),
            "x": np.arange(n_pixels),
            "latitude": ("y", latitudes),
            "longitude": ("x", longitudes),
        },
        name="BT_I05"
    )
    return da

# === FECHA DE AYER ===
ayer = datetime.now() - timedelta(days=1)
año = ayer.year
mes = ayer.month
dia_juliano = ayer.timetuple().tm_yday

print(f"\n=== Procesando BT para {ayer.strftime('%Y-%m-%d')} ===")

# === ELIMINAR ARCHIVO DEL MES ANTERIOR SI ES DÍA 1 ===
if ayer.day == 1:
    mes_anterior = (ayer - timedelta(days=1)).strftime("%Y_%m")
    archivo_anterior = output_dir_bt / f"BT_LaPalma_VJ102IMG_{mes_anterior.replace('_', '_')}.nc"
    if archivo_anterior.exists():
        archivo_anterior.unlink()
        print(f"→ Archivo acumulado anterior eliminado: {archivo_anterior.name}")

# === PROCESAR ARCHIVO DEL DÍA ===
input_folder = input_base_path / f"{año}_{dia_juliano:03d}"
archivos = list(input_folder.glob("VJ102IMG.A*.nc"))

if not archivos:
    print("No hay archivos para procesar.")
    exit()

archivo_bt = archivos[0]
print(f"→ Procesando archivo: {archivo_bt.name}")
bt_da = process_to_monthly(archivo_bt, ayer)
bt_mean = float(np.nanmean(bt_da.values))
print(f"→ BT media del {ayer.strftime('%Y-%m-%d')}: {bt_mean:.2f} K")

# === GUARDAR / ACUMULAR EN ARCHIVO MENSUAL ===
nombre_nc = f"BT_LaPalma_VJ102IMG_{año}_{mes:02d}.nc"
ruta_nc = output_dir_bt / nombre_nc

encoding = {
    "BT_I05": {"zlib": True, "complevel": 4, "dtype": "float32"},
    "latitude": {"zlib": True, "dtype": "float32"},
    "longitude": {"zlib": True, "dtype": "float32"},
}

if ruta_nc.exists():
    existente = xr.open_dataset(ruta_nc)
    combinado = xr.concat([existente, bt_da.to_dataset()], dim="time")
    combinado = combinado.sortby("time")
    existente.close()  # << importante para evitar bloqueo del archivo
else:
    combinado = bt_da.to_dataset()

try:
    combinado.to_netcdf(ruta_nc, encoding=encoding)
    print(f"✔︎ Actualizado: {ruta_nc.name}")
except PermissionError:
    alt_path = ruta_nc.parent / f"{ruta_nc.stem}_v2.nc"
    combinado.to_netcdf(alt_path, encoding=encoding)
    print(f"✔︎ Guardado como versión alternativa: {alt_path.name}")