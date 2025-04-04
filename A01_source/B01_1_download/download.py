
import os
import requests
import netCDF4
import time
from utils import obtener_fecha_ayer, generar_url_api, esta_en_la_palma, es_de_noche

# Configuración
TOKEN_EARTHDATA = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6Im1vbmljYW1hcmlucyIsImV4cCI6MTc0NzY0NTM3NCwiaWF0IjoxNzQyNDYxMzc0LCJpc3MiOiJodHRwczovL3Vycy5lYXJ0aGRhdGEubmFzYS5nb3YiLCJpZGVudGl0eV9wcm92aWRlciI6ImVkbF9vcHMiLCJhY3IiOiJlZGwiLCJhc3N1cmFuY2VfbGV2ZWwiOjN9.j63ZKbiDQ3j7C4bbRUJEQWCMnsC3SLesLvVQuJrudNHw69IoLvX-CW70BhHiQFYC8jVn0XPRKHptlgNp4yCBEwtLdXoTswsEDD9YhaCFOcZEyRA0nG-RXlYO6gcy8Gv9avn3qU6jb9-nUDN0HaWHJUW3tL0aBgTDaY0mkCbOWHxCmGl51aHR0icdAv_G4aJJ1bz5t0f4mactbJht-9t0b2HAZ0iR7T1KAY2ZaBChwwlLkWCKf5N6ffBSWBM9QB_fYQhnkXVnyTIRztx3Z2wZkDiGwQobOPTd3gryH0vx3-dxVV08tXz-PWftVmyRqfZz7smbnaznAlB1MGuo-zBH0A"
TOKEN_ZENODO = "tfQ7C71gC28lgZlAqRMVHkKF2svJluYA5VCq9231HLwtTRLVXcVlEPj6K9t0"  # Reemplaza con tu token real

# Productos VIIRS
PRODUCTS_VJ = ["VJ102IMG", "VJ103IMG"]
COLLECTION_VJ = "5201"

PRODUCTS_VP = ["VNP02IMG", "VNP03IMG"]
COLLECTION_VP = "5200"

def upload_to_zenodo(file_path, year, doy):
    """Sube un archivo a Zenodo"""
    headers = {
        "Authorization": f"Bearer {TOKEN_ZENODO}",
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
                headers={"Authorization": f"Bearer {TOKEN_ZENODO}"}
            )

        if upload_r.status_code in [200, 201]:  # Ambos son éxitos
            print(f"✅ Archivo subido (código {upload_r.status_code})")
            
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
            print(f"❌ Error subiendo archivo: {upload_r.status_code}\n{upload_r.text}")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
    return None

def descargar_y_procesar(productos, collection, prefijo):
    """Función unificada para descargar y procesar archivos"""
    year, doy = obtener_fecha_ayer()
    output_dir = f"./00_data/raw/data_{prefijo}/{year}_{doy}"
    os.makedirs(output_dir, exist_ok=True)
    archivo_valido = None

    print(f"\n📅 Descargando datos {prefijo} para {year}-{doy}...")

    for product in productos:
        print(f"🔍 Buscando archivos de {product}...")

        api_url = generar_url_api(product, year, doy, collection)
        headers = {"Authorization": f"Bearer {TOKEN_EARTHDATA}"}

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            file_list = response.json()

            if not file_list['content']:
                print(f"⚠️ No se encontraron archivos para {product}")
                continue

            download_links = [f['downloadsLink'] for f in file_list['content']]

            for link in download_links:
                filename = link.split("/")[-1]
                filepath = os.path.join(output_dir, filename)

                print(f"📥 Descargando {filename}...")
                
                # Descargar usando requests en lugar de wget para mejor control
                download_response = requests.get(link, headers=headers, stream=True)
                if download_response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        for chunk in download_response.iter_content(1024):
                            f.write(chunk)
                    
                    try:
                        dataset = netCDF4.Dataset(filepath, 'r')
                        flag = dataset.getncattr('DayNightFlag')
                        sur = dataset.getncattr('SouthBoundingCoordinate')
                        norte = dataset.getncattr('NorthBoundingCoordinate')
                        este = dataset.getncattr('EastBoundingCoordinate')
                        oeste = dataset.getncattr('WestBoundingCoordinate')
                        dataset.close()

                        if esta_en_la_palma(sur, norte, este, oeste) and es_de_noche(flag):
                            print("✔️ Archivo válido para La Palma de noche.")
                            archivo_valido = filepath
                            
                            # Subir a Zenodo
                            print("🚀 Subiendo a Zenodo...")
                            result = upload_to_zenodo(filepath, year, doy)
                            if result:
                                print(f"🌍 Disponible en: {result['url']}")
                            
                            break  # Solo procesamos un archivo válido por producto
                        else:
                            print("❌ No cumple condiciones. Eliminando...")
                            os.remove(filepath)
                    except Exception as e:
                        print(f"⚠️ Error procesando {filename}: {e}")
                        os.remove(filepath)
                else:
                    print(f"❌ Error descargando {filename}: {download_response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error accediendo a {product}: {e}")

    print(f"✅ Proceso {prefijo} completado.")
    return archivo_valido

if __name__ == "__main__":
    print("=== Inicio del proceso ===")
    
    # Procesar archivos VJ
    descargar_y_procesar(PRODUCTS_VJ, COLLECTION_VJ, "VJ")
    
    # Procesar archivos VP
    descargar_y_procesar(PRODUCTS_VP, COLLECTION_VP, "VN")
    
    print("✅ Proceso completo. Archivos descargados y subidos a Zenodo.")