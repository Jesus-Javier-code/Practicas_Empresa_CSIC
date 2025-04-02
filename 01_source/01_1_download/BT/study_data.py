import netCDF4 as nc
from netCDF4 import num2date
import os

file = '00_data/processed/BT_By_Year_Month_Day/TB_By_Year_Month_Day.nc'

if os.path.exists(file):
    with nc.Dataset(file, 'r') as dataset:
        print("Variables in the file:")
        print(dataset.variables.keys())

        if 'time' in dataset.variables and 'brightness_temperature_median' in dataset.variables:
            time_var = dataset.variables['time'][:]
            temp_var = dataset.variables['brightness_temperature_median'][:]

            units = dataset.variables['time'].units
            calendar = dataset.variables['time'].calendar

            fechas = num2date(time_var, units=units, calendar=calendar)
            fechas_str = [f.strftime("%Y-%m-%d") for f in fechas]

            print("\nFechas y medianas de temperatura de brillo:")
            for fecha, temp in zip(fechas_str, temp_var):
                print(f"{fecha}: {temp:.2f} K")
        else:
            print("No se encontraron las variables esperadas en el archivo.")
else:
    print(f"El archivo {file} no existe.")

