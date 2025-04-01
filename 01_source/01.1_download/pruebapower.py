from pathlib import Path
import netCDF4 as nc
from netCDF4 import num2date
import numpy as np

# Ruta al archivo
file = Path("../../00_data/processed/BT_by_Year_Month_Day/TB_By_Year_Month_Day.nc")

if file.exists():
    with nc.Dataset(file, 'r') as dataset:
        print("Variables en el archivo:", dataset.variables.keys())

        if 'time' in dataset.variables and 'brightness_temperature_median' in dataset.variables:
            time_var = dataset.variables['time'][:]
            temp_var = dataset.variables['brightness_temperature_median'][:]

            # Convertir tiempo a fechas legibles
            units = dataset.variables['time'].units
            calendar = dataset.variables['time'].calendar
            fechas = num2date(time_var, units=units, calendar=calendar)
            fechas_str = [f.strftime("%Y-%m-%d") for f in fechas]

            # --- Cálculo de la radiancia con Ley de Planck ---
            h = 6.62607015e-34  # Constante de Planck (J·s)
            c = 2.998e8         # Velocidad de la luz (m/s)
            kB = 1.380649e-23    # Constante de Boltzmann (J/K)
            lambda_m = 11.45e-6  # Longitud de onda en metros (11.45 µm)

            radiancias = []
            for tb in temp_var:
                exponente = (h * c) / (lambda_m * kB * tb)
                B_lambda = (2 * h * c**2 / (lambda_m**5)) * (1 / (np.exp(exponente) - 1))
                radiancias.append(B_lambda)

            # Mostrar resultados
            print("\nFecha, TB (K), Radiancia (W·m⁻²·sr⁻¹·m⁻¹):")
            for fecha, tb, rad in zip(fechas_str, temp_var, radiancias):
                print(f"{fecha}: {tb:.2f} K → {rad:.2e} W·m⁻²·sr⁻¹·m⁻¹")

        else:
            print("No se encontraron las variables esperadas en el archivo.")
else:
    print(f"El archivo {file} no existe. Verifica la ruta desde {Path.cwd()}")