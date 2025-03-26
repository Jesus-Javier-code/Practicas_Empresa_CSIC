import xarray as xr

def check_day_night(file_path):
    try:
        # Abrir el archivo NetCDF
        ds = xr.open_dataset(file_path, decode_times=False)
        
        # Acceder al atributo DayNightFlag
        day_night_flag = ds.attrs.get('DayNightFlag', None)
        
        if day_night_flag is not None:
            print(f"El archivo tiene el atributo DayNightFlag: {day_night_flag}")
            # Comprobamos si el valor de DayNightFlag es 'Night' o 'Day' como texto
            if day_night_flag == 'Night':
                print("Es de noche.")
            elif day_night_flag == 'Day':
                print("Es de día.")
            else:
                print(f"Valor desconocido para DayNightFlag: {day_night_flag}")
        else:
            print("El archivo no contiene el atributo DayNightFlag.")
    
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

