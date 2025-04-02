import os
import requests
import netCDF4
from utils import obtener_fecha_ayer, generar_url_api, esta_en_la_palma, es_de_noche

TOKEN = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6Im1vbmljYW1hcmlucyIsImV4cCI6MTc0NzY0NTM3NCwiaWF0IjoxNzQyNDYxMzc0LCJpc3MiOiJodHRwczovL3Vycy5lYXJ0aGRhdGEubmFzYS5nb3YiLCJpZGVudGl0eV9wcm92aWRlciI6ImVkbF9vcHMiLCJhY3IiOiJlZGwiLCJhc3N1cmFuY2VfbGV2ZWwiOjN9.j63ZKbiDQ3j7C4bbRUJEQWCMnsC3SLesLvVQuJrudNHw69IoLvX-CW70BhHiQFYC8jVn0XPRKHptlgNp4yCBEwtLdXoTswsEDD9YhaCFOcZEyRA0nG-RXlYO6gcy8Gv9avn3qU6jb9-nUDN0HaWHJUW3tL0aBgTDaY0mkCbOWHxCmGl51aHR0icdAv_G4aJJ1bz5t0f4mactbJht-9t0b2HAZ0iR7T1KAY2ZaBChwwlLkWCKf5N6ffBSWBM9QB_fYQhnkXVnyTIRztx3Z2wZkDiGwQobOPTd3gryH0vx3-dxVV08tXz-PWftVmyRqfZz7smbnaznAlB1MGuo-zBH0A"  


PRODUCTS1 = ["VJ102IMG", "VJ103IMG"]
COLLECTION1 = "5201"



def descargar_datos1():
    year, doy = obtener_fecha_ayer()
    output_dir = f"./00_data/raw/data_VJ/{year}_{doy}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n📅 Descargando datos para {year}-{doy}...")

    for product1 in PRODUCTS1:
        print(f"🔍 Buscando archivos de {product1}...")

        api_url = generar_url_api(product1, year, doy, COLLECTION1)
        headers = {"Authorization": f"Bearer {TOKEN}"}

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            file_list = response.json()

            if not file_list['content']:
                print(f"⚠️ No se encontraron archivos para {product1}")
                continue

            download_links = [f['downloadsLink'] for f in file_list['content']]

            for link in download_links:
                filename = link.split("/")[-1]
                filepath = os.path.join(output_dir, filename)

                print(f"📥 Descargando {filename}...")
                os.system(f'wget --header="Authorization: Bearer {TOKEN}" -O {filepath} {link}')

                try:
                    dataset = netCDF4.Dataset(filepath, 'r')
                    flag = dataset.getncattr('DayNightFlag')

                    sur = dataset.getncattr('SouthBoundingCoordinate')
                    norte = dataset.getncattr('NorthBoundingCoordinate')
                    este = dataset.getncattr('EastBoundingCoordinate')
                    oeste = dataset.getncattr('WestBoundingCoordinate')

                    if esta_en_la_palma(sur, norte, este, oeste) and es_de_noche(flag):
                        print("✔️ Archivo válido para La Palma de noche.")
                        break
                    else:
                        print("❌ No cumple condiciones. Eliminando...")
                        os.remove(filepath)

                except Exception as e:
                    print(f"⚠️ Error procesando {filename}: {e}")
                    os.remove(filepath)

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error accediendo a {product1}: {e}")

    print("✅ Descarga completada.")

if __name__ == "__main__":
    descargar_datos1()





PRODUCTS = ["VNP02IMG", "VNP03IMG"]
COLLECTION = "5200"

def descargar_datos():
    year, doy = obtener_fecha_ayer()
    output_dir = f"./00_data/raw/data_VN/{year}_{doy}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n📅 Descargando datos para {year}-{doy}...")

    for product in PRODUCTS:
        print(f"🔍 Buscando archivos de {product}...")

        api_url = generar_url_api(product, year, doy, COLLECTION)
        headers = {"Authorization": f"Bearer {TOKEN}"}

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
                os.system(f'wget --header="Authorization: Bearer {TOKEN}" -O {filepath} {link}')

                try:
                    dataset = netCDF4.Dataset(filepath, 'r')
                    flag = dataset.getncattr('DayNightFlag')

                    sur = dataset.getncattr('SouthBoundingCoordinate')
                    norte = dataset.getncattr('NorthBoundingCoordinate')
                    este = dataset.getncattr('EastBoundingCoordinate')
                    oeste = dataset.getncattr('WestBoundingCoordinate')

                    if esta_en_la_palma(sur, norte, este, oeste) and es_de_noche(flag):
                        print("✔️ Archivo válido para La Palma de noche.")
                        break
                    else:
                        print("❌ No cumple condiciones. Eliminando...")
                        os.remove(filepath)

                except Exception as e:
                    print(f"⚠️ Error procesando {filename}: {e}")
                    os.remove(filepath)

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error accediendo a {product}: {e}")

    print("✅ Descarga completada.")

if __name__ == "__main__":
    descargar_datos()

