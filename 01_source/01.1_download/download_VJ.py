import requests
import datetime
import netCDF4
import json

# 🛠 CONFIGURACIÓN
TOKEN_EARTHDATA = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6Im1vbmljYW1hcmlucyIsImV4cCI6MTc0NzY0NTM3NCwiaWF0IjoxNzQyNDYxMzc0LCJpc3MiOiJodHRwczovL3Vycy5lYXJ0aGRhdGEubmFzYS5nb3YiLCJpZGVudGl0eV9wcm92aWRlciI6ImVkbF9vcHMiLCJhY3IiOiJlZGwiLCJhc3N1cmFuY2VfbGV2ZWwiOjN9.j63ZKbiDQ3j7C4bbRUJEQWCMnsC3SLesLvVQuJrudNHw69IoLvX-CW70BhHiQFYC8jVn0XPRKHptlgNp4yCBEwtLdXoTswsEDD9YhaCFOcZEyRA0nG-RXlYO6gcy8Gv9avn3qU6jb9-nUDN0HaWHJUW3tL0aBgTDaY0mkCbOWHxCmGl51aHR0icdAv_G4aJJ1bz5t0f4mactbJht-9t0b2HAZ0iR7T1KAY2ZaBChwwlLkWCKf5N6ffBSWBM9QB_fYQhnkXVnyTIRztx3Z2wZkDiGwQobOPTd3gryH0vx3-dxVV08tXz-PWftVmyRqfZz7smbnaznAlB1MGuo-zBH0A"  # Token de Earthdata para descargar los archivos
TOKEN_ZENODO = "tfQ7C71gC28lgZlAqRMVHkKF2svJluYA5VCq9231HLwtTRLVXcVlEPj6K9t0"  # Token de Zenodo para subir los archivos
PRODUCTS = ["VJ102IMG", "VJ103IMG"]  # Lista de productos VIIRS
COLLECTION = "5201"
LAT_LA_PALMA_MIN = 28.601109109131052  # Latitud mínima de La Palma
LAT_LA_PALMA_MAX = 28.62514776637218  # Latitud máxima de La Palma
LON_LA_PALMA_MIN = -17.929768956228138  # Longitud mínima de La Palma
LON_LA_PALMA_MAX = -17.872144640744164  # Longitud máxima de La Palma

# 📅 Obtener la fecha de ayer
ayer = datetime.datetime.now() - datetime.timedelta(1)
year = ayer.strftime("%Y")
doy = ayer.strftime("%j")  # Día juliano

# 📦 Subir archivos a Zenodo
def upload_to_zenodo(file_path, zenodo_token):
    # Primero, creamos un depósito (deposit) en Zenodo
    url = "https://zenodo.org/api/deposit/depositions"
    headers = {
        "Authorization": f"Bearer {zenodo_token}",
        "Content-Type": "application/json"
    }
    # Crea un depósito vacío
    deposit_data = {
        "metadata": {
            "title": f"Datos VIIRS {year}-{doy}",
            "upload_type": "dataset",
            "description": "Datos de imágenes VIIRS filtrados para La Palma.",
            "creators": [{"name": "Laura", "affiliation": "CSIC"}]
        }
    }
    response = requests.post(url, headers=headers, json=deposit_data)
    if response.status_code == 201:
        deposit_id = response.json()['id']
        print(f"Depósito creado con ID: {deposit_id}")
    else:
        print("Error al crear depósito en Zenodo")
        print(response.text)
        return

    # Ahora, subimos el archivo al depósito
    upload_url = f"https://zenodo.org/api/deposit/depositions/{deposit_id}/uploads"
    files = {'file': open(file_path, 'rb')}
    response = requests.post(upload_url, headers=headers, files=files)
    if response.status_code == 201:
        print(f"Archivo subido correctamente: {file_path}")
    else:
        print("Error al subir el archivo a Zenodo")
        print(response.text)

# 📅 Descargar y procesar archivos desde LAADS DAAC
for product in PRODUCTS:
    print(f"🔍 Buscando archivos de {product}...")

    API_URL = f"https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/details/allData/{COLLECTION}/{product}/{year}/{doy}"
    headers = {"Authorization": f"Bearer {TOKEN_EARTHDATA}"}
    
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
            print(f"📥 Descargando {filename}...")

            # Descargar el archivo
            download_response = requests.get(link, headers={"Authorization": f"Bearer {TOKEN_EARTHDATA}"}, stream=True)
            if download_response.status_code == 200:
                # Guardamos el archivo temporalmente
                temp_file_path = f"./{filename}"
                with open(temp_file_path, "wb") as f:
                    for chunk in download_response.iter_content(1024):
                        f.write(chunk)
                
                # Ahora procesamos el archivo con NetCDF
                try:
                    dataset = netCDF4.Dataset(temp_file_path, 'r')

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
                        # Subir a Zenodo
                        upload_to_zenodo(temp_file_path, TOKEN_ZENODO)
                        break  # Detener el bucle al encontrar un archivo que cumple las condiciones
                    else:
                        if not coordenadas_la_palma:
                            print("⚠️ Las coordenadas no están dentro de La Palma. Eliminando...")
                        if not es_noche:
                            print("⚠️ El archivo no es de noche (DayNightFlag no es 'Night'). Eliminando...")

                except Exception as e:
                    print(f"⚠️ Error al procesar el archivo {filename}: {e}")

            else:
                print(f"⚠️ Error al descargar el archivo: {filename}")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error al obtener los datos para {product} en {year}-{doy}: {e}")

print("✅ Proceso completado.")
