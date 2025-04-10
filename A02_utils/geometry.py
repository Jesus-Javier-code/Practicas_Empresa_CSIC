# process_eq_data.py
import pandas as pd
import plotly.express as px
import os
import sys

def main():
    try:
        # Configurar rutas - VERSIÓN DEFINITIVA CORREGIDA
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # El script está en A02_utils, necesitamos llegar a Practicas_Empresa_CSIC
        project_root = os.path.dirname(current_dir)  # Esto nos lleva a Practicas_Empresa_CSIC
        
        input_csv = os.path.join(project_root, "A00_data", "B_eq_processed", "wrk_df.csv")
        output_folder = os.path.join(project_root, "A04_web", "B_images")
        
        # Verificación EXTENDIDA
        if not os.path.exists(input_csv):
            print(f"❌ Error: Archivo no encontrado en {input_csv}", file=sys.stderr)
            print("Por favor verifica:")
            print(f"1. La estructura exacta debe ser: {project_root}/A00_data/B_eq_processed/wrk_df.csv")
            print(f"2. Que los nombres de carpetas coincidan exactamente (mayúsculas/minúsculas)")
            print(f"3. Que el archivo existe en esa ubicación")
            return 1
        
        # Resto del código...
        os.makedirs(output_folder, exist_ok=True)
        eq_data = pd.read_csv(input_csv)
        
        generate_table(eq_data, output_folder)
        generate_map(eq_data, output_folder)
        generate_histogram(eq_data, output_folder)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}", file=sys.stderr)
        return 1

# ... (resto de funciones igual)
def generate_table(data, output_folder):
    try:
        table_html_path = os.path.join(output_folder, "eq_table.html")

        # Convertir el DataFrame a HTML (solo las primeras 100 filas)
        html_table = data.head(100).to_html(
            index=False,
            border=0,
            classes="table table-striped",
            justify="center"
        )

        # Envolver en HTML básico
        full_html = f"""
        <html>
        <head>
            <title>Earthquake Trigger Index Table</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 20px;
                }}
                .table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .table th, .table td {{
                    border: 1px solid #ccc;
                    padding: 8px;
                    text-align: center;
                }}
                .table th {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <h1 style="text-align:center;">Earthquake Trigger Index Table</h1>
            {html_table}
        </body>
        </html>
        """

        with open(table_html_path, "w", encoding="utf-8") as f:
            f.write(full_html)

<<<<<<< HEAD
    except Exception as e:
        print(f"❌ Error generating table: {str(e)}", file=sys.stderr)
        raise

def generate_map(data, output_folder):
    try:
        map_html_path = os.path.join(output_folder, "eq_map.html")
        fig = px.scatter_geo(
            data,
            lat='latitude',
            lon='longitude',
            size=data['magnitude']*2,
            color='trigger_index',
            color_continuous_scale='Viridis',
            hover_name='id',
            projection='natural earth'
        )
        fig.write_html(map_html_path, full_html=False)
    except Exception as e:
        print(f"❌ Error generating map: {str(e)}", file=sys.stderr)
        raise

def generate_histogram(data, output_folder):
    try:
        hist_html_path = os.path.join(output_folder, "eq_histogram.html")
        fig = px.histogram(
            data,
            x='trigger_index',
            nbins=30,
            title='Trigger Index Distribution'
        )
        fig.write_html(hist_html_path, full_html=False)
    except Exception as e:
        print(f"❌ Error generating histogram: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    sys.exit(main())
=======
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

    fig.add_trace(go.Scattermapbox(
        mode="lines",
        lon=[lon_min, lon_max, lon_max, lon_min, lon_min],
        lat=[lat_min, lat_min, lat_max, lat_max, lat_min],
        marker=dict(size=10, color="black"),
        line=dict(width=2, color="black"),
        name="Área de estudio"
    ))

    grid(fig, lat_min, lat_max, lon_min, lon_max)
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../A04_web/B_images")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)
    
    pio.write_html(fig, output_path, full_html=True, config={'scrollZoom': True})
    print(f"Mapa guardado en: {output_path}")

# Coordenadas del volcán de Tajogaite
pos1_la_palma = np.array([28.601109109131052, -17.929768956228138])
pos2_la_palma = np.array([28.62514776637218, -17.872144640744164])

pos3_la_palma = np.array([28.3, -18.2])
pos4_la_palma = np.array([28.8, -17.9])

geo_map(pos1_la_palma, pos2_la_palma, "Volcán de Tajogaite", "mapa_tajogaite.html")
geo_map(pos3_la_palma, pos4_la_palma, "Región alrededor", "mapa_region_alrededor.html")

def plot_events_histogram(file = "bsc_events_info.csv"):
    path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(path, ".."))

    file_path = os.path.join(project_root, f"A00_data/B_eq_raw/{file}")

    df = pd.read_csv(file_path)

    df["time"] = pd.to_datetime(df["time"], errors='coerce')

    fig = go.Figure(data=[
        go.Histogram(
            x=df["time"],
            nbinsx=30,  
            marker_color="blue"
        )
    ])

    fig.update_layout(
        title="Histograma de Eventos Sísmicos",
        xaxis_title="Fecha y Hora",
        yaxis_title="Número de Eventos",
        xaxis_tickformat="%Y-%m",  
        xaxis_rangeslider_visible=True,  
        barmode="overlay"
    )
    total_events = len(df)  # Contar el número total de eventos

    fig.update_layout(
        title=f"Histograma de Eventos Sísmicos (Total: {total_events})",  # Agregar el total al título
        xaxis_title="Fecha",
        yaxis_title="Número de Eventos",
        xaxis_tickformat="%Y-%m",  # Formato de solo fecha en el eje x
        xaxis_rangeslider_visible=True,  # Mostrar el rango deslizante
        barmode="overlay"
    )


    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../A04_web/B_images")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "histograma_eventos.html")

    pio.write_html(fig, output_path, full_html=True, config={'scrollZoom': True})
    print(f"Histograma guardado en: {output_path}")

plot_events_histogram("bsc_events_info.csv")
>>>>>>> 32aad805db90742d4e8d5b1440f8420175a06eae
