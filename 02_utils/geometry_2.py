import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
import numpy as np

# Configuración de paths
CARPETA_IMAGENES = "Practicas_Empresa_CSIC/04_web/images"
if not os.path.exists(CARPETA_IMAGENES):
    os.makedirs(CARPETA_IMAGENES)

ARCHIVO_SALIDA = os.path.join(CARPETA_IMAGENES, "potencia_radiativa.html")

def generar_datos_aleatorios(dias=7):
    """Genera datos aleatorios de ejemplo (serán reemplazados por tus datos reales)"""
    fecha_inicio = datetime.now() - timedelta(days=dias)
    timestamps = pd.date_range(fecha_inicio, periods=dias*24, freq='H')
    potencia = np.random.uniform(50, 200, size=len(timestamps)) * \
               (1 + 0.1 * np.sin(np.linspace(0, dias*np.pi, len(timestamps))))
    
    return pd.DataFrame({
        'Fecha_Hora': timestamps,
        'Potencia_Radiativa': potencia
    })

def crear_grafica_interactiva(df, dias):
    """Crea y guarda la gráfica interactiva"""
    fig = px.line(df, x='Fecha_Hora', y='Potencia_Radiativa',
                  title=f'Potencia Radiativa vs Tiempo (Últimos {dias} días)',
                  labels={'Potencia_Radiativa': 'Potencia (W/m²)', 'Fecha_Hora': 'Tiempo'},
                  template='plotly_white')
    
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Fecha y Hora",
        yaxis_title="Potencia Radiativa (W/m²)",
        showlegend=False
    )
    
    # Guardar como HTML interactivo
    fig.write_html(ARCHIVO_SALIDA)
    print(f"Gráfica guardada en: {ARCHIVO_SALIDA}")

if __name__ == "__main__":
    # Parámetro configurable - número de días a visualizar
    DIAS_A_MOSTRAR = 7  # Puedes cambiar esto o hacerlo un parámetro de entrada
    
    # Generar datos (reemplazar con tus datos reales)
    datos = generar_datos_aleatorios(DIAS_A_MOSTRAR)
    
    # Crear y guardar gráfica
    crear_grafica_interactiva(datos, DIAS_A_MOSTRAR)
