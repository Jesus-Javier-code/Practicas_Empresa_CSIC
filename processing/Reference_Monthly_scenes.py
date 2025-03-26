import os
import numpy as np
import pandas as pd

# Definir rutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Carpeta raíz del proyecto
data_path = os.path.join(base_dir, 'data', 'processed', 'brightness_temperature_by_Year_Month')  # Carpeta con las imágenes BT
output_dir = os.path.join(base_dir, 'data', 'processed', 'Generation_Monthly_Reference')  # Carpeta de salida para la referencia mensual

# Crear la carpeta de salida si no existe
os.makedirs(output_dir, exist_ok=True)

# Listar todos los archivos CSV en el directorio de BT
files = [f for f in os.listdir(data_path) if f.endswith('.csv')]

# Lista para almacenar las imágenes de BT
bt_images = []

# Procesar cada archivo CSV
for file in files:
    file_path = os.path.join(data_path, file)
    df = pd.read_csv(file_path)

    # Verificar que la columna 'Brightness_Temperature (K)' existe en los datos
    if 'Brightness_Temperature (K)' not in df.columns:
        print(f"⚠️ La columna 'Brightness_Temperature (K)' no está en el archivo {file}")
        continue

    # Almacenar los valores de BT en la lista
    bt_images.append(df['Brightness_Temperature (K)'].values)

# Apilar las imágenes de BT para crear la matriz cúbica
bt_stack = np.stack(bt_images)

# Calcular la imagen de referencia promediada (promedio mensual)
average_bt = np.mean(bt_stack, axis=0)

# Guardar la imagen promedio de BT como referencia mensual
output_path = os.path.join(output_dir, 'monthly_reference_brightness_temperature.csv')
pd.DataFrame(average_bt).to_csv(output_path, index=False)
print(f"✅ Imagen de referencia mensual guardada en: {output_path}")
