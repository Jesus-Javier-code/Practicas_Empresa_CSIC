'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Cargar el archivo de Excel
file_path = "TIRVolcH_La_Palma_Dataset.xlsx"  # Ajusta la ruta si es necesario
df = pd.read_excel(file_path, sheet_name="LaPalma_TIRVolcH_Filtered_Data")
'''
'''
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Obtener la ruta absoluta de este script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Ajuste importante: la raíz del repo debe ser el nombre correcto
repo_root = os.path.abspath(os.path.join(script_dir, ".."))  # Esto sube un nivel correctamente

# Ruta correcta del archivo
data_path = os.path.join(repo_root, "data", "raw", "TIRVolcH_La_Palma_Dataset.xlsx")
c = 2 +2 
# Debugging
print("\n=== DEBUGGING INFORMATION ===")
print(f"Directorio del script: {script_dir}")
print(f"Raíz del repositorio: {repo_root}")
print(f"Ruta completa al archivo: {data_path}")
print(f"¿Existe el archivo?: {'SÍ' if os.path.exists(data_path) else 'NO'}")

# Verificar si el archivo existe
if not os.path.exists(data_path):
    raw_dir = os.path.join(repo_root, "data", "raw")
    print(f"\nContenido de {raw_dir}:")
    if os.path.exists(raw_dir):
        print(os.listdir(raw_dir))  # Mostrar lo que hay en la carpeta
    else:
        print(f"¡El directorio {raw_dir} no existe!")
    
    raise FileNotFoundError(
        f"\nERROR: No se encuentra el archivo Excel.\n"
        f"Ruta esperada: {data_path}\n"
        "Por favor verifica:\n"
        "1. Que el archivo existe exactamente con ese nombre\n"
        "2. Que está en la carpeta correcta\n"
        f"3. Directorio actual: {script_dir}"
    )
'''
# Directorio de salida
# Directorio de salida en data/raw/radiance_by_Year_Month_
output_dir = os.path.join(repo_root, "data", "processed", "radiance_by_Year_Month_")
os.makedirs(output_dir, exist_ok=True)  # Crear si no existe'
'''


# Leer el archivo Excel y procesar
print("\n📥 Cargando archivo...")
df = pd.read_excel(data_path)

# Definir constantes
sigma = 5.670e-8  # Constante de Stefan-Boltzmann (W/m²K⁴)
epsilon = 1  # Emisividad
A = 375 * 375  # Área del píxel VIIRS I5 en m²

# Aplicar interpolación iterativa para estimar BT_background
df["BT_background_Iter"] = df["Weekly_Mean_BT_Hottest_Pixel (Kelvin)"] - df["Weekly_Max_DT_Hottest_Pixel (Kelvin)"]

# Iterar para refinar el BT_background eliminando valores extremos
for _ in range(5):  # Iteramos varias veces para suavizar el fondo
    median_bg = df["BT_background_Iter"].median()  # Mediana como referencia
    df["BT_background_Iter"] = np.where(
        df["BT_background_Iter"] < median_bg,  # Si es menor que la mediana, ajustar
        (df["BT_background_Iter"] + median_bg) / 2,  # Suavizado
        df["BT_background_Iter"]
    )

# Calcular VRP_TIR con el nuevo BT_background iterativo
df["VRP_TIR_Iter (W)"] = sigma * epsilon * (
    df["Weekly_Mean_BT_Hottest_Pixel (Kelvin)"]**4 - df["BT_background_Iter"]**4
) * A

# Convertir a MW
df["VRP_TIR_Iter (MW)"] = df["VRP_TIR_Iter (W)"] / 1e6

# Graficar comparación entre VRP TIR oficial, calculado e iterativo
plt.figure(figsize=(10, 5))
plt.plot(df["Date"], df["Weekly_Max_VRP_TIR (MW)"], label="VRP TIR Oficial", linestyle='-', marker='.')
plt.plot(df["Date"], df["VRP_TIR_Iter (MW)"], label="VRP TIR Iterado", linestyle='--', marker='.')

plt.xlabel("Fecha")
plt.ylabel("Potencia Radiativa (MW)")
plt.title("Comparación de VRP TIR (Método Iterativo)")
plt.legend()
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

# Crear la carpeta de destino si no existe
output_folder = "web/images"
os.makedirs(output_folder, exist_ok=True)

# Guardar la gráfica en la carpeta `web/images/`
output_path = os.path.join(output_folder, "Graphic_Power_Rad.png")
plt.savefig(output_path, dpi=300)
plt.close()

print(f"Gráfica guardada en: {output_path}")'
'''

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Obtener la ruta absoluta de este script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Raíz del repositorio (sube un nivel desde este script)
repo_root = os.path.abspath(os.path.join(script_dir, ".."))

# Ruta del archivo Excel
data_path = os.path.join(repo_root, "data", "raw", "TIRVolcH_La_Palma_Dataset.xlsx")

# Debugging
print("\n=== DEBUGGING INFORMATION ===")
print(f"Directorio del script: {script_dir}")
print(f"Raíz del repositorio: {repo_root}")
print(f"Ruta completa al archivo: {data_path}")
print(f"¿Existe el archivo?: {'SÍ' if os.path.exists(data_path) else 'NO'}")

# Verificar si el archivo existe
if not os.path.exists(data_path):
    raw_dir = os.path.join(repo_root, "data", "raw")
    
    if os.path.exists(raw_dir):
        print(f"\nContenido de {raw_dir}: {os.listdir(raw_dir)}")
    else:
        print(f"¡El directorio {raw_dir} no existe!")

    raise FileNotFoundError(
        f"\nERROR: No se encuentra el archivo Excel en:\n{data_path}\n"
        "Verifica que:\n"
        "1. El archivo tiene el nombre correcto\n"
        "2. Está en la carpeta adecuada\n"
        f"3. El script se ejecuta en el directorio correcto ({script_dir})"
    )

# 📥 Cargar el archivo Excel
print("\n📥 Cargando archivo...")
df = pd.read_excel(data_path)

# Verificar si las columnas esperadas están en el DataFrame
expected_columns = [
    "Date", "Weekly_Mean_BT_Hottest_Pixel (Kelvin)", 
    "Weekly_Max_DT_Hottest_Pixel (Kelvin)", "Weekly_Max_VRP_TIR (MW)"
]

missing_columns = [col for col in expected_columns if col not in df.columns]
if missing_columns:
    raise ValueError(f"❌ ERROR: Las siguientes columnas faltan en el archivo: {missing_columns}")

print("✅ Archivo cargado correctamente con las columnas esperadas.")

# Convertir la columna "Date" a tipo datetime
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])  # Eliminar filas con fechas inválidas

# Definir constantes
sigma = 5.670e-8  # Constante de Stefan-Boltzmann (W/m²K⁴)
epsilon = 1  # Emisividad
A = 375 * 375  # Área del píxel VIIRS I5 en m²

# Aplicar interpolación iterativa para estimar BT_background
df["BT_background_Iter"] = df["Weekly_Mean_BT_Hottest_Pixel (Kelvin)"] - df["Weekly_Max_DT_Hottest_Pixel (Kelvin)"]

# Iterar para refinar el BT_background eliminando valores extremos
for _ in range(5):  # Iteramos varias veces para suavizar el fondo
    median_bg = df["BT_background_Iter"].median()  # Mediana como referencia
    df["BT_background_Iter"] = np.where(
        df["BT_background_Iter"] < median_bg,  # Si es menor que la mediana, ajustar
        (df["BT_background_Iter"] + median_bg) / 2,  # Suavizado
        df["BT_background_Iter"]
    )

# Calcular VRP_TIR con el nuevo BT_background iterativo
df["VRP_TIR_Iter (W)"] = sigma * epsilon * (
    df["Weekly_Mean_BT_Hottest_Pixel (Kelvin)"]**4 - df["BT_background_Iter"]**4
) * A

# Convertir a MW
df["VRP_TIR_Iter (MW)"] = df["VRP_TIR_Iter (W)"] / 1e6

# 📊 Graficar comparación entre VRP TIR oficial, calculado e iterativo
plt.figure(figsize=(10, 5))
plt.plot(df["Date"], df["Weekly_Max_VRP_TIR (MW)"], label="VRP TIR Oficial", linestyle='-', marker='.')
plt.plot(df["Date"], df["VRP_TIR_Iter (MW)"], label="VRP TIR Iterado", linestyle='--', marker='.')

plt.xlabel("Fecha")
plt.ylabel("Potencia Radiativa (MW)")
plt.title("Comparación de VRP TIR (Método Iterativo)")
plt.legend()
plt.xticks(rotation=45)
plt.grid(True)

# 📂 Crear la carpeta de destino si no existe
output_folder = os.path.join(repo_root, "web", "images")
os.makedirs(output_folder, exist_ok=True)

# 📷 Guardar la gráfica en la carpeta `web/images/`
output_path = os.path.join(output_folder, "Graphic_Power_Rad.png")
print(f"Intentando guardar la imagen en: {output_path}")

plt.savefig(output_path, dpi=300, format="png")
plt.close()

print(f"✅ Gráfica guardada en: {output_path}")

