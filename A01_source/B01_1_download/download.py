import os
import requests
import netCDF4
from datetime import datetime, timedelta
import time
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='zenodo_upload.log'
)
logger = logging.getLogger()

# Configuración
TOKEN_EARTHDATA = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6Im1vbmljYW1hcmlucyIsImV4cCI6MTc0NzY0NTM3NCwiaWF0IjoxNzQyNDYxMzc0LCJpc3MiOiJodHRwczovL3Vycy5lYXJ0aGRhdGEubmFzYS5nb3YiLCJpZGVudGl0eV9wcm92aWRlciI6ImVkbF9vcHMiLCJhY3IiOiJlZGwiLCJhc3N1cmFuY2VfbGV2ZWwiOjN9.j63ZKbiDQ3j7C4bbRUJEQWCMnsC3SLesLvVQuJrudNHw69IoLvX-CW70BhHiQFYC8jVn0XPRKHptlgNp4yCBEwtLdXoTswsEDD9YhaCFOcZEyRA0nG-RXlYO6gcy8Gv9avn3qU6jb9-nUDN0HaWHJUW3tL0aBgTDaY0mkCbOWHxCmGl51aHR0icdAv_G4aJJ1bz5t0f4mactbJht-9t0b2HAZ0iR7T1KAY2ZaBChwwlLkWCKf5N6ffBSWBM9QB_fYQhnkXVnyTIRztx3Z2wZkDiGwQobOPTd3gryH0vx3-dxVV08tXz-PWftVmyRqfZz7smbnaznAlB1MGuo-zBH0A"  # Reemplaza con tu token real
TOKEN_ZENODO = "tfQ7C71gC28lgZlAqRMVHkKF2svJluYA5VCq9231HLwtTRLVXcVlEPj6K9t0"        # Reemplaza con tu token real

# Productos VIIRS
PRODUCTS_VJ = ["VJ102IMG", "VJ103IMG"]
COLLECTION_VJ = "5201"

PRODUCTS_VP = ["VNP02IMG", "VNP03IMG"]
COLLECTION_VP = "5200"

# Coordenadas La Palma
LAT_LA_PALMA_MIN = 28.601109109131052
LAT_LA_PALMA_MAX = 28.62514776637218
LON_LA_PALMA_MIN = -17.929768956228138
LON_LA_PALMA_MAX = -17.872144640744164

def obtener_fecha_ayer():
    """Obtiene la fecha de ayer en formato año y día juliano"""
    ayer = datetime.now() - timedelta(days=1)
    return ayer.strftime("%Y"), ayer.strftime("%j")

def generar_url_api(product, year, doy, collection):
    """Genera la URL de la API LAADS DAAC para un producto y fecha"""
    return f"https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/details/allData/{collection}/{product}/{year}/{doy}"

def esta_en_la_palma(sur, norte, este, oeste):
    """Verifica si las coordenadas están dentro del área de La Palma"""
    return (sur <= LAT_LA_PALMA_MAX and norte >= LAT_LA_PALMA_MIN and
            oeste <= LON_LA_PALMA_MAX and este >= LON_LA_PALMA_MIN)

def es_de_noche(day_night_flag):
    """Verifica si la imagen es nocturna"""
    return day_night_flag == 'Night'

def crear_deposito_zenodo(year, doy):
    """Crea un nuevo depósito en Zenodo y devuelve los datos del depósito"""
    headers = {
        "Authorization": f"Bearer {TOKEN_ZENODO}",
        "Content-Type": "application/json"
    }
    
    # Fecha formateada para metadatos
    fecha_formateada = datetime.strptime(f"{year}-{doy}", "%Y-%j").strftime("%Y-%m-%d")
    
    metadata = {
        "metadata": {
            "title": f"Datos VIIRS La Palma - {fecha_formateada}",
            "upload_type": "dataset",
            "description": f"Datos VIIRS procesados automáticamente para La Palma ({fecha_formateada}). Incluye productos VJ y VP validados (nocturnos y dentro de coordenadas).",
            "creators": [{"name": "Laura", "affiliation": "CSIC"}],
            "keywords": ["VIIRS", "La Palma", "Remote Sensing", "Night Images", "NASA"],
            "license": "cc-by"
        }
    }
    
    try:
        response = requests.post(
            "https://zenodo.org/api/deposit/depositions",
            json=metadata,
            headers=headers
        )
        
        if response.status_code == 201:
            deposit = response.json()
            logger.info(f"Depósito creado exitosamente. ID: {deposit['id']}")
            return deposit
        else:
            logger.error(f"Error al crear depósito: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error inesperado al crear depósito: {str(e)}")
        return None

def subir_archivo_a_zenodo(deposit, file_path):
    """Sube un archivo al depósito especificado en Zenodo"""
    if not deposit or not os.path.exists(file_path):
        return None
    
    headers = {"Authorization": f"Bearer {TOKEN_ZENODO}"}
    bucket_url = deposit['links']['bucket']
    filename = os.path.basename(file_path)
    
    try:
        with open(file_path, 'rb') as file_obj:
            response = requests.put(
                f"{bucket_url}/{filename}",
                data=file_obj,
                headers=headers
            )
        
        if response.status_code in [200, 201]:
            logger.info(f"Archivo {filename} subido correctamente")
            return response.json()
        else:
            logger.error(f"Error al subir {filename}: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error al subir {filename}: {str(e)}")
        return None

def descargar_y_validar_archivos(productos, collection, prefijo, year, doy):
    """Descarga archivos y devuelve los que cumplen las condiciones"""
    output_dir = f"./00_data/raw/data_{prefijo}/{year}_{doy}"
    os.makedirs(output_dir, exist_ok=True)
    archivos_validos = []
    
    for product in productos:
        logger.info(f"Procesando producto: {product}")
        
        try:
            # Obtener lista de archivos disponibles
            api_url = generar_url_api(product, year, doy, collection)
            response = requests.get(
                api_url,
                headers={"Authorization": f"Bearer {TOKEN_EARTHDATA}"}
            )
            response.raise_for_status()
            
            file_list = response.json().get('content', [])
            if not file_list:
                logger.info(f"No hay archivos disponibles para {product}")
                continue
            
            # Procesar cada archivo
            for file_info in file_list:
                file_url = file_info['downloadsLink']
                filename = file_url.split('/')[-1]
                filepath = os.path.join(output_dir, filename)
                
                logger.info(f"Descargando {filename}...")
                
                # Descargar archivo
                download_response = requests.get(
                    file_url,
                    headers={"Authorization": f"Bearer {TOKEN_EARTHDATA}"},
                    stream=True
                )
                
                if download_response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        for chunk in download_response.iter_content(1024):
                            f.write(chunk)
                    
                    # Validar archivo
                    try:
                        with netCDF4.Dataset(filepath, 'r') as dataset:
                            day_night_flag = dataset.getncattr('DayNightFlag')
                            south = dataset.getncattr('SouthBoundingCoordinate')
                            north = dataset.getncattr('NorthBoundingCoordinate')
                            east = dataset.getncattr('EastBoundingCoordinate')
                            west = dataset.getncattr('WestBoundingCoordinate')
                            
                            if esta_en_la_palma(south, north, east, west) and es_de_noche(day_night_flag):
                                logger.info(f"Archivo válido: {filename}")
                                archivos_validos.append(filepath)
                            else:
                                logger.info(f"Archivo no válido: {filename}")
                                os.remove(filepath)
                    except Exception as e:
                        logger.error(f"Error al validar {filename}: {str(e)}")
                        os.remove(filepath)
                else:
                    logger.error(f"Error al descargar {filename}: {download_response.status_code}")
        
        except Exception as e:
            logger.error(f"Error procesando {product}: {str(e)}")
    
    return archivos_validos

def main():
    logger.info("=== Inicio del proceso ===")
    
    # Obtener fecha de ayer
    year, doy = obtener_fecha_ayer()
    fecha_formateada = datetime.strptime(f"{year}-{doy}", "%Y-%j").strftime("%Y-%m-%d")
    logger.info(f"Procesando datos para {fecha_formateada}")
    
    # Crear un único depósito en Zenodo
    deposit = crear_deposito_zenodo(year, doy)
    
    if not deposit:
        logger.error("No se pudo crear el depósito en Zenodo. Abortando...")
        return
    
    # Descargar y validar archivos VJ
    logger.info("Procesando productos VJ...")
    archivos_vj = descargar_y_validar_archivos(PRODUCTS_VJ, COLLECTION_VJ, "VJ", year, doy)
    
    # Descargar y validar archivos VP
    logger.info("Procesando productos VP...")
    archivos_vp = descargar_y_validar_archivos(PRODUCTS_VP, COLLECTION_VP, "VN", year, doy)
    
    # Combinar todos los archivos válidos
    todos_archivos = archivos_vj + archivos_vp
    
    if not todos_archivos:
        logger.info("No se encontraron archivos válidos para subir")
        return
    
    # Subir todos los archivos al mismo depósito
    logger.info(f"Subiendo {len(todos_archivos)} archivos a Zenodo...")
    for archivo in todos_archivos:
        subir_archivo_a_zenodo(deposit, archivo)
        
        # Eliminar archivo local después de subirlo
        try:
            os.remove(archivo)
            logger.info(f"Archivo {archivo} eliminado de la máquina local.")
        except Exception as e:
            logger.error(f"Error al eliminar {archivo}: {str(e)}")
    
    logger.info(f"Proceso completado. Depósito disponible en: {deposit['links']['html']}")

if __name__ == "__main__":
    main()
