'''
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import numpy as np
import os
from dash.dependencies import Input, Output

# Paso 1: Generación de datos ficticios
# Definir el rango de fechas (por ejemplo, un mes de datos)
fechas = pd.date_range(start="2022-09-01", end="2022-09-30", freq="D")

# Generar valores ficticios de potencia radiativa (en unidades arbitrarias)
np.random.seed(42)  # Para que los datos sean reproducibles
potencia_radiativa = np.random.normal(loc=500, scale=100, size=len(fechas))  # media 500, desviación 100

# Limitar los valores de la potencia radiativa a ser siempre positivos
potencia_radiativa = np.abs(potencia_radiativa)

# Crear un DataFrame con los datos
df = pd.DataFrame({
    'Fecha': fechas,
    'Potencia_Radiativa': potencia_radiativa
})

# Guardar los datos en un archivo CSV (en el mismo directorio)
csv_path = 'actividad_volcanica_potencia.csv'
df.to_csv(csv_path, index=False)

# Paso 2: Crear la aplicación Dash
app = dash.Dash(__name__)

# Convertir la columna de fecha a datetime
df['Fecha'] = pd.to_datetime(df['Fecha'])

# Crear la figura inicial (por ejemplo, una gráfica de la potencia radiativa con respecto al tiempo)
fig = px.line(df, x='Fecha', y='Potencia_Radiativa', title='Potencia Radiativa en La Palma')

# Definir el layout de la aplicación
app.layout = html.Div([
    # Título
    html.H1("Actividad Volcánica en La Palma: Potencia Radiativa"),

    # Filtro de selección de fechas
    dcc.DatePickerRange(
        id='fecha-selector',
        start_date=df['Fecha'].min().date(),
        end_date=df['Fecha'].max().date(),
        display_format='YYYY-MM-DD',
        style={'padding': '10px'}
    ),

    # Gráfico interactivo
    dcc.Graph(id='grafico', figure=fig)
])

# Callback para actualizar el gráfico según la selección de fechas
@app.callback(
    Output('grafico', 'figure'),
    [Input('fecha-selector', 'start_date'),
     Input('fecha-selector', 'end_date')]
)
def actualizar_grafico(start_date, end_date):
    # Filtrar los datos según el rango de fechas seleccionado
    df_filtrado = df[(df['Fecha'] >= start_date) & (df['Fecha'] <= end_date)]
    
    # Crear la nueva figura con los datos filtrados
    fig_filtrada = px.line(df_filtrado, x='Fecha', y='Potencia_Radiativa', title='Potencia Radiativa en La Palma')
    
    return fig_filtrada

# Paso 3: Guardar el archivo HTML generado
if __name__ == '__main__':
    # Crear una carpeta para almacenar el HTML si no existe
    carpeta_salida = 'Practicas_Empresa_CSIC/web/images'
    os.makedirs(carpeta_salida, exist_ok=True)

    # Guardar el archivo HTML del gráfico en la carpeta 'repositorio/resultado'
    app.run(debug=True, use_reloader=False, port=8051)  # Cambia el puerto a 8051 o cualquier otro

    #app.run(debug=True, use_reloader=False)  # Esto ejecuta la aplicación Dash
    # Guardar el archivo HTML al finalizar la ejecución
    # Aquí, Dash por defecto ya genera un archivo HTML en la web que se puede abrir en el navegador.
'''
'''
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import numpy as np
import os
from dash.dependencies import Input, Output
import plotly.io as pio

# Paso 1: Generación de datos ficticios
fechas = pd.date_range(start="2022-09-01", end="2022-09-30", freq="D")
np.random.seed(42)
potencia_radiativa = np.random.normal(loc=500, scale=100, size=len(fechas))
potencia_radiativa = np.abs(potencia_radiativa)

df = pd.DataFrame({
    'Fecha': fechas,
    'Potencia_Radiativa': potencia_radiativa
})

# Paso 2: Crear la aplicación Dash
app = dash.Dash(__name__)

# Convertir la columna de fecha a datetime
df['Fecha'] = pd.to_datetime(df['Fecha'])

# Crear la figura inicial
fig = px.line(df, x='Fecha', y='Potencia_Radiativa', title='Potencia Radiativa en La Palma')

# Definir el layout de la aplicación
app.layout = html.Div([
    html.H1("Actividad Volcánica en La Palma: Potencia Radiativa"),

    dcc.DatePickerRange(
        id='fecha-selector',
        start_date=df['Fecha'].min().date(),
        end_date=df['Fecha'].max().date(),
        display_format='YYYY-MM-DD',
        style={'padding': '10px'}
    ),

    dcc.Graph(id='grafico', figure=fig)
])

@app.callback(
    Output('grafico', 'figure'),
    [Input('fecha-selector', 'start_date'),
     Input('fecha-selector', 'end_date')]
)
def actualizar_grafico(start_date, end_date):
    df_filtrado = df[(df['Fecha'] >= start_date) & (df['Fecha'] <= end_date)]
    fig_filtrada = px.line(df_filtrado, x='Fecha', y='Potencia_Radiativa', title='Potencia Radiativa en La Palma')
    return fig_filtrada

# Paso 3: Guardar la figura como un archivo HTML estático

def save_html_static():
    try:
        # Carpeta donde se guardará el archivo HTML
        carpeta_salida = os.path.join(os.getcwd(), 'repositorio', 'resultado')
        os.makedirs(carpeta_salida, exist_ok=True)  # Crea la carpeta si no existe

        # Ruta del archivo HTML
        html_path = os.path.join(carpeta_salida, 'grafico_potencia_radiativa.html')

        # Guardar el gráfico como HTML
        pio.write_html(fig, file=html_path, auto_open=False)

        # Mostrar confirmación en la terminal
        print(f"✅ Archivo HTML guardado correctamente en: {html_path}")

    except Exception as e:
        print(f"❌ Error al guardar el archivo HTML: {e}")

# Llamar a la función para guardar el archivo HTML antes de iniciar el servidor Dash
save_html_static()

# Paso 4: Iniciar la aplicación Dash
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)  # Ejecuta el servidor Dash
'''


import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import numpy as np
import os
from dash.dependencies import Input, Output
import plotly.io as pio

# Paso 1: Generación de datos ficticios
fechas = pd.date_range(start="2022-09-01", end="2022-09-30", freq="D")
np.random.seed(42)
potencia_radiativa = np.random.normal(loc=500, scale=100, size=len(fechas))
potencia_radiativa = np.abs(potencia_radiativa)

df = pd.DataFrame({
    'Fecha': fechas,
    'Potencia_Radiativa': potencia_radiativa
})

# Paso 2: Crear la aplicación Dash
app = dash.Dash(__name__)

# Convertir la columna de fecha a datetime
df['Fecha'] = pd.to_datetime(df['Fecha'])

# Crear la figura inicial
fig = px.line(df, x='Fecha', y='Potencia_Radiativa', title='Potencia Radiativa en La Palma')

# Definir el layout de la aplicación
app.layout = html.Div([
    html.H1("Actividad Volcánica en La Palma: Potencia Radiativa"),

    dcc.DatePickerRange(
        id='fecha-selector',
        start_date=df['Fecha'].min().date(),
        end_date=df['Fecha'].max().date(),
        display_format='YYYY-MM-DD',
        style={'padding': '10px'}
    ),

    dcc.Graph(id='grafico', figure=fig)
])

@app.callback(
    Output('grafico', 'figure'),
    [Input('fecha-selector', 'start_date'),
     Input('fecha-selector', 'end_date')]
)
def actualizar_grafico(start_date, end_date):
    df_filtrado = df[(df['Fecha'] >= start_date) & (df['Fecha'] <= end_date)]
    fig_filtrada = px.line(df_filtrado, x='Fecha', y='Potencia_Radiativa', title='Potencia Radiativa en La Palma')
    return fig_filtrada

# Paso 3: Guardar la figura como un archivo HTML estático

def save_html_static():
    try:
        # Carpeta donde se guardará el archivo HTML
        carpeta_salida = os.path.join(os.getcwd(), 'web', 'images')
        os.makedirs(carpeta_salida, exist_ok=True)  # Crea la carpeta si no existe

        # Ruta del archivo HTML
        html_path = os.path.join(carpeta_salida, 'grafico_potencia_radiativa.html')

        # Guardar el gráfico como HTML
        pio.write_html(fig, file=html_path, auto_open=False)

        # Mostrar confirmación en la terminal
        print(f"✅ Archivo HTML guardado correctamente en: {html_path}")

    except Exception as e:
        print(f"❌ Error al guardar el archivo HTML: {e}")

# Llamar a la función para guardar el archivo HTML antes de iniciar el servidor Dash
save_html_static()

# Paso 4: Iniciar la aplicación Dash
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)  # Ejecuta el servidor Dash