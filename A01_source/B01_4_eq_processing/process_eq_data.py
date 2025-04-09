# process_eq_data.py
import pandas as pd
import plotly.express as px
from great_tables import GT, md
import os
import sys
import dash
from dash import dash_table, html

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
        eq_data = pd.read_csv(input_csv)
        print(f"✅ Data loaded successfully ({len(eq_data)} records)")
        
        # Generate outputs
        generate_table(eq_data, output_folder)
        generate_map(eq_data, output_folder)
        generate_histogram(eq_data, output_folder)
        
        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}", file=sys.stderr)
        return 1

def generate_table(data, output_folder):
    try:
        from dash import dash_table, html
        import dash
        import os

        # Crear la tabla interactiva con Dash DataTable
        table_html_path = os.path.join(output_folder, "eq_table.html")
        app = dash.Dash(__name__)

        # Configurar la tabla interactiva
        table = dash_table.DataTable(
            id="eq-table",
            columns=[
                {"name": col, "id": col, "type": "numeric" if pd.api.types.is_numeric_dtype(data[col]) else "text"}
                for col in data.columns
            ],
            data=data.head(100).to_dict("records"),  # Mostrar solo las primeras 100 filas
            page_size=10,  # Número de filas por página
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center", "padding": "5px"},
            style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
            filter_action="native",  # Permitir filtrado
            sort_action="native",    # Permitir ordenamiento
            row_selectable="multi",  # Permitir selección de filas
        )

        # Configurar el layout de la aplicación Dash
        app.layout = html.Div(
            [
                html.H1("Earthquake Trigger Index Table", style={"textAlign": "center"}),
                html.Div(table, style={"margin": "20px"}),
            ]
        )

        # Guardar la tabla como un archivo HTML
        with open(table_html_path, "w", encoding="utf-8") as f:
            f.write(app.index_string)
        print(f"✅ Table saved to: {table_html_path}")
        print(data.head(100).to_string(index=False))  # Print the first 100 rows of the table to console


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
        print(f"✅ Map saved to: {map_html_path}")
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
        print(f"✅ Histogram saved to: {hist_html_path}")
    except Exception as e:
        print(f"❌ Error generating histogram: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    sys.exit(main())