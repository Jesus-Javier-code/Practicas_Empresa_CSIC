#Medir areas de una celda en funcion del display del mapa

import numpy as np
import matplotlib as plt
import pandas as pd
import plotly.express as px


# Creating a function to show a grid in function of the zoomlevel
def grid(figure, lat_min, lat_max, lon_min, lon_max, zoom_lvl):
    # The number of cells can be changed here by changing the number
    n_rows = max(zoom_lvl , 5)
    n_columns = max(zoom_lvl , 5)

    # Distance between cells
    lat_step = (lat_max - lat_min) / n_rows
    lon_step = (lon_max - lon_min) / n_columns
    
    for i in range(n_rows):
        for j in range(n_columns):
            lat1 = lat_min + i * lat_step
            lat2 = lat_min + (i + 1) * lat_step
            lon1 = lon_min + j * lon_step
            lon2 = lon_min + (j + 1) * lon_step

            figure.add_shape(
                type="rect",
                x0 = lon1, x1 = lon2,
                y0 = lat1, y1 = lat2,
                line=dict(color="black", width=2), 
                fillcolor="rgba(0, 0, 0, 1)"
            )
    figure.show()

def geo_map(lati, long, zoom_lvl):

    # AQUÍ SE PODRÍA PREGUNTAR TAMBIÉN CON BOTONES QUE DATOS SON LOS QUE QUIERE PONER EL USUARIO
    lat_min = lati - 0.05
    lat_max = lati + 0.05
    lon_min = long - 0.05
    lon_max = long + 0.05

    data = [
        [lati, long] # Desired point (Just to show in the map the introduced coordinates)
    ]
    # Data is turned into a pandas dataframe
    df = pd.DataFrame(data, columns=["lat", "lon"]) 

    # Creating the map
    fig = px.scatter_map(df, lat="lat", lon="lon", center={"lat": lati, "lon": long}, zoom = zoom_lvl) 

    # Configurar el mapa base (puedes usar varios estilos como 'stamen-terrain', 'carto-positron', 'open-street-map', etc.)
    fig.update_layout(map_style="open-street-map")

    grid(fig, lat_min, lat_max, lon_min, lon_max, zoom_lvl)
    fig.show()


geo_map(28.614099067906647, -17.86711684652606, 11)