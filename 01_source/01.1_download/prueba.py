from pathlib import Path

# Ruta correcta: subir dos niveles para salir de "01_source/01.1_download"
file = Path("../../00_data/processed/BT_by_Year_Month_Day/TB_By_Year_Month_Day.nc")

print("Ruta absoluta que se está usando:", file.resolve())
print("El archivo existe?", file.exists())

