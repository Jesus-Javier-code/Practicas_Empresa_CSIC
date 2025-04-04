import os
import numpy as np
from netCDF4 import Dataset
from datetime import datetime, timedelta

# === CONFIGURACIÓN ===
base_dir = '/Users/moni/Desktop/Practicas_Empresa_CSIC'
bt_dir = os.path.join(base_dir, '00_data/processed/BT_daily_pixels')
year = 2025
month = 3

# === FECHAS ===
start_date = datetime(year, month, 1)
end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
num_days = (end_date - start_date).days

print(f"\n>>> Guardando diagnóstico diario de TB en archivos .nc para {year}-{month:02d}\n")

for i in range(num_days):
    date = start_date + timedelta(days=i)
    doy = date.timetuple().tm_yday
    folder = os.path.join(bt_dir, f"{year}_{doy:03d}")
    file_in = os.path.join(folder, f"brightness_temperature_{date.strftime('%Y%m%d')}.nc")

    if not os.path.exists(file_in):
        print(f"{date.date()} → archivo no encontrado.")
        continue

    with Dataset(file_in, 'r') as ds:
        tb = ds.variables['brightness_temperature'][:]
        total = tb.size
        valid = np.sum(~np.isnan(tb))
        ratio = valid / total if total > 0 else np.nan
        tmin = np.nanmin(tb) if valid > 0 else np.nan
        tmax = np.nanmax(tb) if valid > 0 else np.nan

    # === GUARDAR ARCHIVO DE DIAGNÓSTICO ===
    diag_path = os.path.join(folder, 'diagnostico_BT_validos.nc')
    with Dataset(diag_path, 'w') as ds_out:
        ds_out.createDimension('scalar', 1)

        def create_scalar_var(name, value, unit, desc):
            var = ds_out.createVariable(name, 'f4', ('scalar',))
            var.units = unit
            var.long_name = desc
            var[:] = value if not np.isnan(value) else np.nan

        create_scalar_var('pixeles_validos', valid, 'count', 'Número de píxeles válidos')
        create_scalar_var('pixeles_totales', total, 'count', 'Total de píxeles')
        create_scalar_var('proporcion_validos', ratio, '1', 'Proporción de píxeles válidos')
        create_scalar_var('temperatura_minima', tmin, 'K', 'Temperatura mínima en la región')
        create_scalar_var('temperatura_maxima', tmax, 'K', 'Temperatura máxima en la región')

        ds_out.date = date.strftime('%Y-%m-%d')
        ds_out.doy = doy
        ds_out.description = 'Diagnóstico diario de calidad de la temperatura de brillo'
        ds_out.history = f'Creado el {datetime.utcnow().isoformat()}'

    print(f"{date.date()} → diagnóstico guardado en: {diag_path}")