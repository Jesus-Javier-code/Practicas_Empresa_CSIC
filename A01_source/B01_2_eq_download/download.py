from libcomcat.search import search
from libcomcat.dataframes import get_summary_data_frame, get_detail_data_frame
from datetime import datetime
import pandas as pd
import os
try:
    from . import utils as utils
except ImportError:
    import utils as utils
    
from tqdm import tqdm

#--------------------------------------------------------------------------

# In case it is recquired to filter by minimum magnitude in the whole area (NOT USED)
def search_by_minimum_magnitude(date_i, date_f, min_mag, center_coords, reg_rad):

    # Center coordinates must be given as (latitude, longitude) form
    lat_cent, lon_cent = center_coords
    lat_min, lat_max, lon_min, lon_max = utils.limit_region_coords(lat_cent, lon_cent, reg_rad)

    date_i = datetime.strptime(utils.date_format(date_i), "%Y,%m,%d,%H,%M")
    date_f = datetime.strptime(utils.date_format(date_f), "%Y,%m,%d,%H,%M")

    events = search(
        starttime= date_i,
        endtime= date_f,
        minlatitude= lat_min,
        maxlatitude= lat_max,
        minlongitude= lon_min,
        maxlongitude= lon_max,
        minmagnitude= min_mag,
        eventtype= "earthquake",
        orderby= "time"
    )

    summary_events_df = get_summary_data_frame(events)
    utils.saving_data(summary_events_df, "bsc_info_by_min_mag.csv", folder = "B_eq_raw")

    detail_events_df = get_detail_data_frame(events, get_all_magnitudes= True)
    utils.saving_data(detail_events_df, "mags_info_by_min_mag.csv", folder = "B_eq_raw")

    return working_df(summary_events_df, detail_events_df), center_coords

#-------------------------------------------------------------------------

# This function downloads all events in a given region, the data is stored in eq_raw folder
def download_all_by_region(date_i, date_f, center_coords, reg_rad):

    # Center coordinates must be given as (latitude, longitude) form
    lat_cent, lon_cent = center_coords
    lat_min, lat_max, lon_min, lon_max = utils.limit_region_coords(lat_cent, lon_cent, reg_rad)

    date_i = datetime.strptime(utils.date_format(date_i), "%Y,%m,%d,%H,%M")
    date_f = datetime.strptime(utils.date_format(date_f), "%Y,%m,%d,%H,%M")

    events = search(
        starttime= date_i,
        endtime= date_f,
        minlatitude= lat_min,
        maxlatitude= lat_max,
        minlongitude= lon_min,
        maxlongitude= lon_max,
        minmagnitude= 1,
        eventtype= "earthquake"
    )

    summary_events_df = get_summary_data_frame(events)
    utils.saving_data(summary_events_df, "all_bsc_events_info.csv", folder = "B_eq_raw")
    
    detail_events_df = get_detail_data_frame(events, get_all_magnitudes= True)
    utils.saving_data(detail_events_df, "all_dtl_mag_events_info.csv", folder = "B_eq_raw")

    merged_df = working_df(summary_events_df, detail_events_df, "wrk_df.csv")

    return merged_df, center_coords

def working_df(df1, df2, file_name = "wrk_df.csv"):
    # Create a working dataframe with the next variables:
    # ID, Date, Magnitude, Magtype, Latitude, Longitude, Depth (km)
    
    variables = ["id", "time", "magnitude", "magtype", "latitude", "longitude", "depth"]

    for col in tqdm(df1.columns, desc="Procesando columnas de df1"):
        if col not in variables:
            df1.drop(columns= col, inplace= True)
        else:
            None

    for col in tqdm(df2.columns, desc="Procesando columnas de df2"):
        if col not in variables:
            df2.drop(columns= col, inplace= True)
        else:
            None
    
    merged_df = pd.merge(df1, df2, on= "id", how= "inner")

    for col in  tqdm(variables, desc="Procesando columnas fusionadas"):
        if col != "id" and f"{col}_y" in merged_df.columns:
            merged_df[col] = merged_df[f"{col}_y"]
            merged_df.drop(columns=[f"{col}_x", f"{col}_y"], inplace=True)

    utils.saving_data(merged_df, f"{file_name}", folder = "B_eq_processed")

    return merged_df

def download_optimized(date_i, date_f, center_coords, reg_rad):
    min_mag, distance_list = utils.simulate_min_mag_by_radius(reg_rad, max_trigger_index= 100.0, L_method= "Singh")
    
    # Search area coordinates
    lat_cent, lon_cent = center_coords
    lat_min, lat_max, lon_min, lon_max = utils.limit_region_coords(lat_cent, lon_cent, reg_rad)

    date_i = datetime.strptime(utils.date_format(date_i), "%Y,%m,%d,%H,%M")
    date_f = datetime.strptime(utils.date_format(date_f), "%Y,%m,%d,%H,%M")

    cumulative_summary_df = pd.DataFrame()
    cumulative_detail_df = pd.DataFrame()

    # Smaller search area
    for i in tqdm(range(len(distance_list)), desc=f"Procesando para cada radio"):
        lat_min_list, lat_max_list, lon_min_list, lon_max_list = utils.limit_region_coords(lat_cent, lon_cent, distance_list[i])

        events = search(
            starttime= date_i,
            endtime= date_f,
            minlatitude= lat_min_list,
            maxlatitude= lat_max_list,
            minlongitude= lon_min_list,
            maxlongitude= lon_max_list,
            minmagnitude= min_mag[i],
            eventtype= "earthquake",
            orderby= "time"
        )

        if not events:
            print(f"No se encontraron eventos con magnitud {min_mag[i]} para la distancia {round(distance_list[i], 2)} km.")
            continue

        try:
            summary_events_df = get_summary_data_frame(events)
            detail_events_df = get_detail_data_frame(events, get_all_magnitudes=True)

            required_columns = ["id", "time", "latitude", "longitude", "depth", "magnitude"]
            if not set(required_columns).issubset(detail_events_df.columns):
                print(f"Columnas faltantes en el DataFrame: {set(required_columns) - set(detail_events_df.columns)}")
                continue

            cumulative_summary_df = pd.concat([cumulative_summary_df, summary_events_df]).drop_duplicates(subset="id")
            cumulative_detail_df = pd.concat([cumulative_detail_df, detail_events_df]).drop_duplicates(subset="id")

        except KeyError as e:
            print(f"Error procesando los eventos: {e}")
            continue

    utils.saving_data(cumulative_summary_df, "bsc_events_info.csv", folder = "B_eq_raw")
    utils.saving_data(cumulative_detail_df, "dtl_mag_events_info.csv", folder = "B_eq_raw")

    return working_df(cumulative_summary_df, cumulative_detail_df, file_name="trigger_index_filtered.csv"), center_coords

def coordinates_format(lat, lon):
    coords = (lat, lon)
    return coords

def update_ref(date_i, date_f, coords, region):
    ref = ref(date_i, date_f, coords, region)
    return ref

def process_ign_file(file_name, file_path):
    path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(path, "..", ".."))
    file_path = os.path.join(project_root, f"A00_data/B_eq_raw/{file_name}")

    try:
        text_file = pd.read_table(f'{file_name}', sep='\t')
        text_file.to_csv(f'{file_name}', index=False) # index=False para evitar que se agregue una columna de índice
        print(f"Succeed conversion '{file_name}' to CSV")
    except FileNotFoundError:
        print("File not found.")
    except pd.errors.ParserError as e:
        print(f"Error: {e}")
    
    
    return id


date_i = "1973-01-01 00:00"
date_f = "2025-04-29 00:00"
lat_cent = 28.612777777778
lon_cent = -17.866111111111
reg_rad = 350

ref = (date_i, date_f, coordinates_format(lat_cent, lon_cent), reg_rad)

#download_all_by_region(*ref)
#download_optimized(*ref)