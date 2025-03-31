import numpy as np
import plotly.io as pio
import pandas as pd
import plotly.graph_objects as go
import os
import numpy as np
import plotly.io as pio

# Crear una función para mostrar una cuadrícula según el nivel de zoom
def grid(fig, lat_min, lat_max, lon_min, lon_max):
    # El número de celdas puede cambiarse aquí modificando el número
    n_rows = 10
    n_columns = 10
    # Distancia entre celdas
    lat_step = (lat_max - lat_min) / n_rows
    lon_step = (lon_max - lon_min) / n_columns
    
    for i in range(n_rows):
        for j in range(n_columns):
            lat1 = lat_min + i * lat_step
            lat2 = lat_min + (i + 1) * lat_step
            lon1 = lon_min + j * lon_step
            lon2 = lon_min + (j + 1) * lon_step

            fig.add_shape(
                type="rect",
                x0=lon1, x1=lon2,
                y0=lat1, y1=lat2,
                line=dict(color="black", width=2), 
                fillcolor="rgba(0, 0, 0, 1)"
            )

# pos1 y pos2 son las posiciones del área que quieres mostrar
def geo_map(pos1, pos2, zone, output_file):
    lat_min = min(pos1[0], pos2[0])
    lat_max = max(pos1[0], pos2[0])
    lon_min = min(pos1[1], pos2[1])
    lon_max = max(pos1[1], pos2[1])

    lati = (lat_max + lat_min) / 2
    long = (lon_max + lon_min) / 2

    df = pd.DataFrame({
        "lat": [lati],
        "lon": [long],
        "description": [zone]
    })
    
    # Crear el mapa
    fig = go.Figure()

    # Configurar el mapa base (puedes usar varios estilos como 'stamen-terrain', 'carto-positron', 'open-street-map', etc.)
    fig.update_layout(
        map_style="open-street-map", 
        map_bounds={"west": lon_min, "east": lon_max, "north": lat_max, "south": lat_min},
        dragmode=False
    )

    # Mostrar la delimitación del área
    fig.add_trace(go.Scattermap(
        mode="lines",
        lon=[lon_min, lon_max, lon_max, lon_min, lon_min],
        lat=[lat_min, lat_min, lat_max, lat_max, lat_min],
        marker={"size": 10, "color": "black"},
        line={"width": 2, "color": "black"},
        name="Desired region"
    ))

    grid(fig, lat_min, lat_max, lon_min, lon_max)
    
    # Crear la ruta completa para el archivo HTML en la carpeta 'images' dentro de '04_web'
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../04_web/images")
    os.makedirs(output_dir, exist_ok=True)  # Crear la carpeta 'images' si no existe
    output_path = os.path.join(output_dir, output_file)
    
    # Guardar la gráfica interactiva en el archivo HTML
    pio.write_html(fig, output_path, full_html=True)
    print(f"Mapa guardado en: {output_path}")

# Coordenadas del volcán de Tajogaite: 28.61357798637031, -17.865478560801982
pos1_la_palma = np.array([28.601109109131052, -17.929768956228138])
pos2_la_palma = np.array([28.62514776637218, -17.872144640744164])

# Región alrededor:
pos3_la_palma = np.array([28.3, -18.2])
pos4_la_palma = np.array([28.8, -17.9])

# Llamar a geo_map para ambos mapas
geo_map(pos1_la_palma, pos2_la_palma, "Volcan de Tajogaite", "mapa_tajogaite.html")
geo_map(pos3_la_palma, pos4_la_palma, "Región alrededor", "mapa_region_alrededor.html")

