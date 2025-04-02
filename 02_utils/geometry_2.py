# geometry_2.py - Versión final
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
import numpy as np
import argparse
import sys

def main():
    try:
        # Configurar rutas
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        carpeta_imagenes = os.path.join(base_dir, "04_web", "images")
        os.makedirs(carpeta_imagenes, exist_ok=True)
        archivo_salida = os.path.join(carpeta_imagenes, "potencia_radiativa.html")

        # Generar datos
        dias = 7  # Puedes hacer esto configurable con argparse
        fecha_inicio = datetime.now() - timedelta(days=dias)
        timestamps = pd.date_range(fecha_inicio, periods=dias*24, freq='h')
        potencia = np.random.uniform(50, 200, len(timestamps)) * (1 + 0.1 * np.sin(np.linspace(0, dias*np.pi, len(timestamps))))
        
        df = pd.DataFrame({
            'Fecha_Hora': timestamps,
            'Potencia_Radiativa': potencia.round(2)
        })

        # Crear gráfica
        fig = px.line(df, x='Fecha_Hora', y='Potencia_Radiativa',
                     title=f'Radiative Power (Últimos {dias} días)',
                     template='plotly_white')
        
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1d", step="day", stepmode="backward"),
                        dict(count=7, label="1w", step="day", stepmode="backward"),
                        dict(step="all", label="Todo")
                    ])
                ),
                rangeslider=dict(visible=True),
                type="date"
            ),
            hovermode="x unified"
        )

        # Guardar gráfica
        fig.write_html(archivo_salida, include_plotlyjs='cdn')
        print(f"Gráfica generada en: {archivo_salida}")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)