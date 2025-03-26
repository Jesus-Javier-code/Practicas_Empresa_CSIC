import os
import pandas as pd

# 1. Obtener la ruta CORRECTA al archivo
# (Modificado para tu estructura específica)
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, '..'))  # Sube un nivel desde processing

# Ruta ABSOLUTA y CORRECTA para tus datos
data_path = os.path.join(repo_root, 'Practicas_Empresa_CSIC', 'data', 'raw', 'TIRVolcH_La_Palma_Dataset.xlsx')

# 2. Verificación EXTENDIDA (para diagnóstico)
print("\n=== DEBUGGING INFORMATION ===")
print(f"Directorio del script: {script_dir}")
print(f"Raíz del repositorio: {repo_root}")
print(f"Ruta completa al archivo: {data_path}")
print(f"¿Existe el archivo?: {'SÍ' if os.path.exists(data_path) else 'NO'}")

# Verificar directorio raw
raw_dir = os.path.join(repo_root, 'Practicas_Empresa_CSIC', 'data', 'raw')
print(f"\nContenido de {raw_dir}:")
try:
    print(os.listdir(raw_dir))
except FileNotFoundError:
    print("¡El directorio no existe!")

# 3. Carga del archivo con manejo de errores
if not os.path.exists(data_path):
    raise FileNotFoundError(
        f"\nERROR: No se encuentra el archivo Excel.\n"
        f"Ruta esperada: {data_path}\n"
        f"Por favor verifica:\n"
        f"1. Que el archivo existe exactamente con ese nombre\n"
        f"2. Que está en la carpeta correcta\n"
        f"3. Directorio actual: {os.getcwd()}\n"
    )

try:
    print("\nCargando archivo Excel...")
    df = pd.read_excel(data_path)
    print("¡Archivo cargado correctamente!")
    
    # 4. Procesamiento (ejemplo básico)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    
    # 5. Guardar resultados
    output_dir = os.path.join(repo_root, 'Practicas_Empresa_CSIC', 'data', 'processed')
    os.makedirs(output_dir, exist_ok=True)
    
    for (year, month), group in df.groupby(["Year", "Month"]):
        output_path = os.path.join(output_dir, f"radiance_{year}-{month:02d}.csv")
        group.to_csv(output_path, index=False)
        print(f"Guardado: {output_path}")
    
    print("\n¡Proceso completado con éxito!")

except Exception as e:
    print(f"\nERROR durante el procesamiento: {str(e)}")