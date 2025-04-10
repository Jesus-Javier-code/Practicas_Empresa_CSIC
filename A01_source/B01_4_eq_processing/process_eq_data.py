# process_eq_data.py
import pandas as pd
import plotly.express as px
import os
import sys
import dash
from dash import dash_table, html
import plotly.graph_objects as go
import plotly.io as pio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from A01_source.B01_4_eq_processing import preprocess as pre
from A01_source.B01_2_eq_download import utils as utils
from A01_source.B01_2_eq_download import download as dwl

def main():
    try:
        # Update data to the new parameters
        print("🔄 Loading data...")
        #pre.trigger_index(L_method="Singh")     

        # Configure paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(current_dir))
        
        files = ["wrk_df.csv", "trigger_index_filtered.csv"]

        input_csv = os.path.join(base_dir, "A00_data", "B_eq_processed", f"{files[0]}")
        input_csv_filtered = os.path.join(base_dir, "A00_data", "B_eq_processed", f"{files[1]}")
        output_folder = os.path.join(base_dir, "A04_web", "B_images")

        # Verify input file exists
        if not os.path.exists(input_csv):
            print(f"❌ Error: File not found at {input_csv}", file=sys.stderr)
            return 1
        
        # Create output folder
        os.makedirs(output_folder, exist_ok=True)

        eq_data = pd.read_csv(input_csv)
        print(f"✅ Data loaded successfully ({len(eq_data)} records)")

        eq_filtered_data = pd.read_csv(input_csv_filtered)
        print(f"✅ Filtered data loaded successfully ({len(eq_filtered_data)} records)")
        
        # Generate outputs
        print("🔄 Generating table...")
        generate_table(eq_data, output_folder)
        print("✅ Table generated successfully")
        
        print("🔄 Generating maps...")
        generate_map(eq_data, output_folder, is_filtered=False)
        generate_map(eq_filtered_data, output_folder, is_filtered=True)
        print("✅ Maps generated successfully")
        
        print("🔄 Generating histogram...")
        generate_histogram(eq_data, output_folder)
        print("✅ Histogram generated successfully")
        
        print("🔄 Plotting events histogram...")
        plot_events_histogram(file="wrk_df.csv")
        print("✅ Events histogram plotted successfully")

        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}", file=sys.stderr)
        return 1

def generate_table(data, output_folder):
    try:
        table_html_path = os.path.join(output_folder, "eq_table.html")

        # Convertir el DataFrame a HTML (solo las primeras 100 filas)
        html_table = data.to_html(
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

        print(f"✅ Table saved to: {table_html_path}")
        print(data.head(5).to_string(index=False))

    except Exception as e:
        print(f"❌ Error generating table: {str(e)}", file=sys.stderr)
        raise

def generate_map(data, output_folder, is_filtered=False):
    try:
        # Determinar el nombre del archivo y el título del mapa según el DataFrame
        if is_filtered:
            map_html_path = os.path.join(output_folder, "eq_map_filtered.html")
            map_title = "Filtered Earthquake Trigger Index Map"
            os.makedirs(output_folder, exist_ok=True)
        else:
            map_html_path = os.path.join(output_folder, "eq_map.html")
            map_title = "Earthquake Trigger Index Map"

        # Crear el mapa principal con los datos sísmicos
        fig = px.scatter_geo(
            data,
            lat="latitude",
            lon="longitude",
            size=data["magnitude"]*2,
            color="trigger_index",
            color_continuous_scale="Viridis",
            hover_name="id",
            title=map_title
        )

        # Coordenadas del volcán (centro de referencia)
        lat_cent, lon_cent = dwl.ref[2]
        reg = dwl.ref[3] + 50
        lat_min, lat_max, lon_min, lon_max = utils.limit_region_coords(lat_cent, lon_cent, reg)

        # Agregar un marcador para el volcán
        fig.add_trace(
            go.Scattergeo(
                lat=[lat_cent],
                lon=[lon_cent],
                mode="markers+text",
                marker=dict(
               symbol="triangle-up",
               size=15,
              color="red"
            ),
            text=["Volcán"],
            textposition="top right",  # Ajustar la posición de la etiqueta
            textfont=dict(
                size=10,  # Reducir el tamaño de la fuente
                color="black"
            ),
            hovertext=["Volcán (Información adicional)"],  # Información al pasar el cursor
            hoverinfo="text"
        )
    )

        fig.add_trace(
            go.Scattergeo(
                lat=[lat_min, lat_min, lat_max, lat_max, lat_min],
                lon=[lon_min, lon_max, lon_max, lon_min, lon_min],
                mode="lines",
                line=dict(color="red", width=2),
                name="Search Area",
                showlegend=False
            )
        )

        # Configurar los límites y la proyección del mapa
        fig.update_geos(
            projection_type="mercator",
            center={"lat": lat_cent, "lon": lon_cent},
            fitbounds="locations",
            lataxis={"range": [lat_min, lat_max]},
            lonaxis={"range": [lon_min, lon_max]},
            visible=True,
            showland=True,
            landcolor="lightgray",
            showocean=True,
            oceancolor="lightblue",
            showcountries=True,
            countrycolor="black",
            showcoastlines=True,
            coastlinecolor="black",
            coastlinewidth=1,
            showrivers=True,
            rivercolor="blue",
            showlakes=True,
            lakecolor="blue",
            riverwidth=1,
            resolution=50
        )

        fig.update_geos(lataxis_showgrid=True, lonaxis_showgrid=True)

        # Configurar el diseño del mapa
        fig.update_layout(
            title_font=dict(size=20),
            margin={"r": 0, "t": 50, "l": 0, "b": 0}
        )
        
        os.makedirs(output_folder, exist_ok=True)  # Asegurarse de que la carpeta exista
        fig.write_html(map_html_path, full_html=True)
        print(f"✅ Map saved to: {map_html_path}")

        if os.path.exists(map_html_path):
            with open(map_html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

        # Agregar estilo CSS para bordes redondeados
            rounded_style = """
            <style>
                .main-svg-container {
                    border-radius: 15px; /* Bordes redondeados */
                    overflow: hidden; /* Ocultar contenido fuera de los bordes */
                    border: 2px solid black; /* Opcional: agregar un borde */
                }
            </style>
            """
            html_content = html_content.replace("<head>", f"<head>{rounded_style}")

        # Guardar el archivo HTML modificado
            with open(map_html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            print(f"✅ Map saved to: {map_html_path}")
        else:
            print(f"❌ Error: Map HTML file not found at {map_html_path}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error generating map: {str(e)}", file=sys.stderr)
        raise

def generate_histogram(data, output_folder):
    try:
        hist_html_path = os.path.join(output_folder, "eq_trigger_histogram.html")

        fig = px.histogram(
            data,
            x="trigger_index",
            nbins=60,
            title="Trigger Index Histogram",
            marginal="rug"
        )

        # Configurar el diseño del histograma
        fig.update_layout(
            title_font=dict(size=20),
            xaxis_title="Trigger Index",
            yaxis_title="Frequency",
            bargap= 10,
            coloraxis_colorbar=dict(
                title="Trigger Index",  # Título de la barra de colores
                tickvals=[data["trigger_index"].min(), data["trigger_index"].max()],
                ticktext=["Low", "High"]),
            xaxis = dict(
                showgrid=True,
                gridcolor="lightgray",
                gridwidth=0.5,
            ),
            yaxis = dict(
                showgrid=True,
                gridcolor="lightgray",
                gridwidth=0.5,
            )
        )



        # Guardar el histograma como un archivo HTML
        fig.write_html(hist_html_path, full_html=True)
        print(f"✅ Histogram saved to: {hist_html_path}")
    except Exception as e:
        print(f"❌ Error generating histogram: {str(e)}", file=sys.stderr)
        raise

""""

def plot_events_histogram(file="wrk_df.csv"):
    path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(path, "..", ".."))

    file_path = os.path.join(project_root, f"A00_data/B_eq_processed/{file}")

    df = pd.read_csv(file_path)

    # Convertir la columna 'time' a tipo datetime
    df["time"] = pd.to_datetime(df["time"], errors='coerce')

    # Eliminar filas con valores NaT en la columna 'time'
    df = df.dropna(subset=["time"])

    # Calcular el total de eventos
    total_events = len(df)

    # Crear el histograma
    fig = go.Figure(data=[
        go.Histogram(
            x=df["time"],
            nbinsx=30,  # Número de bins en el eje x
            marker_color="blue"
        )
    ])

    # Configurar el diseño del gráfico
    fig.update_layout(
        title=f"Seismic events histogram (Total: {total_events})",  # Agregar el total al título
        xaxis_title="Date",
        yaxis_title="Number of events",
        xaxis_tickformat="%Y-%m",  # Formato de solo fecha en el eje x
        xaxis_rangeslider_visible=True,  # Mostrar el rango deslizante
        barmode="overlay"
    )

    # Agregar una anotación con el total de eventos
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.5, y=1.1,  # Posición relativa en el gráfico
        text=f"Total de eventos: {total_events}",
        showarrow=False,
        font=dict(size=14, color="black")
    )

    # Guardar el gráfico
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../A04_web/B_images")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "eq_histogram.html")

    pio.write_html(fig, output_path, full_html=True, config={'scrollZoom': True})
    print(f"Histograma guardado en: {output_path}")
"""

def plot_events_histogram(file="wrk_df.csv"):
    path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(path, "..", ".."))

    file_path = os.path.join(project_root, f"A00_data/B_eq_processed/{file}")

    df = pd.read_csv(file_path)

    # Convertir la columna 'time' a tipo datetime
    df["time"] = pd.to_datetime(df["time"], errors='coerce')

    # Eliminar filas con valores NaT en la columna 'time'
    df = df.dropna(subset=["time"])

    # Calcular el total de eventos
    total_events = len(df)

    # Crear el histograma con colores alternados
    fig = go.Figure()

    # Configurar el diseño del gráfico
    fig.update_layout(
        title=f"Seismic events histogram (Total: {total_events})",  # Agregar el total al título
        xaxis_title="Date",
        yaxis_title="Number of events",
        xaxis_tickformat="%Y-%m",  # Formato de solo fecha en el eje x
        xaxis_rangeslider_visible=True,  # Mostrar el rango deslizante
        barmode="overlay",
        plot_bgcolor="white",  # Fondo blanco
    )

    # Agregar una anotación con el total de eventos
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.5, y=1.1,  # Posición relativa en el gráfico
        text=f"Total de eventos: {total_events}",
        showarrow=False,
        font=dict(size=14, color="black")
    )

    # Guardar el gráfico
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../A04_web/B_images")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "eq_histogram.html")

    pio.write_html(fig, output_path, full_html=True, config={'scrollZoom': True})
    print(f"✅ Histograma guardado en: {output_path}")

if __name__ == "__main__":
    sys.exit(main())