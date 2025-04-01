from pathlib import Path
import netCDF4 as nc
from netCDF4 import num2date

# Ruta relativa al archivo NetCDF
file = Path("Practicas_Empresa_CSIC/00_data/processed/BT_by_Year_Month_Day/TB_By_Year_Month_Day.nc")

if file.exists():
    with nc.Dataset(file, 'r') as dataset:
        print("Variables en el archivo:", dataset.variables.keys())

        # Verifica si las variables 'time' y 'brightness_temperature_median' existen
        if 'time' in dataset.variables and 'brightness_temperature_median' in dataset.variables:
            time_var = dataset.variables['time'][:]
            temp_var = dataset.variables['brightness_temperature_median'][:]

            # Convertir el tiempo a fechas legibles
            units = dataset.variables['time'].units
            calendar = dataset.variables['time'].calendar
            fechas = num2date(time_var, units=units, calendar=calendar)
            fechas_str = [f.strftime("%Y-%m-%d") for f in fechas]

            # Mostrar los datos
            print("\nFechas y medianas de temperatura de brillo:")
            for fecha, temp in zip(fechas_str, temp_var):
                print(f"{fecha}: {temp:.2f} K")
        else:
            print("No se encontraron las variables esperadas en el archivo.")
else:
    print(f"El archivo {file} no existe. Verifica la ruta desde {Path.cwd()}")
