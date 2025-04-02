import numpy as np
from netCDF4 import Dataset, date2num
from datetime import datetime
import os

# Rutas
input_path = '/Users/moni/Desktop/Practicas_Empresa_CSIC-2/data/raw/data_VJ/2025_088/VJ102IMG.A2025088.0300.021.2025088091601.nc'
output_nc = '/Users/moni/Desktop/Practicas_Empresa_CSIC-2/data/processed/TB_By_Year_Month_Day.nc'

# Fecha de la observación (puedes ajustarla)
fecha_obs = datetime(2025, 3, 29)

with Dataset(input_path, 'r') as nc_in:
    # --- Grupo de observaciones ---
    obs_group = nc_in.groups['observation_data']
    I05_var = obs_group.variables['I05']
    LUT_var = obs_group.variables['I05_brightness_temperature_lut']
    
    I05 = np.ma.filled(I05_var[:], np.nan)
    LUT = LUT_var[:]
    scale = I05_var.getncattr('scale_factor')
    offset = I05_var.getncattr('add_offset')

    # Aviso: Algunos valores podrían generar warning al convertirse a entero si son NaN o inválidos.
    lut_index = np.round((I05 - offset) / scale).astype(int)
    I05_bt = np.full_like(I05, np.nan)
    valid = (lut_index >= 0) & (lut_index < len(LUT))
    I05_bt[valid] = LUT[lut_index[valid]]

    # --- Reconstrucción de la grilla lat/lon a partir de los atributos del dataset ---
    south = nc_in.getncattr('SouthBoundingCoordinate')
    north = nc_in.getncattr('NorthBoundingCoordinate')
    west = nc_in.getncattr('WestBoundingCoordinate')
    east = nc_in.getncattr('EastBoundingCoordinate')
    print(f"Límites del archivo: N:{north}, S:{south}, E:{east}, O:{west}")

    n_lines, n_pixels = I05.shape
    latitudes = np.linspace(north, south, n_lines)  # desde el norte hasta el sur
    longitudes = np.linspace(west, east, n_pixels)    # desde el oeste hasta el este
    lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)

    # --- Definir la región de interés (ajusta estos límites según tu zona) ---
    lat_min, lat_max = 28.601109109131052, 28.62514776637218
    lon_min, lon_max = -17.929768956228138, -17.872144640744164

    region_mask = (lat_grid >= lat_min) & (lat_grid <= lat_max) & \
                  (lon_grid >= lon_min) & (lon_grid <= lon_max)

    # --- Calcular la mediana de TB solo en la región de interés ---
    I05_bt_region = I05_bt[region_mask]
    mediana_bt = float(np.nanmedian(I05_bt_region))
    print("Mediana de temperatura de brillo (en la región):", mediana_bt)

# === Crear o actualizar NetCDF de salida ===
if not os.path.exists(output_nc):
    with Dataset(output_nc, 'w') as nc_out:
        # Crear dimensión temporal ilimitada
        nc_out.createDimension('time', None)
        time_var = nc_out.createVariable('time', 'f8', ('time',))
        time_var.units = 'days since 2000-01-01 00:00:00'
        time_var.calendar = 'standard'

        temp_var = nc_out.createVariable('brightness_temperature_median', 'f4', ('time',))
        temp_var.units = 'K'
        temp_var.long_name = 'Daily median brightness temperature (masked region) from VIIRS I05 channel'

        time_val = date2num(fecha_obs, units=time_var.units, calendar=time_var.calendar)
        time_var[0] = time_val
        temp_var[0] = mediana_bt

        print(f"Archivo {output_nc} creado con la primera observación.")
else:
    with Dataset(output_nc, 'a') as nc_out:
        time_var = nc_out.variables['time']
        temp_var = nc_out.variables['brightness_temperature_median']
        time_val = date2num(fecha_obs, units=time_var.units, calendar=time_var.calendar)

        if time_val in time_var[:]:
            print("La fecha ya está registrada. No se añade de nuevo.")
        else:
            idx = len(time_var)
            time_var[idx] = time_val
            temp_var[idx] = mediana_bt
            print(f"Mediana añadida para el día {fecha_obs.date()}.")