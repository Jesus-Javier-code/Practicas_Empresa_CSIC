import os
import pandas as pd

# Obtener la ruta absoluta de este script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Ajuste importante: la raíz del repo debe ser el nombre correcto
repo_root = os.path.abspath(os.path.join(script_dir, ".."))  # Esto sube un nivel correctamente

# Ruta correcta del archivo
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

# Directorio de salida
# Directorio de salida en data/raw/radiance_by_Year_Month_
output_dir = os.path.join(repo_root, "data", "processed", "radiance_by_Year_Month_")
os.makedirs(output_dir, exist_ok=True)  # Crear si no existe


# Leer el archivo Excel y procesar
try:
    print("\n📥 Cargando archivo...")
    df = pd.read_excel(data_path)

    # Procesamiento
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month

    # Guardar por año/mes
    for (year, month), group in df.groupby(["Year", "Month"]):
        year = int(year)  # Convertir a entero
        month = int(month)  # Convertir a entero
        filename = f"radiance_{year}-{month:02d}.csv"
        output_path = os.path.join(output_dir, filename)
        group.to_csv(output_path, index=False)
        print(f"✅ Guardado: {output_path}")


    print("\n🎉 ¡Proceso completado con éxito!")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
