import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
import numpy as np
import argparse

# Configuración de paths
CARPETA_IMAGENES = os.path.join("Practicas_Empresa_CSIC", "04_web", "images")
if not os.path.exists(CARPETA_IMAGENES):
    os.makedirs(CARPETA_IMAGENES)

ARCHIVO_SALIDA = os.path.join(CARPETA_IMAGENES, "potencia_radiativa.html")

def generar_datos_aleatorios(dias=7):
    """Genera datos aleatorios de ejemplo"""
    fecha_inicio = datetime.now() - timedelta(days=dias)
    timestamps = pd.date_range(fecha_inicio, periods=dias*24, freq='h')
    potencia = np.random.uniform(50, 200, size=len(timestamps)) * \
               (1 + 0.1 * np.sin(np.linspace(0, dias*np.pi, len(timestamps))))
    
    return pd.DataFrame({
        'Fecha_Hora': timestamps,
        'Potencia_Radiativa': potencia.round(2)
    })

def crear_grafica_interactiva(df, dias, mostrar=False):
    """Crea, guarda y opcionalmente muestra la gráfica"""
    fig = px.line(df, x='Fecha_Hora', y='Potencia_Radiativa',
                  title=f'Potencia Radiativa vs Tiempo (Últimos {dias} días)',
                  labels={'Potencia_Radiativa': 'Potencia (W/m²)', 'Fecha_Hora': 'Tiempo'},
                  template='plotly_white')
    
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Fecha y Hora",
        yaxis_title="Potencia Radiativa (W/m²)",
        showlegend=False,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        )
    )
    
    # Guardar como HTML interactivo
    fig.write_html(ARCHIVO_SALIDA, include_plotlyjs='cdn')
    print(f"Gráfica guardada en: {ARCHIVO_SALIDA}")
    
    # Mostrar la gráfica si se solicita
    if mostrar:
        fig.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dias', type=int, default=7, 
                       help='Número de días a visualizar (por defecto: 7)')
    parser.add_argument('--mostrar', action='store_true',
                       help='Mostrar la gráfica interactiva en una ventana')
    args = parser.parse_args()
    
    datos = generar_datos_aleatorios(args.dias)
    crear_grafica_interactiva(datos, args.dias, args.mostrar)