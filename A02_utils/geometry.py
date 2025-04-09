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
