from pathlib import Path

# Construcción de la ruta relativa desde donde ejecutas el script
file = Path("../00_data/processed/BT_by_Year_Month_Day/TB_By_Year_Month_Day.nc")

# Mostrar información útil
print("Ruta absoluta que se está usando:", file.resolve())
print("El archivo existe?", file.exists())

