from libcomcat.search import search
from libcomcat.dataframes import get_summary_data_frame, get_detail_data_frame
from datetime import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm
import os
import plotly.express as px
import dash
from dash import dash_table, html
import plotly.graph_objects as go
import plotly.io as pio
import sys

"""
Due to incompatibilites with the pyodide library used in the quarto script,
in order to keep a useful, friendly and interactive dashboard, the functions used
in other folders must be imported here
"""

#-------------------------------------------------------------------
#ref.py
#--------------------------------------------------------------------

ref = ("2000-01-01 00:00", "2025-03-30 00:00", (28.61302051993363, -17.866746656292413), 750)

#-------------------------------------------------------------------
# Download.py
#-------------------------------------------------------------------

# This function downloads all events in a given region, the data is stored in eq_raw folder
def download_all_by_region(date_i, date_f, center_coords, reg_rad):

    # Center coordinates must be given as (latitude, longitude) form
    lat_cent, lon_cent = center_coords
    lat_min, lat_max, lon_min, lon_max = limit_region_coords(lat_cent, lon_cent, reg_rad)

    date_i = datetime.strptime(date_format(date_i), "%Y,%m,%d,%H,%M")
    date_f = datetime.strptime(date_format(date_f), "%Y,%m,%d,%H,%M")

    events = search(
        starttime = date_i,
        endtime = date_f,
        minlatitude = lat_min,
        maxlatitude = lat_max,
        minlongitude = lon_min,
        maxlongitude = lon_max,
        minmagnitude = 1,
        eventtype = "earthquake"
    )

    summary_events_df = get_summary_data_frame(events)
    saving_data(summary_events_df, "all_bsc_events_info.csv", folder = "B_eq_raw")
    
    detail_events_df = get_detail_data_frame(events, get_all_magnitudes = True)
    saving_data(detail_events_df, "all_dtl_mag_events_info.csv", folder = "B_eq_raw")

    merged_df = working_df(summary_events_df, detail_events_df, "all_events_wrk_df.csv")

    return merged_df, center_coords

def working_df(df1, df2, file_name = "wrk_df.csv"):
    
    variables = ["id", "time", "magnitude", "magtype", "latitude", "longitude", "depth"]

    for col in tqdm(df1.columns, desc ="Procesando columnas de df1"):
        if col not in variables:
            df1.drop(columns = col, inplace = True)
        else:
            None

    for col in tqdm(df2.columns, desc="Procesando columnas de df2"):
        if col not in variables:
            df2.drop(columns = col, inplace = True)
        else:
            None
    
    merged_df = pd.merge(df1, df2, on= "id", how= "inner")

    for col in  tqdm(variables, desc ="Procesando columnas fusionadas"):
        if col != "id" and f"{col}_y" in merged_df.columns:
            merged_df[col] = merged_df[f"{col}_y"]
            merged_df.drop(columns=[f"{col}_x", f"{col}_y"], inplace=True)

    saving_data(merged_df, f"{file_name}", folder = "B_eq_processed")

    return merged_df

def download_optimized(date_i, date_f, center_coords, reg_rad):
    min_mag, distance_list = simulate_min_mag_by_radius(reg_rad, max_trigger_index = 100.0, L_method = "Singh")
    
    # Search area coordinates
    lat_cent, lon_cent = center_coords
    lat_min, lat_max, lon_min, lon_max = limit_region_coords(lat_cent, lon_cent, reg_rad)

    date_i = datetime.strptime(date_format(date_i), "%Y,%m,%d,%H,%M")
    date_f = datetime.strptime(date_format(date_f), "%Y,%m,%d,%H,%M")

    cumulative_summary_df = pd.DataFrame()
    cumulative_detail_df = pd.DataFrame()

    # Smaller search area
    for i in tqdm(range(len(distance_list)), desc=f"Procesando para cada radio"):
        lat_min_list, lat_max_list, lon_min_list, lon_max_list = limit_region_coords(lat_cent, lon_cent, distance_list[i])

        events = search(
            starttime = date_i,
            endtime = date_f,
            minlatitude = lat_min_list,
            maxlatitude = lat_max_list,
            minlongitude = lon_min_list,
            maxlongitude = lon_max_list,
            minmagnitude = min_mag[i],
            eventtype = "earthquake",
            orderby = "time"
        )

        if not events:
            print(f"No se encontraron eventos con magnitud {min_mag[i]} para la distancia {round(distance_list[i], 2)} km.")
            continue

    # Procesar los eventos
        try:
            summary_events_df = get_summary_data_frame(events)
            detail_events_df = get_detail_data_frame(events, get_all_magnitudes=True)

        # Verificar columnas esperadas
            required_columns = ['id', 'time', 'latitude', 'longitude', 'depth', 'magnitude']
            if not set(required_columns).issubset(detail_events_df.columns):
                print(f"Columnas faltantes en el DataFrame: {set(required_columns) - set(detail_events_df.columns)}")
                continue

        # Concatenar los datos
            cumulative_summary_df = pd.concat([cumulative_summary_df, summary_events_df]).drop_duplicates(subset="id")
            cumulative_detail_df = pd.concat([cumulative_detail_df, detail_events_df]).drop_duplicates(subset="id")

        except KeyError as e:
            print(f"Error procesando los eventos: {e}")
            continue

    saving_data(cumulative_summary_df, "bsc_events_info.csv", folder = "B_eq_raw")
    saving_data(cumulative_detail_df, "dtl_mag_events_info.csv", folder = "B_eq_raw")

    return working_df(cumulative_summary_df, cumulative_detail_df), center_coords

#----------------------------------------------------------------------
# Utils.py
#----------------------------------------------------------------------

# Constants
R_earth = 6378.1 # km | Equatorial radius (source: NASA's Earth Fact Sheet)

def saving_data(df, filename, folder="B_eq_raw"):

    script_dir = os.path.dirname(os.path.abspath(__file__))  # Script path
    project_root = os.path.abspath(os.path.join(script_dir, "../"))  # Project root path
    eq_dir = os.path.join(project_root, f"A00_data/{folder}") # Eq. data folder

    if not os.path.exists(eq_dir):
        os.makedirs(eq_dir)

    filepath = os.path.join(eq_dir, filename) # File path to save the data
    df.to_csv(filepath, index=False)
       
    print(f"Data saved to {filepath}")

def date_format(date):
    date = date.replace("-", ",")
    date = date.replace(" ", ",")
    date = date.replace(":", ",")
    date = date.replace("/", ",")
    return date

def limit_region_coords(lat_cent, lon_cent, region_rad):

    #Differential of the angle and then the lat and long
    d_theta = region_rad / R_earth
    d_lat = np.degrees(d_theta)  
    d_lon = np.degrees(d_theta) / np.cos(np.radians(lat_cent))

    #Creating the square interval
    lat_min = lat_cent - d_lat
    lat_max = lat_cent + d_lat
    lon_min = lon_cent - d_lon
    lon_max = lon_cent + d_lon
    
    return lat_min, lat_max, lon_min, lon_max

def get_lat_lot_from_file(file="wrk_df.csv"):
    path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(path, ".."))

    file_path = os.path.join(project_root, f"A00_data/B_eq_raw/{file}")

    df = pd.read_csv(file_path)

    id = df['id'].values
    lat = df['latitude'].values
    lon = df['longitude'].values

    return id, lat, lon

def simulate_min_mag_by_radius(radius, max_trigger_index = 100.0, L_method = "Singh"):

    distance_list = np.arange(15, radius+15, radius/15) 
    min_magnitude = np.array([])
    
    for distance in distance_list: 
        fault_length = distance / max_trigger_index
 
        if L_method == "Singh":
            min_magnitude = np.append(min_magnitude, np.ceil(4 + 2 *  np.log10(fault_length)))

        elif L_method == "USGS":
            min_magnitude = np.append(min_magnitude, np.ceil(1.85 + 2 * np.log10(fault_length)))

        else:
            raise ValueError("Invalid L_method. Choose 'Singh' or 'USGS'.")

    return min_magnitude, distance_list

#-------------------------------------------------------------------
# Preprocess.py
#-------------------------------------------------------------------

def fault_length(magnitude, L_method = "Singh"):
    if L_method == "Singh":
        L = np.sqrt(10**(magnitude - 4))
    
    elif L_method == "USGS":
        L = 10**(0.5 * magnitude - 1.85)
    return L

def distance_calculation(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

    distance = R_earth * c
    return id, distance

# This function must be called only after the working_df function, it uses the wrk_df.csv file
def trigger_index(L_method="Singh", file_name="wrk_df.csv"):

    file_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(file_path, ".."))

    file_path = os.path.join(project_root, f"A00_data/B_eq_processed/{file_name}")

    df = pd.read_csv(file_path)
    center_coords = ref[2]
    lat1 = center_coords[0]
    lon1 = center_coords[1]

    result_df = pd.DataFrame(columns=["id","time", "magnitude", "magtype", "depth", "latitude", "longitude", "distance", "trigger_index" ])
    
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Procesando filas"):
        lat2 = row["latitude"]
        lon2 = row["longitude"]
        mag = row["magnitude"]
        L = fault_length(mag, L_method = L_method)
        d = distance_calculation(lat1, lon1, lat2, lon2)[1]
        trigger_index = round(d / L, 3)

        result_df.loc[index] = [row["id"], row["time"], row["magnitude"], row["magtype"], row["depth"], row["latitude"], row["longitude"], round(d, 3), trigger_index]
    
    saving_data(result_df, "wrk_df.csv", folder="B_eq_processed")
    return result_df

def discard_by_max_trigger_index(file="wrk_df.csv", max_trigger_index= 40.0):
    
    trigger_index(L_method="Singh")
    
    path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(path, ".."))

    file_path = os.path.join(project_root, f"A00_data/B_eq_processed/{file}")

    df = pd.read_csv(file_path)
    result_df = df[df["trigger_index"] <= max_trigger_index]

    if result_df.empty == True:
        print(f"There are no records that fulldfill the condition of trigger index > {max_trigger_index}")
    else:
        print(f"There were {len(result_df)} records saved")

    saving_data(result_df, "trigger_index_filtered.csv", folder = "B_eq_processed")
    return result_df
 
def get_all_events(answer = "no"):
    if answer == "yes":
        download_all_by_region(*ref)
        trigger_index(L_method = "Singh", file_name = "all_events_wrk_df.csv")
        discard_by_max_trigger_index("all_events_wrk_df.csv", 40)
        return print("All vents downloaded in 'all_events_wrk_df.csv'")
    elif answer == "no":
        download_optimized(*ref)
        trigger_index(L_method = "Singh")
        discard_by_max_trigger_index("wrk_df.csv", 40)
        return print("Only relevants events downloaded in 'wrk_df.csv'")

#--------------------------------------------------------------------
# process_eq_data.py
#--------------------------------------------------------------------


def main():
    try:
        # Update data to the new parameters
        print("🔄 Loading data...")
        
        get_all_events("yes")    

        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.abspath(os.path.join(current_dir, ".."))
        
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
        print(f"❌ Unexpected error: {str(e)}", file = sys.stderr)
        return 1

def generate_table(data, output_folder):
    try:
        table_html_path = os.path.join(output_folder, "eq_table.html")

        # Convertir el DataFrame a HTML (solo las primeras 100 filas)
        html_table = data.to_html(
            index = False,
            border = 0,
            classes = "table table-striped",
            justify = "center"
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
        print(f"❌ Error generating table: {str(e)}", file = sys.stderr)
        raise

def generate_map(data, output_folder, is_filtered=False):
    try:
        # Determinar el nombre del archivo y el título del mapa según el DataFrame
        if is_filtered:
            map_html_path = os.path.join(output_folder, "eq_map_filtered.html")
            map_title = "Filtered Earthquake Trigger Index Map"
            os.makedirs(output_folder, exist_ok = True)
        else:
            map_html_path = os.path.join(output_folder, "eq_map.html")
            map_title = "Earthquake Trigger Index Map"

        # Crear el mapa principal con los datos sísmicos
        fig = px.scatter_geo(
            data,
            lat = "latitude",
            lon = "longitude",
            size = data["magnitude"]*2,
            color = "trigger_index",
            color_continuous_scale = "Viridis",
            hover_name = "id",
            title = map_title
        )

        # Coordenadas del volcán (centro de referencia)
        lat_cent, lon_cent = ref[2]
        reg = ref[3] + 50
        lat_min, lat_max, lon_min, lon_max = limit_region_coords(lat_cent, lon_cent, reg)

        fig.add_trace(
            go.Scattergeo(
                lat = [lat_cent],
                lon = [lon_cent],
                mode = "markers+text",
                marker = dict(
               symbol = "triangle-up",
               size = 15,
              color = "red"
            ),
            text = ["Reference"],
            textposition = "bottom right", 
            textfont = dict(
                size = 10,  
                color = "black"
            ),
            hovertext = ["Volcán (Información adicional)"], 
            hoverinfo = "text"
        )
    )

        fig.add_trace(
            go.Scattergeo(
                lat = [lat_min, lat_min, lat_max, lat_max, lat_min],
                lon = [lon_min, lon_max, lon_max, lon_min, lon_min],
                mode = "lines",
                line = dict(color = "red", width = 2),
                name = "Search Area",
                showlegend = False
            )
        )

        fig.update_geos(
            projection_type = "mercator",
            center = {"lat": lat_cent, "lon": lon_cent},
            fitbounds = "locations",
            lataxis = {"range": [lat_min, lat_max]},
            lonaxis = {"range": [lon_min, lon_max]},
            visible = True,
            showland = True,
            landcolor = "lightgray",
            showocean = True,
            oceancolor = "lightblue",
            showcountries = True,
            countrycolor = "black",
            showcoastlines = True,
            coastlinecolor = "black",
            coastlinewidth = 1,
            showrivers = True,
            rivercolor = "blue",
            showlakes = True,
            lakecolor = "blue",
            riverwidth = 1,
            resolution = 50
        )

        fig.update_geos(lataxis_showgrid = True, lonaxis_showgrid = True)

        fig.update_layout(
            title_font = dict(size = 20),
            margin = {"r": 0, "t": 50, "l": 0, "b": 0}
        )
        
        os.makedirs(output_folder, exist_ok = True) 
        fig.write_html(map_html_path, full_html = True)
        print(f"✅ Map saved to: {map_html_path}")

        if os.path.exists(map_html_path):
            with open(map_html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

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

            with open(map_html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            print(f"✅ Map saved to: {map_html_path}")
        else:
            print(f"❌ Error: Map HTML file not found at {map_html_path}", file = sys.stderr)
    except Exception as e:
        print(f"❌ Error generating map: {str(e)}", file = sys.stderr)
        raise

def generate_histogram(data, output_folder):
    try:
        hist_html_path = os.path.join(output_folder, "eq_trigger_histogram.html")

        fig = px.histogram(
            data,
            x = "time",
            nbins = 60,
            title = "Trigger Index Histogram",
            marginal = "rug"
        )

        fig.update_layout(
            title_font = dict(size = 20),
            xaxis_title = "Date",
            yaxis_title = "Frequency",
            bargap = 0.2,
            coloraxis_colorbar = dict(
                title = "Trigger Index",
                tickvals = [data["trigger_index"].min(), data["trigger_index"].max()],
                ticktext = ["Low", "High"]),  
            xaxis = dict(
                showgrid = True,
                gridcolor = "lightgray",
                gridwidth = 0.5,
                tickformat = "%Y-%m"
            ),
            yaxis = dict(
                showgrid = True,
                gridcolor = "lightgray",
                gridwidth = 0.5,
            )
        )

        fig.write_html(hist_html_path, full_html=True)
        print(f"✅ Histogram saved to: {hist_html_path}")
    except Exception as e:
        print(f"❌ Error generating histogram: {str(e)}", file=sys.stderr)
        raise


def count_events_per_month(data):
    data["time"] = pd.to_datetime(data["time"], errors="coerce")
    data = data.dropna(subset=["time"])

    monthly_counts = data.resample("ME", on = "time").size().reset_index(name = "event_count")
    monthly_counts.rename(columns = {"time": "date"}, inplace = True)

    return monthly_counts

def plot_events_histogram(file = "wrk_df.csv"):
    path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(path, ".."))

    file_path = os.path.join(project_root, f"A00_data/B_eq_processed/{file}")
    df = pd.read_csv(file_path)

    df["time"] = pd.to_datetime(df["time"], errors = 'coerce')
    df = df.dropna(subset = ["time"])

    total_events = len(df)
    events_per_month = count_events_per_month(df)

    fig = px.bar(
        events_per_month,
        x = "date",
        y = "event_count",
        title = "Seismic Events Histogram",
        labels={"date": "Date", "event_count": "Number of events"}
    )

    fig.update_layout(
        title_font = dict(size=20),
        xaxis_title = "Date",
        yaxis_title = "Number of Events",
        xaxis = dict(
            showgrid = True,
            gridcolor = "lightgray",
            gridwidth = 0.5,
            tickformat = "%Y-%m" 
        ),
        yaxis = dict(
            showgrid = True,
            gridcolor = "lightgray",
            gridwidth = 0.5,
        ),
        bargap = 0.2,
    )
        
    fig.add_annotation(
        xref = "paper",
        yref = "paper",
        x = 0.5, 
        y = 1.1,
        text = f"Total de eventos: {total_events}",
        showarrow = False,
        font = dict(size = 14, color = "black")
    )

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../A04_web/B_images")
    os.makedirs(output_dir, exist_ok = True)
    output_path = os.path.join(output_dir, "eq_histogram.html")

    pio.write_html(fig, output_path, full_html=True, config={"scrollZoom": True})
    print(f"✅ Histograma guardado en: {output_path}")

if __name__ == "__main__":
    sys.exit(main())