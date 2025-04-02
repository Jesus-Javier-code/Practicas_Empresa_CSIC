import pandas as pd
import numpy as np
import plotly.express as px
import panel as pn
import datetime
import os

# Crear datos aleatorios de potencia radiativa
np.random.seed(42)
num_datos = 100
fechas = pd.date_range(start='2024-01-01', periods=num_datos, freq='D')
potencia_radiativa = np.random.uniform(10, 100, num_datos)
df = pd.DataFrame({'Fecha': fechas, 'Potencia Radiativa': potencia_radiativa})

# Widget para seleccionar el rango de fechas
date_picker = pn.widgets.DateRangeSlider(
    name='Selecciona el rango de fechas',
    start=df['Fecha'].min(),
    end=df['Fecha'].max(),
    value=(df['Fecha'].min(), df['Fecha'].max())
)

def actualizar_grafico(rango):
    fecha_inicio, fecha_fin = rango
    df_filtrado = df[(df['Fecha'] >= fecha_inicio) & (df['Fecha'] <= fecha_fin)]
    fig = px.line(df_filtrado, x='Fecha', y='Potencia Radiativa', title='Potencia Radiativa vs. Tiempo')
    return fig

# Panel interactivo
grafico = pn.bind(actualizar_grafico, date_picker)
layout = pn.Column(date_picker, pn.panel(grafico))

# Guardar HTML en carpeta específica
output_folder = "graficas_generadas"
os.makedirs(output_folder, exist_ok=True)
output_path = os.path.join(output_folder, "grafica_potencia.html")
layout.save(output_path)

print(f"Gráfica guardada en {output_path}")
