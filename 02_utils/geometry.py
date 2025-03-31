import numpy as np
import matplotlib as plt
import plotly.io as pio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Creating a function to show a grid in function of the zoomlevel
def grid(fig, lat_min, lat_max, lon_min, lon_max):
    # The number of cells can be changed here by changing the number
    n_rows = 10
    n_columns = 10
    # Distance between cells
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
                x0 = lon1, x1 = lon2,
                y0 = lat1, y1 = lat2,
                line=dict(color="black", width=2), 
                fillcolor="rgba(0, 0, 0, 1)"
            )

# pos1 and pos2 are the positions of the area you would like to see
def geo_map(pos1, pos2, zone):

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
    
    # Creating the map
    fig = go.Figure()

    # Configurar el mapa base (puedes usar varios estilos como 'stamen-terrain', 'carto-positron', 'open-street-map', etc.)
    fig.update_layout(
        map_style="carto-positron", 
        map_bounds={"west":lon_min, "east":lon_max, "north":lat_max, "south":lat_min},
        dragmode=False
        )

    # To show the area delimitation
    fig.add_trace(go.Scattermap(
    mode="lines",
        lon=[lon_min, lon_max, lon_max, lon_min, lon_min],
        lat=[lat_min, lat_min, lat_max, lat_max, lat_min],
        marker={"size": 10, "color": "black"},
        line={"width": 2, "color": "black"},
        name="Desired region"
    ))

    grid(fig, lat_min, lat_max, lon_min, lon_max)
    pio.write_html(fig, "04_web/mapa_tajogaite.html", full_html=False)

# Coordenadas del volcán de Tajogaite: 28.61357798637031, -17.865478560801982
pos1_la_palma = np.array([28.601109109131052, -17.929768956228138])
pos2_la_palma =  np.array([28.62514776637218, -17.872144640744164])

# Región alrededor:
pos3_la_palma = np.array([28.3, -18.2])
pos4_la_palma =  np.array([28.8, -17.9])

geo_map(pos1_la_palma, pos2_la_palma, "Volcan de Tajogaite")
geo_map(pos3_la_palma, pos4_la_palma, "Volcan de Tajogaite")



