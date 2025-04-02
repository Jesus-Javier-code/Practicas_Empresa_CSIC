'''
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
    upload_url = f"https://zenodo.org/uploads/{deposit_id}"
    #upload_url = f"https://zenodo.org/api/deposit/depositions/{deposit_id}/files"
    with open(file_path, 'rb') as f:
    files = {'file': f}
    ##files = {'file': (file_path, open(file_path, 'rb'))}
    #files = {'file': open(file_path, 'rb')}
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
'''

'''
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
        deposit = response.json()
        deposit_id = deposit['id']
        print(f"Depósito creado con ID: {deposit_id}")
        
        # Obtener el URL del bucket para subir archivos
        bucket_url = deposit['links']['bucket']
        filename = file_path.split('/')[-1]
        
        # Subir el archivo al bucket
        with open(file_path, 'rb') as f:
            upload_response = requests.put(
                f"{bucket_url}/{filename}",
                data=f,
                headers={"Authorization": f"Bearer {zenodo_token}"}
            )
            
        if upload_response.status_code == 200:
            print(f"Archivo {filename} subido correctamente a Zenodo")
            
            # Publicar el depósito (opcional, si quieres que se publique inmediatamente)
            # publish_url = f"https://zenodo.org/api/deposit/depositions/{deposit_id}/actions/publish"
            # publish_response = requests.post(publish_url, headers=headers)
            # if publish_response.status_code == 202:
            #     print("Depósito publicado correctamente")
        else:
            print(f"Error al subir el archivo: {upload_response.status_code}")
            print(upload_response.text)
    else:
        print("Error al crear depósito en Zenodo")
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
'''
import requests
import datetime
import netCDF4
import os
import time

# Configuración
TOKEN_EARTHDATA = "tu_token_earthdata"
TOKEN_ZENODO = "tu_token_zenodo"
PRODUCTS = ["VJ102IMG", "VJ103IMG"]
COLLECTION = "5201"
LAT_LA_PALMA_MIN = 28.601109109131052
LAT_LA_PALMA_MAX = 28.62514776637218
LON_LA_PALMA_MIN = -17.929768956228138
LON_LA_PALMA_MAX = -17.872144640744164

# Obtener fecha de ayer
ayer = datetime.datetime.now() - datetime.timedelta(1)
year = ayer.strftime("%Y")
doy = ayer.strftime("%j")

def upload_to_zenodo(file_path, zenodo_token):
    """Función corregida para manejar respuesta 201"""
    headers = {
        "Authorization": f"Bearer {zenodo_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # 1. Crear depósito
        r = requests.post(
            "https://zenodo.org/api/deposit/depositions",
            json={},
            headers=headers
        )
        if r.status_code != 201:
            print(f"❌ Error creando depósito: {r.status_code}\n{r.text}")
            return None
        
        deposit = r.json()
        print(f"✅ Depósito {deposit['id']} creado")

        # 2. Subir archivo
        filename = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            upload_r = requests.put(
                f"{deposit['links']['bucket']}/{filename}",
                data=f,
                headers={"Authorization": f"Bearer {zenodo_token}"}
            )

        # Manejo CORRECTO de respuesta 201
        if upload_r.status_code in [200, 201]:  # Ambos son éxitos
            print(f"✅ Archivo subido (código {upload_r.status_code})")
            print(f"📄 Datos: {upload_r.json()}")
            
            # 3. Actualizar metadatos
            metadata = {
                "metadata": {
                    "title": f"Datos VIIRS {year}-{doy}",
                    "upload_type": "dataset",
                    "description": f"Datos VIIRS para La Palma ({year}-{doy})",
                    "creators": [{"name": "Laura", "affiliation": "CSIC"}],
                    "license": "cc-by"
                }
            }
            update_r = requests.put(
                deposit['links']['self'],
                json=metadata,
                headers=headers
            )
            
            if update_r.status_code == 200:
                print("✅ Metadatos actualizados")
                return {
                    "id": deposit['id'],
                    "url": deposit['links']['html'],
                    "file_url": upload_r.json()['links']['self']
                }
            else:
                print(f"⚠️ Error actualizando metadatos: {update_r.status_code}")
                return None
        else:
            print(f"❌ Error subiendo archivo: {upload_r.status_code}\n{upload_r.text}")
            return None

    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return None

def download_file(url, destination):
    """Descarga archivos con reintentos"""
    for attempt in range(3):
        try:
            with requests.get(url, headers={"Authorization": f"Bearer {TOKEN_EARTHDATA}"}, stream=True) as r:
                r.raise_for_status()
                with open(destination, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return True
        except Exception as e:
            print(f"⚠️ Intento {attempt+1} fallido: {str(e)}")
            time.sleep(5)
    return False

def process_file(file_path):
    """Procesa archivo NetCDF"""
    try:
        with netCDF4.Dataset(file_path, 'r') as ds:
            coords_ok = (ds.SouthBoundingCoordinate <= LAT_LA_PALMA_MAX and 
                        ds.NorthBoundingCoordinate >= LAT_LA_PALMA_MIN and
                        ds.WestBoundingCoordinate <= LON_LA_PALMA_MAX and 
                        ds.EastBoundingCoordinate >= LON_LA_PALMA_MIN)
            is_night = ds.DayNightFlag == 'Night'
        return coords_ok, is_night
    except Exception as e:
        print(f"❌ Error procesando archivo: {str(e)}")
        return False, False

def main():
    print(f"🔍 Buscando datos VIIRS para {year}-{doy}")
    
    for product in PRODUCTS:
        print(f"\n🛰 Procesando {product}...")
        try:
            r = requests.get(
                f"https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/details/allData/{COLLECTION}/{product}/{year}/{doy}",
                headers={"Authorization": f"Bearer {TOKEN_EARTHDATA}"}
            )
            r.raise_for_status()
            
            files = r.json().get('content', [])
            if not files:
                print("⚠️ No hay archivos disponibles")
                continue

            for file_info in files:
                filename = file_info['downloadsLink'].split('/')[-1]
                temp_path = f"./{filename}"
                
                if download_file(file_info['downloadsLink'], temp_path):
                    print(f"📥 Descargado: {filename}")
                    coords_ok, is_night = process_file(temp_path)
                    
                    if coords_ok and is_night:
                        print("✅ Cumple condiciones - Subiendo a Zenodo...")
                        result = upload_to_zenodo(temp_path, TOKEN_ZENODO)
                        if result:
                            print(f"🌍 Disponible en: {result['url']}")
                        os.remove(temp_path)
                        break  # Solo subir un archivo por producto
                    else:
                        print("❌ No cumple condiciones")
                        os.remove(temp_path)
                else:
                    print(f"❌ Falló descarga de {filename}")
        except Exception as e:
            print(f"❌ Error procesando {product}: {str(e)}")

if __name__ == "__main__":
    print("=== Inicio del proceso ===")
    main()
    print("✅ Proceso completadoo")