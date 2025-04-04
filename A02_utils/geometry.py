import numpy as np
import plotly.io as pio
import pandas as pd
import plotly.graph_objects as go
import os

def grid(fig, lat_min, lat_max, lon_min, lon_max):
    n_rows = 10
    n_columns = 10
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
    
    fig = go.Figure()

    # Configuración del mapa sin márgenes y fondo transparente
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(
            center=dict(lat=lati, lon=long),
            zoom=12,
            bounds=dict(west=lon_min, east=lon_max, north=lat_max, south=lat_min)
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        autosize=True,
        dragmode=False
    )

    # Mostrar la delimitación del área
    fig.add_trace(go.Scattermapbox(
        mode="lines",
        lon=[lon_min, lon_max, lon_max, lon_min, lon_min],
        lat=[lat_min, lat_min, lat_max, lat_max, lat_min],
        marker=dict(size=10, color="black"),
        line=dict(width=2, color="black"),
        name="Área de estudio"
    ))

    grid(fig, lat_min, lat_max, lon_min, lon_max)
    
    # Guardar el mapa
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../A04_web/B_images")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)
    
    pio.write_html(fig, output_path, full_html=True, config={'scrollZoom': True})
    print(f"Mapa guardado en: {output_path}")

# Coordenadas del volcán de Tajogaite
pos1_la_palma = np.array([28.601109109131052, -17.929768956228138])
pos2_la_palma = np.array([28.62514776637218, -17.872144640744164])

# Región alrededor
pos3_la_palma = np.array([28.3, -18.2])
pos4_la_palma = np.array([28.8, -17.9])

# Generar los mapas
geo_map(pos1_la_palma, pos2_la_palma, "Volcán de Tajogaite", "mapa_tajogaite.html")
geo_map(pos3_la_palma, pos4_la_palma, "Región alrededor", "mapa_region_alrededor.html")