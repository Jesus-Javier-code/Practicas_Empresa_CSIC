#La Reference Scene (REF) es una temperatura de brillo mensual por píxel, 
#que representa el estado “normal” o “de fondo” del volcán cuando no hay actividad térmica.

#Se usará como base de comparación para detectar anomalías y calcular la potencia radiactiva diaria (ΦRad).

import os
import numpy as np
from netCDF4 import Dataset
from datetime import datetime
from glob import glob
from skimage.transform import resize
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt

# === CONFIGURACIÓN ===
base_dir = "/Users/moni/Desktop/Practicas_Empresa_CSIC"
bt_dir = os.path.join(base_dir, "00_data/processed/BT_daily_pixels")
ref_base_dir = os.path.join(base_dir, "00_data/processed/REF")
year = 2025
month = 3
min_valid_pixels = 50

# === FUNCIONES ===
def extract_tb_matrix(nc_path):
    with Dataset(nc_path, 'r') as ds:
        return ds.variables['brightness_temperature'][:].astype('float32')

def calculate_r2(reference, candidate):
    mask = ~np.isnan(reference) & ~np.isnan(candidate)
    if np.sum(mask) < min_valid_pixels:
        return np.nan
    ref_vals = reference[mask].flatten()
    cand_vals = candidate[mask].flatten()
    if np.all(ref_vals == ref_vals[0]):
        return np.nan
    return r2_score(ref_vals, cand_vals)

def save_ref_nc(path, ref_array, metadata):
    ny, nx = ref_array.shape
    with Dataset(path, 'w') as ds:
        ds.createDimension('lat', ny)
        ds.createDimension('lon', nx)
        var = ds.createVariable('brightness_temperature_REF', 'f4', ('lat', 'lon'), fill_value=np.nan)
        var.units = 'K'
        var.long_name = 'Monthly reference brightness temperature (median of scenes)'
        var[:, :] = ref_array
        for key, value in metadata.items():
            setattr(ds, key, value)

# === CARGAR ESCENAS DEL MES ===
doy_start = datetime(year, month, 1).timetuple().tm_yday
doy_end = datetime(year, month + 1, 1).timetuple().tm_yday if month < 12 else 366

candidatos = []
for doy in range(doy_start, doy_end):
    folder = os.path.join(bt_dir, f"{year}_{doy:03d}")
    archivos = sorted(glob(os.path.join(folder, "*.nc")))
    if archivos:
        candidatos.append(archivos[0])

if not candidatos:
    raise ValueError("No se encontraron archivos para este mes.")

# === CARGAR ESCENAS CON INTERPOLACIÓN SI NECESARIO ===
matrices, nombres = [], []
for path in candidatos:
    tb = extract_tb_matrix(path)
    if np.all(np.isnan(tb)):
        print(f"{os.path.basename(path)} descartada (vacía)")
        continue
    if not matrices:
        ref_shape = tb.shape
    if tb.shape != ref_shape:
        print(f"{os.path.basename(path)} interpolada de {tb.shape} a {ref_shape}")
        tb = resize(tb, ref_shape, order=3, preserve_range=True, anti_aliasing=True)
    matrices.append(tb)
    nombres.append(os.path.basename(path))

if len(matrices) < 2:
    raise ValueError("No hay suficientes escenas válidas para construir una REF.")

# === CALCULAR REF PROVISIONAL ===
base_ref = np.nanmedian(np.stack(matrices), axis=0)

# === MOSTRAR R² PARA CADA ESCENA ===
print("\n=== R² de cada escena con la REF provisional ===")
r2_list = []
for i, tb in enumerate(matrices):
    r2 = calculate_r2(base_ref, tb)
    r2_list.append(r2)
    print(f"{nombres[i]} -> R² = {r2:.3f}" if not np.isnan(r2) else f"{nombres[i]} -> R² = NaN")

# === FILTRAR ESCENAS QUE NO PUEDEN COMPARARSE NI APORTAN INFORMACIÓN NUEVA ===
validas = []
valid_names = []

for i, r2 in enumerate(r2_list):
    if np.isnan(r2):
        continue
    is_duplicate = any(np.allclose(matrices[i], v, equal_nan=True) for v in validas)
    if not is_duplicate:
        validas.append(matrices[i])
        valid_names.append(nombres[i])
    else:
        print(f"{nombres[i]} descartada (duplicada de otra escena)")

if len(validas) < 2:
    raise ValueError("Demasiadas escenas descartadas: REF no fiable con menos de 2 únicas.")

print(f"\nEscenas válidas utilizadas en la REF:")
for name in valid_names:
    print(f" - {name}")

# === CALCULAR REF FINAL ===
ref_array = np.nanmedian(np.stack(validas), axis=0)

# === GUARDAR REF ===
output_folder = os.path.join(ref_base_dir, f"{year}", f"{month:02d}")
os.makedirs(output_folder, exist_ok=True)
ref_path = os.path.join(output_folder, f"REF_LaPalma_{year}_{month:02d}.nc")

save_ref_nc(ref_path, ref_array, {
    "region": "La Palma Volcano",
    "year": year,
    "month": month,
    "source": f"Monthly brightness temperature scenes (n={len(validas)})",
    "history": f"Created on {datetime.utcnow().isoformat()}"
})

print(f"\nREF guardada correctamente en: {ref_path}")