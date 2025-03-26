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

# Comprobar la forma de la primera imagen para asegurar que todas sean iguales
first_shape = None

# Procesar cada archivo CSV
for file in files:
    file_path = os.path.join(data_path, file)
    df = pd.read_csv(file_path)

    # Verificar que la columna 'Brightness_Temperature (K)' existe en los datos
    if 'Brightness_Temperature (K)' not in df.columns:
        print(f"⚠️ La columna 'Brightness_Temperature (K)' no está en el archivo {file}")
        continue

    # Extraer los valores de BT
    bt_values = df['Brightness_Temperature (K)'].values

    # Verificar la forma de la imagen
    if first_shape is None:
        first_shape = bt_values.shape
    elif bt_values.shape != first_shape:
        print(f"⚠️ La imagen {file} tiene una forma diferente: {bt_values.shape}. Se ajustará al tamaño de la primera imagen.")
        # Rellenar o recortar la imagen para que tenga el mismo tamaño
        bt_values = np.resize(bt_values, first_shape)
    
    # Almacenar los valores de BT
    bt_images.append(bt_values)

# Apilar las imágenes de BT para crear la matriz cúbica
bt_stack = np.stack(bt_images)

# Calcular la imagen de referencia promediada (promedio mensual)
average_bt = np.mean(bt_stack, axis=0)

# Guardar la imagen promedio de BT como referencia mensual
output_path = os.path.join(output_dir, 'monthly_reference_brightness_temperature.csv')
pd.DataFrame(average_bt).to_csv(output_path, index=False)
print(f"✅ Imagen de referencia mensual guardada en: {output_path}")
