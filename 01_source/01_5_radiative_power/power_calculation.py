
import requests
from io import StringIO
import os
import numpy as np
import pandas as pd

# Definir rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Carpeta raíz del proyecto
data_path = os.path.join(base_dir, 'data', 'processed', 'radiance_by_Year_Month')
output_dir = os.path.join(base_dir, 'data', 'processed', 'brightness_temperature_by_Year_Month')


def obtener_archivos_github(folder_path):
    """
    Obtiene la lista de archivos CSV desde el repositorio de GitHub en una carpeta específica.
    """
    api_url = f"https://api.github.com/repos/Jesus-Javier-code/Practicas_Empresa_CSIC/contents/{folder_path}"
    response = requests.get(api_url)
    if response.status_code != 200:
        raise ValueError("No se pudo acceder al repositorio de GitHub.")
    
    files = response.json()
    return [file["download_url"] for file in files if file["name"].endswith(".csv")]

def cargar_datos_github(folder_path):
    """
    Carga y combina datos CSV desde el repositorio de GitHub.
    """
    csv_urls = obtener_archivos_github(folder_path)
    dataframes = []
    
    for url in csv_urls:
        response = requests.get(url)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            dataframes.append(df)
    
    if not dataframes:
        raise ValueError("No se encontraron datos válidos en los archivos CSV.")
    
    return pd.concat(dataframes, ignore_index=True)

def calcular_potencia_radiativa(folder_path, area=140625, emisividad=1, output_file="resultado_potencia.csv"):
    """
    Carga datos desde GitHub y calcula la potencia radiativa.
    """
    df = cargar_datos_github(folder_path)
    
    # Renombrar columnas para evitar problemas con espacios
    df.rename(columns={
        "Date": "date",
        "Weekly_Max_VRP_TIR (MW)": "Weekly_Max_VRP_TIR(MW)",
        "Weekly_Mean_BT_Hottest_Pixel (Kelvin)": "Weekly_Mean_BT_Hottest_Pixel(Kelvin)",
        "Weekly_Max_DT_Hottest_Pixel (Kelvin)": "Weekly_Mean_DT_Hottest_Pixel(Kelvin)"
    }, inplace=True)
    
    # Verificar que las columnas esperadas están en el archivo
    expected_columns = ["date", "Weekly_Max_VRP_TIR(MW)", 
                         "Weekly_Mean_BT_Hottest_Pixel(Kelvin)", 
                         "Weekly_Mean_DT_Hottest_Pixel(Kelvin)"]
    
    if not all(col in df.columns for col in expected_columns):
        raise ValueError("Los archivos CSV no tienen las columnas esperadas.")
    
    # Calcular la potencia radiativa (ΦRad = sigma * emisividad * A * (BT^4 - BTbg^4))
    SIGMA = 5.67e-8  # W/m²K⁴
    df["Radiative_Power(W)"] = SIGMA * emisividad * area * (
        np.power(df["Weekly_Mean_BT_Hottest_Pixel(Kelvin)"], 4) - 
        np.power(df["Weekly_Mean_DT_Hottest_Pixel(Kelvin)"], 4)
    )
    
    # Guardar resultado en CSV
    df.to_csv(output_file, index=False)
    print(f"Archivo guardado como {output_file}")
    
    return df

# Ejemplo de uso
if __name__ == "__main__":
    folder_path = "data/processed/radiance_by_Year_Month"
    df_resultado = calcular_potencia_radiativa(folder_path)
    print(df_resultado.head())


'''
import pandas as pd
import numpy as np
import os
import requests
from io import StringIO

def obtener_archivos_github(repo_url, folder_path):
    """
    Obtiene la lista de archivos CSV desde un repositorio de GitHub en una carpeta específica.
    """
    api_url = f"https://api.github.com/repos/{repo_url}/contents/{folder_path}"
    response = requests.get(api_url)
    if response.status_code != 200:
        raise ValueError("No se pudo acceder al repositorio de GitHub.")
    
    files = response.json()
    return [file["download_url"] for file in files if file["name"].endswith(".csv")]

def cargar_datos_github(repo_url, folder_path):
    """
    Carga y combina datos CSV desde un repositorio de GitHub.
    """
    csv_urls = obtener_archivos_github(repo_url, folder_path)
    dataframes = []
    
    for url in csv_urls:
        response = requests.get(url)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            dataframes.append(df)
    
    if not dataframes:
        raise ValueError("No se encontraron datos válidos en los archivos CSV.")
    
    return pd.concat(dataframes, ignore_index=True)

def calcular_potencia_radiativa(repo_url, folder_path, area=140625, emisividad=1):
    """
    Carga datos desde GitHub y calcula la potencia radiativa.
    """
    df = cargar_datos_github(repo_url, folder_path)
    
    # Renombrar columnas para evitar problemas con espacios
    df.rename(columns={
        "Date": "date",
        "Weekly_Max_VRP_TIR (MW)": "Weekly_Max_VRP_TIR(MW)",
        "Weekly_Mean_BT_Hottest_Pixel (Kelvin)": "Weekly_Mean_BT_Hottest_Pixel(Kelvin)",
        "Weekly_Max_DT_Hottest_Pixel (Kelvin)": "Weekly_Mean_DT_Hottest_Pixel(Kelvin)"
    }, inplace=True)
    
    # Verificar que las columnas esperadas están en el archivo
    expected_columns = ["date", "Weekly_Max_VRP_TIR(MW)", 
                         "Weekly_Mean_BT_Hottest_Pixel(Kelvin)", 
                         "Weekly_Mean_DT_Hottest_Pixel(Kelvin)"]
    
    if not all(col in df.columns for col in expected_columns):
        raise ValueError("Los archivos CSV no tienen las columnas esperadas.")
    
    # Calcular la potencia radiativa (ΦRad = sigma * emisividad * A * (BT^4 - BTbg^4))
    SIGMA = 5.67e-8  # W/m²K⁴
    df["Radiative_Power(W)"] = SIGMA * emisividad * area * (
        np.power(df["Weekly_Mean_BT_Hottest_Pixel(Kelvin)"], 4) - 
        np.power(df["Weekly_Mean_DT_Hottest_Pixel(Kelvin)"], 4)
    )
    
    return df

# Ejemplo de uso
if __name__ == "__main__":
    repo_url = "https://github.com/Jesus-Javier-code/Practicas_Empresa_CSIC"  # Reemplaza con el usuario/repositorio real
    folder_path = "data/processed/radiance_by_Year_Month"
    df_resultado = calcular_potencia_radiativa(repo_url, folder_path)
    print(df_resultado.head())
    df_resultado.to_csv("resultado_potencia.csv", index=False)'
    '''

