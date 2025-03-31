import requests
import datetime
import os
import netCDF4

# 🛠 CONFIGURACIÓN
TOKEN = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6Im1vbmljYW1hcmlucyIsImV4cCI6MTc0NzY0NTM3NCwiaWF0IjoxNzQyNDYxMzc0LCJpc3MiOiJodHRwczovL3Vycy5lYXJ0aGRhdGEubmFzYS5nb3YiLCJpZGVudGl0eV9wcm92aWRlciI6ImVkbF9vcHMiLCJhY3IiOiJlZGwiLCJhc3N1cmFuY2VfbGV2ZWwiOjN9.j63ZKbiDQ3j7C4bbRUJEQWCMnsC3SLesLvVQuJrudNHw69IoLvX-CW70BhHiQFYC8jVn0XPRKHptlgNp4yCBEwtLdXoTswsEDD9YhaCFOcZEyRA0nG-RXlYO6gcy8Gv9avn3qU6jb9-nUDN0HaWHJUW3tL0aBgTDaY0mkCbOWHxCmGl51aHR0icdAv_G4aJJ1bz5t0f4mactbJht-9t0b2HAZ0iR7T1KAY2ZaBChwwlLkWCKf5N6ffBSWBM9QB_fYQhnkXVnyTIRztx3Z2wZkDiGwQobOPTd3gryH0vx3-dxVV08tXz-PWftVmyRqfZz7smbnaznAlB1MGuo-zBH0A"  
PRODUCTS = ["VJ102IMG", "VJ103IMG"]  # Lista de productos VIIRS
COLLECTION = "5201"
LAT_LA_PALMA_MIN = 28.601109109131052  # Latitud mínima de La Palma
LAT_LA_PALMA_MAX = 28.62514776637218 # Latitud máxima de La Palma
LON_LA_PALMA_MIN = -17.929768956228138  # Longitud mínima de La Palma
LON_LA_PALMA_MAX = -17.872144640744164  # Longitud máxima de La Palma

# 📅 Obtener la fecha de ayer
ayer = datetime.datetime.now() - datetime.timedelta(1)
year = ayer.strftime("%Y")
doy = ayer.strftime("%j")  # Día juliano

OUTPUT_DIR = f"./data/raw/data_VJ/{year}_{doy}"
os.makedirs(OUTPUT_DIR, exist_ok=True)


print(f"\n📅 Descargando datos para {year}-{doy}...")

for product in PRODUCTS:
    print(f"🔍 Buscando archivos de {product}...")

    API_URL = f"https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/details/allData/{COLLECTION}/{product}/{year}/{doy}"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es 200

        file_list = response.json()
        if not file_list['content']:
            print(f"⚠️ No se encontraron archivos para {product} en {year}-{doy}")
            continue

        download_links = [file['downloadsLink'] for file in file_list['content']]

        for link in download_links:
            filename = link.split("/")[-1]
            filepath = os.path.join(OUTPUT_DIR, filename)

            print(f"📥 Descargando {filename}...")
            # Usar wget para la descarga
            os.system(f'wget --header="Authorization: Bearer {TOKEN}" -O {filepath} {link}')

            # Ahora comprobar si el archivo corresponde a La Palma y es de noche
            try:
                dataset = netCDF4.Dataset(filepath, 'r')

                # Obtener el DayNightFlag
                day_night_flag = dataset.getncattr('DayNightFlag')

                # Obtener los límites de la caja delimitadora
                south_bound = dataset.getncattr('SouthBoundingCoordinate')
                north_bound = dataset.getncattr('NorthBoundingCoordinate')
                east_bound = dataset.getncattr('EastBoundingCoordinate')
                west_bound = dataset.getncattr('WestBoundingCoordinate')

                # Verificar si las coordenadas están dentro de La Palma usando la caja delimitadora
                coordenadas_la_palma = (south_bound <= LAT_LA_PALMA_MAX and north_bound >= LAT_LA_PALMA_MIN and
                                        west_bound <= LON_LA_PALMA_MAX and east_bound >= LON_LA_PALMA_MIN)

                # Comprobar si es de noche
                es_noche = day_night_flag == 'Night'

                if coordenadas_la_palma and es_noche:
                    print("✔️ El archivo cumple con las condiciones: Es de noche y las coordenadas están dentro de La Palma.")
                    break  # Detener el bucle al encontrar un archivo que cumple las condiciones
                else:
                    if not coordenadas_la_palma:
                        print("⚠️ Las coordenadas no están dentro de La Palma. Eliminando...")
                    if not es_noche:
                        print("⚠️ El archivo no es de noche (DayNightFlag no es 'Night'). Eliminando...")
                    os.remove(filepath)  # Eliminar archivo que no cumple con los criterios

            except Exception as e:
                print(f"⚠️ Error al procesar el archivo {filename}: {e}")
                os.remove(filepath)  # Eliminar archivo en caso de error

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error al obtener los datos para {product} en {year}-{doy}: {e}")

print("✅ Descarga de datos de ayer completada.")

