import os
import requests
import netCDF4
import datetime
from pathlib import Path


# === CONSTANTS ===

# Geographic bounding box for La Palma (Canary Islands)
LAT_LA_PALMA_MIN = 28.601109109131052
"""
float: Southern latitude boundary of La Palma.
"""

LAT_LA_PALMA_MAX = 28.62514776637218
"""
float: Northern latitude boundary of La Palma.
"""

LON_LA_PALMA_MIN = -17.929768956228138
"""
float: Western longitude boundary of La Palma.
"""

LON_LA_PALMA_MAX = -17.872144640744164
"""
float: Eastern longitude boundary of La Palma.
"""

# Satellite product codes used for data download
PRODUCTS1 = ["VJ102IMG"]
"""
List[str]: List of satellite product identifiers used to query and download data.
"""

# MODIS collection identifier used in the API request
COLLECTION1 = "5201"
"""
str: Collection number used when querying the satellite data API.
"""

# NASA Earthdata bearer token for authenticated access to the API
TOKEN = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6Im1vbmljYW1hcmlucyIsImV4cCI6MTc0NzY0NTM3NCwiaWF0IjoxNzQyNDYxMzc0LCJpc3MiOiJodHRwczovL3Vycy5lYXJ0aGRhdGEubmFzYS5nb3YiLCJpZGVudGl0eV9wcm92aWRlciI6ImVkbF9vcHMiLCJhY3IiOiJlZGwiLCJhc3N1cmFuY2VfbGV2ZWwiOjN9.j63ZKbiDQ3j7C4bbRUJEQWCMnsC3SLesLvVQuJrudNHw69IoLvX-CW70BhHiQFYC8jVn0XPRKHptlgNp4yCBEwtLdXoTswsEDD9YhaCFOcZEyRA0nG-RXlYO6gcy8Gv9avn3qU6jb9-nUDN0HaWHJUW3tL0aBgTDaY0mkCbOWHxCmGl51aHR0icdAv_G4aJJ1bz5t0f4mactbJht-9t0b2HAZ0iR7T1KAY2ZaBChwwlLkWCKf5N6ffBSWBM9QB_fYQhnkXVnyTIRztx3Z2wZkDiGwQobOPTd3gryH0vx3-dxVV08tXz-PWftVmyRqfZz7smbnaznAlB1MGuo-zBH0A"
"""
str: Bearer token used to authenticate requests to the NASA Earthdata API.
"""


# === FUNCTIONS ===
def obtener_fecha_ayer():
    """
    Returns yesterday's date as a tuple of year and day-of-year (DOY).

    Returns:
        tuple:
            - year (str): The 4-digit year (e.g., '2025').
            - doy (str): The day of the year, zero-padded to 3 digits (e.g., '099').
    """
    ayer = datetime.datetime.now() - datetime.timedelta(1)
    return ayer.strftime("%Y"), ayer.strftime("%j")


def generar_url_api(product, year, doy, collection):
    """
    Constructs the API URL to query metadata for a specific satellite product on a given date.

    Args:
        product (str): The product name or ID (e.g., 'VJ102IMG').
        year (str): The year in YYYY format.
        doy (str): The day of the year (DOY), zero-padded (e.g., '099').
        collection (str): The collection number to query (e.g., '5201').

    Returns:
        str: A formatted URL string to query the product metadata via the LAADS DAAC API.
    """
    return f"https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/details/allData/{collection}/{product}/{year}/{doy}"


def esta_en_la_palma(sur, norte, este, oeste):
    """
    Checks whether a satellite image covers the geographic area of La Palma island.

    Args:
        sur (float): Southern boundary latitude of the image.
        norte (float): Northern boundary latitude of the image.
        este (float): Eastern boundary longitude of the image.
        oeste (float): Western boundary longitude of the image.

    Returns:
        bool: True if the image intersects with the defined bounding box of La Palma, False otherwise.
    """
    return (sur <= LAT_LA_PALMA_MAX and norte >= LAT_LA_PALMA_MIN and
            oeste <= LON_LA_PALMA_MAX and este >= LON_LA_PALMA_MIN)



def es_de_noche(day_night_flag):
    """
    Determines whether a satellite image was taken during the night.

    Args:
        day_night_flag (str): The 'DayNightFlag' attribute from the NetCDF metadata.

    Returns:
        bool: True if the value indicates 'night', False otherwise.
    """
    return day_night_flag.lower() == 'night'



# === MAIN FUNCTION ===

def descargar_datos1():
    """
    Downloads satellite data for the previous day, filters it for nighttime images 
    over La Palma island, and saves the valid files locally.

    Steps:
        1. Get yesterday's date as year and day-of-year (DOY).
        2. Create a directory to store downloaded files based on the date.
        3. Loop through each product defined in PRODUCTS1:
            - Request the list of available files from the API.
            - If files are found, download them using wget and a Bearer token.
            - Open each file using netCDF4 and check:
                a. If the image was taken at night ('DayNightFlag').
                b. If the image geographically covers La Palma.
            - Keep the file only if both conditions are met.
            - Delete the file otherwise.

    Requirements:
        - Environment variables or global definitions:
            - PRODUCTS1: List of product identifiers.
            - COLLECTION1: Satellite data collection number.
            - TOKEN: Valid NASA Earthdata API token.
        - Utility functions:
            - obtener_fecha_ayer(): returns (year, doy).
            - generar_url_api(): builds the API request URL.
            - esta_en_la_palma(): checks if coordinates cover La Palma.
            - es_de_noche(): checks if image is nighttime.

    Notes:
        - If the downloaded file is not a valid NetCDF file, it will be deleted.
        - Uses wget with an Authorization header for downloading.
    """
    # Obtener el año y el día juliano de ayer
    year, doy = obtener_fecha_ayer()

    # === CONFIGURACIÓN DE DIRECTORIO DE SALIDA ===
    # Ruta absoluta del script actual
    script_path = Path(__file__).resolve()

    # Subir hasta la raíz del proyecto (parece estar 3 niveles arriba desde el script)
    proyecto_dir = script_path.parents[3]

    # Ruta a la carpeta de salida dentro de A00_data
    base_output_dir = proyecto_dir / "A00_data" / "B_raw" / "La_Palma"
    
    # Obtener la fecha actual (o la fecha del día juliano, según tu caso)
    year, doy = obtener_fecha_ayer()  # Asumiendo que esta función devuelve el año y el día juliano de ayer

    # Definir el directorio específico para los archivos del día (a partir del directorio base)
    output_dir = base_output_dir / f"{year}_{doy}"

    # Crear el directorio si no existe 
    os.makedirs(output_dir, exist_ok=True)

    print(f"Ruta de salida: {output_dir}")
    print(f"\n📅 Downloading data for {year}-{doy}...")

    for product1 in PRODUCTS1:
        print(f"🔍 Searching for files of {product1}...")

        api_url = generar_url_api(product1, year, doy, COLLECTION1)
        headers = {"Authorization": f"Bearer {TOKEN}"}

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            file_list = response.json()

            if not file_list['content']:
                print(f"⚠️ No files found for {product1}")
                continue

            download_links = [f['downloadsLink'] for f in file_list['content']]

            for link in download_links:
                filename = link.split("/")[-1]
                filepath = os.path.join(output_dir, filename)

                print(f"📥 Downloading {filename}...")
                os.system(f'wget --header="Authorization: Bearer {TOKEN}" -O {filepath} {link}')

                try:
                    dataset = netCDF4.Dataset(filepath, 'r')
                    flag = dataset.getncattr('DayNightFlag')

                    sur = dataset.getncattr('SouthBoundingCoordinate')
                    norte = dataset.getncattr('NorthBoundingCoordinate')
                    este = dataset.getncattr('EastBoundingCoordinate')
                    oeste = dataset.getncattr('WestBoundingCoordinate')

                    if esta_en_la_palma(sur, norte, este, oeste) and es_de_noche(flag):
                        print("✔️ Valid file: nighttime over La Palma.")
                        break
                    else:
                        print("❌ Does not meet conditions. Deleting...")
                        os.remove(filepath)

                except Exception as e:
                    print(f"⚠️ Error processing {filename}: {e}")
                    os.remove(filepath)

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error accessing {product1}: {e}")

    print("✅ Download complete.")



if __name__ == "__main__":
    descargar_datos1()
