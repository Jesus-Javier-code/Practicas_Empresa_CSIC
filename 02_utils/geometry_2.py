import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
import numpy as np
import argparse

def configurar_rutas():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    carpeta_imagenes = os.path.join(base_dir, "04_web", "images")
    
    if not os.path.exists(carpeta_imagenes):
        os.makedirs(carpeta_imagenes)
    
    return os.path.join(carpeta_imagenes, "potencia_radiativa.html")

def generar_datos(dias=7):
    fecha_inicio = datetime.now() - timedelta(days=dias)
    timestamps = pd.date_range(fecha_inicio, periods=dias*24, freq='h')
    potencia = np.random.uniform(50, 200, size=len(timestamps)) * \
               (1 + 0.1 * np.sin(np.linspace(0, dias*np.pi, len(timestamps))))
    
    return pd.DataFrame({
        'Fecha_Hora': timestamps,
        'Potencia_Radiativa': potencia.round(2)
    })

def crear_grafica_interactiva(df, dias):
    fig = px.line(df, x='Fecha_Hora', y='Potencia_Radiativa',
                 title=f'Potencia Radiativa vs Tiempo (Últimos {dias} días)',
                 template='plotly_white')
    
    # Configuración del layout
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=3, label="3d", step="day", stepmode="backward"),
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(step="all", label="Todo")
                ]),
                bgcolor='lightgray',
                activecolor='blue'
            ),
            rangeslider=dict(visible=True),
            type="date"
        ),
        yaxis_title="Potencia Radiativa (W/m²)",
        hovermode="x unified",
        showlegend=False,
        height=600
    )
    
    # Configuración de la barra de herramientas (CORRECCIÓN: fuera de update_layout)
    fig.update_layout(
        modebar=dict(
            orientation='v',
            bgcolor='rgba(255,255,255,0.7)'
        )
    )
    
    # Configuración adicional para los botones de la barra de herramientas
    fig.update_layout(
        config={
            'modeBarButtonsToAdd': [
                'zoom2d',
                'pan2d',
                'select2d',
                'lasso2d',
                'zoomIn2d',
                'zoomOut2d',
                'resetScale2d',
                'toImage'
            ]
        }
    )
    
    return fig

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dias', type=int, default=7)
    args = parser.parse_args()
    
    archivo_salida = configurar_rutas()
    datos = generar_datos(args.dias)
    fig = crear_grafica_interactiva(datos, args.dias)
    
    fig.write_html(archivo_salida, include_plotlyjs='cdn', config={'responsive': True})
    print(f"Gráfica interactiva guardada en: {archivo_salida}")