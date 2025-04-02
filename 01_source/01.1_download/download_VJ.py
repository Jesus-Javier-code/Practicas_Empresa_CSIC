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

# 🛠 CONFIGURACIÓN
TOKEN_EARTHDATA = "tu_token_earthdata"  # Reemplaza con tu token real
TOKEN_ZENODO = "tu_token_zenodo"        # Reemplaza con tu token real
PRODUCTS = ["VJ102IMG", "VJ103IMG"]     # Lista de productos VIIRS
COLLECTION = "5201"
LAT_LA_PALMA_MIN = 28.601109109131052   # Latitud mínima de La Palma
LAT_LA_PALMA_MAX = 28.62514776637218    # Latitud máxima de La Palma
LON_LA_PALMA_MIN = -17.929768956228138  # Longitud mínima de La Palma
LON_LA_PALMA_MAX = -17.872144640744164  # Longitud máxima de La Palma

# 📅 Obtener la fecha de ayer
ayer = datetime.datetime.now() - datetime.timedelta(1)
year = ayer.strftime("%Y")
doy = ayer.strftime("%j")  # Día juliano

def upload_to_zenodo(file_path, zenodo_token):
    """
    Sube un archivo a Zenodo siguiendo la API oficial
    """
    # 1. Crear un nuevo depósito
    headers = {
        "Authorization": f"Bearer {zenodo_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Crear depósito vacío
        response = requests.post(
            "https://zenodo.org/api/deposit/depositions",
            json={},  # Depósito vacío inicialmente
            headers=headers
        )
        
        if response.status_code != 201:
            print(f"❌ Error al crear depósito: {response.status_code}")
            print(f"Respuesta del servidor: {response.text}")
            return None
        
        deposit = response.json()
        deposit_id = deposit['id']
        print(f"✅ Depósito creado con ID: {deposit_id}")
        
        # 2. Subir el archivo al bucket
        bucket_url = deposit['links']['bucket']
        filename = os.path.basename(file_path)
        
        print(f"⬆️ Subiendo archivo {filename}...")
        
        # Leer y subir el archivo en chunks para manejar archivos grandes
        with open(file_path, 'rb') as file_obj:
            upload_response = requests.put(
                f"{bucket_url}/{filename}",
                data=file_obj,
                headers={"Authorization": f"Bearer {zenodo_token}"}
            )
        
        if upload_response.status_code != 200:
            print(f"❌ Error al subir archivo: {upload_response.status_code}")
            print(f"Respuesta: {upload_response.text}")
            return None
        
        print(f"✅ Archivo {filename} subido correctamente")
        
        # 3. Actualizar metadatos
        metadata = {
            "metadata": {
                "title": f"Datos VIIRS {year}-{doy}",
                "upload_type": "dataset",
                "description": f"Datos de imágenes VIIRS para La Palma ({year}-{doy}). Filtrados por coordenadas y hora nocturna.",
                "creators": [{"name": "Laura", "affiliation": "CSIC"}],
                "keywords": ["VIIRS", "La Palma", "Remote Sensing", "Night Images"]
            }
        }
        
        update_response = requests.put(
            deposit['links']['self'],
            json=metadata,
            headers=headers
        )
        
        if update_response.status_code != 200:
            print(f"⚠️ Error al actualizar metadatos: {update_response.status_code}")
            print(f"Respuesta: {update_response.text}")
        else:
            print("✅ Metadatos actualizados correctamente")
        
        # 4. Opcional: Publicar el depósito automáticamente
        # publish_response = requests.post(
        #     deposit['links']['publish'],
        #     headers=headers
        # )
        # if publish_response.status_code == 202:
        #     print("🎉 Depósito publicado correctamente")
        # else:
        #     print(f"⚠️ Error al publicar: {publish_response.text}")
        
        return deposit['links']['html']  # Devuelve el enlace al depósito
    
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return None

def download_file(url, destination):
    """Descarga un archivo con manejo de errores y reintentos"""
    max_retries = 3
    retry_delay = 5  # segundos
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {TOKEN_EARTHDATA}"},
                stream=True
            )
            response.raise_for_status()
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Intento {attempt + 1} fallido: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Esperando {retry_delay} segundos antes de reintentar...")
                time.sleep(retry_delay)
    
    return False

def process_file(file_path):
    """Procesa el archivo NetCDF y verifica las condiciones"""
    try:
        dataset = netCDF4.Dataset(file_path, 'r')
        
        # Obtener metadatos importantes
        day_night_flag = dataset.getncattr('DayNightFlag')
        south_bound = dataset.getncattr('SouthBoundingCoordinate')
        north_bound = dataset.getncattr('NorthBoundingCoordinate')
        west_bound = dataset.getncattr('WestBoundingCoordinate')
        east_bound = dataset.getncattr('EastBoundingCoordinate')
        
        # Verificar condiciones
        coordenadas_ok = (south_bound <= LAT_LA_PALMA_MAX and 
                         north_bound >= LAT_LA_PALMA_MIN and
                         west_bound <= LON_LA_PALMA_MAX and 
                         east_bound >= LON_LA_PALMA_MIN)
        
        es_noche = day_night_flag == 'Night'
        
        dataset.close()
        
        return coordenadas_ok, es_noche
    
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {str(e)}")
        return False, False

def main():
    print(f"🔍 Buscando datos VIIRS para {year}-{doy}")
    
    for product in PRODUCTS:
        print(f"\n🛰 Procesando producto: {product}")
        
        # Obtener lista de archivos disponibles
        api_url = f"https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/details/allData/{COLLECTION}/{product}/{year}/{doy}"
        
        try:
            response = requests.get(
                api_url,
                headers={"Authorization": f"Bearer {TOKEN_EARTHDATA}"}
            )
            response.raise_for_status()
            
            file_list = response.json()
            
            if not file_list.get('content'):
                print(f"⚠️ No se encontraron archivos para {product} en {year}-{doy}")
                continue
            
            # Procesar cada archivo
            for file_info in file_list['content']:
                file_url = file_info['downloadsLink']
                filename = file_url.split('/')[-1]
                temp_path = os.path.join(".", filename)
                
                print(f"\n📥 Descargando {filename}...")
                
                # Descargar el archivo
                if not download_file(file_url, temp_path):
                    print(f"❌ No se pudo descargar {filename}")
                    continue
                
                # Procesar el archivo
                print("🔍 Analizando archivo...")
                coordenadas_ok, es_noche = process_file(temp_path)
                
                if coordenadas_ok and es_noche:
                    print("✅ Cumple condiciones: Coordenadas OK y es de noche")
                    print("🚀 Subiendo a Zenodo...")
                    
                    # Subir a Zenodo
                    zenodo_link = upload_to_zenodo(temp_path, TOKEN_ZENODO)
                    if zenodo_link:
                        print(f"🌍 Enlace al depósito: {zenodo_link}")
                    
                    # Eliminar el archivo temporal después de subirlo
                    os.remove(temp_path)
                    break  # Solo subimos un archivo por producto
                
                else:
                    print("❌ No cumple condiciones:")
                    if not coordenadas_ok:
                        print("- Fuera del área de La Palma")
                    if not es_noche:
                        print("- No es imagen nocturna")
                    
                    # Eliminar el archivo que no cumple las condiciones
                    os.remove(temp_path)
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al obtener datos para {product}: {str(e)}")
        except Exception as e:
            print(f"❌ Error inesperado procesando {product}: {str(e)}")

if __name__ == "__main__":
    print("Iniciando proceso de descarga y subida a Zenodo")
    print("="*50)
    main()
    print("\n✅ Proceso completado")