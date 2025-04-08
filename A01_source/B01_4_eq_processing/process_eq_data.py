import pandas as pd
import plotly.express as px
from plotnine import ggplot, aes, geom_histogram, labs, theme_minimal, ggsave
from great_tables import GT
from IPython.display import display
import os

# Paths
input_csv = "A00_data/B_eq_processed/trigger_index.csv"
output_folder = "A00_data/B_images"
table_html_path = os.path.join(output_folder, "eq_table.html")
map_html_path = os.path.join(output_folder, "eq_map.html")
histogram_path = os.path.join(output_folder, "trigger_index_histogram.png")

# Crear carpeta si no existe
os.makedirs(output_folder, exist_ok=True)

# Leer CSV
try:
    eq_data = pd.read_csv(input_csv)
except Exception as e:
    print(f"Error al leer el CSV: {e}")
    exit()

# Tabla (como HTML con great_tables)
try:
    eq_table = (
        GT(eq_data.copy())
        .fmt_number(columns=["latitude", "longitude", "distance"], decimals=4)
        .fmt_number(columns=["trigger_index"], decimals=2)
        .tab_header(title="Índice de Trigger de Terremotos")
        .tab_options(container_width="100%", table_width="auto")
        .tab_style(style="background-color: #FBEBE8;", locations="table")
    )

    eq_table.save_html(table_html_path)
    print(f"Tabla guardada en: {table_html_path}")
except Exception as e:
    print(f"Error generando tabla: {e}")

# Mapa interactivo con Plotly
try:
    fig = px.scatter_geo(eq_data,
                        lat='latitude',
                        lon='longitude',
                        size='magnitude',
                        color='trigger_index',
                        hover_name='id',
                        hover_data=['distance', 'magtype'],
                        projection='natural earth',
                        title='Distribución de Terremotos')
    
    fig.update_layout(geo=dict(showcountries=True))
    fig.write_html(map_html_path)
    print(f"Mapa guardado en: {map_html_path}")
except Exception as e:
    print(f"Error generando mapa: {e}")

# Histograma con plotnine
try:
    p = (
        ggplot(eq_data, aes(x='trigger_index')) 
        + geom_histogram(binwidth=0.1, fill="#413224", color="white")
        + labs(title="Distribución del Índice de Trigger", x="Índice de Trigger", y="Conteo")
        + theme_minimal()
    )

    ggsave(plot=p, filename=histogram_path, dpi=150)
    print(f"Histograma guardado en: {histogram_path}")
except Exception as e:
    print(f"Error generando histograma: {e}")
