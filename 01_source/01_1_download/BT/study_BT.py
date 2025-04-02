from netCDF4 import Dataset

archivo = '/Users/moni/Desktop/Practicas_Empresa_CSIC/00_data/processed/BT_daily_pixels/2025_084/diagnostico_BT_validos.nc'
with Dataset(archivo, 'r') as nc:
    print("=== Variables ===")
    print(nc.variables.keys())

    print("\n=== Dimensiones ===")
    for dim in nc.dimensions.items():
        print(dim)

    print("\n=== Atributos globales ===")
    for attr in nc.ncattrs():
        print(f"{attr}: {getattr(nc, attr)}")

    print("\n=== Forma de la variable 'brightness_temperature' ===")
    tb = nc.variables['brightness_temperature'][:]
    print(tb.shape)

    print("\n=== brightness_temperature ===")
    print(tb)