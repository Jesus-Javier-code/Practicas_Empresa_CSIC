import numpy as np
import pandas as pd
from netCDF4 import Dataset

# Ruta del archivo
file_path = '/Users/moni/Desktop/Practicas_Empresa_CSIC-2/data/raw/data_VJ/2025_089/VJ102IMG.A2025089.0242.021.2025089092121.nc'
output_csv = '/Users/moni/Desktop/Practicas_Empresa_CSIC-2/data/processed/output.csv'

with Dataset(file_path, 'r') as nc_file:
    if 'observation_data' in nc_file.groups:
        obs_group = nc_file.groups['observation_data']
        
        if 'I05' in obs_group.variables and 'I05_brightness_temperature_lut' in obs_group.variables:
            I05_var = obs_group.variables['I05']
            LUT_var = obs_group.variables['I05_brightness_temperature_lut']
            
            I05 = np.ma.filled(I05_var[:], np.nan)
            LUT = LUT_var[:]
            
            scale = I05_var.getncattr('scale_factor')
            offset = I05_var.getncattr('add_offset')

            print("Radiancia min/max:", np.nanmin(I05), np.nanmax(I05))
            print("Aplicando escala inversa: (I05 -", offset, ")/", scale)

            # Convertir radiancia a índice LUT
            lut_index = np.round((I05 - offset) / scale).astype(int)

            # Aplicar LUT
            I05_bt = np.full_like(I05, np.nan)
            valid = (lut_index >= 0) & (lut_index < len(LUT))
            I05_bt[valid] = LUT[lut_index[valid]]

            print("Temperatura de brillo min/max:", np.nanmin(I05_bt), np.nanmax(I05_bt))

            # Guardar como CSV
            df = pd.DataFrame(I05_bt)
            df.to_csv(output_csv, index=False, header=False)
            print(f"Archivo CSV guardado en {output_csv}")
        else:
            print("Faltan variables I05 o LUT.")
    else:
        print("Grupo 'observation_data' no encontrado.")