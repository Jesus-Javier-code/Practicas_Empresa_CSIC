import os
import pandas as pd

# Obtener la ruta absoluta de este script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Subir un nivel para encontrar la raíz del repositorio
repo_root = os.path.abspath(os.path.join(script_dir, ".."))

# Ruta correcta del archivo de datos
data_path = os.path.join(repo_root, "data", "raw", "TIRVolcH_La_Palma_Dataset.xlsx")

# Comprobaciones antes de continuar
print("\n=== COMPROBACIÓN DE RUTAS ===")
print(f"📂 Directorio del script: {script_dir}")
print(f"📂 Raíz del repositorio: {repo_root}")
print(f"📄 Ruta del archivo: {data_path}")
print(f"❓ ¿El archivo existe? {'SÍ' if os.path.exists(data_path) else 'NO'}")

if not os.path.exists(data_path):
    print("\n🚨 ERROR: El archivo no se encuentra en la ruta esperada.")
    print("📂 Contenido real de la carpeta data/raw:")
    
    raw_dir = os.path.join(repo_root, "data", "raw")
    if os.path.exists(raw_dir):
        print(os.listdir(raw_dir))  # Mostrar lo que hay en data/raw
    else:
        print(f"🚨 La carpeta {raw_dir} NO EXISTE.")
    
    raise FileNotFoundError("⚠️ Mueve el archivo a la carpeta correcta y vuelve a ejecutar el script.")

# Directorio de salida
output_dir = os.path.join(repo_root, "data", "processed")
os.makedirs(output_dir, exist_ok=True)

try:
    print("\n📥 Cargando archivo...")
    df = pd.read_excel(data_path)

    # Procesamiento
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month

    # Guardar por año/mes
    for (year, month), group in df.groupby(["Year", "Month"]):
        output_path = os.path.join(output_dir, f"radiance_{year}-{month:02d}.csv")
        group.to_csv(output_path, index=False)
        print(f"✅ Guardado: {output_path}")

    print("\n🎉 ¡Proceso completado con éxito!")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
