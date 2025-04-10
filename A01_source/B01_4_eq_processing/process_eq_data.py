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
        # Configure paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(current_dir))
        
        input_csv = os.path.join(base_dir, "A00_data", "B_eq_processed", "wrk_df.csv")
        output_folder = os.path.join(base_dir, "A04_web", "B_images")

        # Verify input file exists
        if not os.path.exists(input_csv):
            print(f"❌ Error: File not found at {input_csv}", file=sys.stderr)
            return 1
        
        # Create output folder
        os.makedirs(output_folder, exist_ok=True)
        
        # Load data
        pre.trigger_index(L_method="Singh")

        eq_data = pd.read_csv(input_csv)
        print(f"✅ Data loaded successfully ({len(eq_data)} records)")

        
         # Load data
        print("🔄 Loading data...")
        eq_data = pd.read_csv(input_csv)
        print(f"✅ Data loaded successfully ({len(eq_data)} records)")
        
        # Generate outputs
        print("🔄 Generating table...")
        generate_table(eq_data, output_folder)
        print("✅ Table generated successfully")
        
        print("🔄 Generating map...")
        generate_map(eq_data, output_folder)
        print("✅ Map generated successfully")
        
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

        print(f"✅ Table saved to: {table_html_path}")
        print(data.head(5).to_string(index=False))

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
            title = "Earthquake Trigger Index Map"
            #projection='natural earth'
        )

        center_coords = dwl.ref[2]
        reg = dwl.ref[3]
        lat_min , lat_max, lon_min , lon_max = utils.limit_region_coords(center_coords, reg+50)

        fig.update_geos(
            projection_type="mercator",  # Proyección más adecuada para mapas detallados
            center={"lat": center_coords[0], "lon": center_coords[1]},  # Centrar en las Islas Canarias
            fitbounds="locations",  # Ajustar los límites al rango de datos
            lataxis={"range": [lat_min, lat_max]},  # Rango de latitud
            lonaxis={"range": [lon_min, lon_max]},  # Rango de longitud
            visible=True,  # Hacer visibles los ejes
        )

        fig.update_layout(
            title_font=dict(size=20),
            legend_title_text="Trigger Index",
            margin={"r": 0, "t": 50, "l": 0, "b": 0},  # Reducir márgenes
        )
        
        fig.write_html(map_html_path, full_html=False)
        print(f"✅ Map saved to: {map_html_path}")
    except Exception as e:
        print(f"❌ Error generating map: {str(e)}", file=sys.stderr)
        raise

def generate_histogram(data, output_folder):
    try:
        hist_html_path = os.path.join(output_folder, "eq_trigger_histogram.html")
        fig = px.histogram(
            data,
            x='trigger_index',
            nbins=30,
            title='Trigger Index Distribution'
        )
        fig.write_html(hist_html_path, full_html=False)
        print(f"✅ Histogram saved to: {hist_html_path}")
    except Exception as e:
        print(f"❌ Error generating histogram: {str(e)}", file=sys.stderr)
        raise

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

if __name__ == "__main__":
    sys.exit(main())
