from libcomcat.search import search
from libcomcat.dataframes import get_summary_data_frame, get_detail_data_frame
from datetime import datetime
import pandas as pd
from . import utils as utils
import warnings
from tqdm import tqdm


# The errors given are by the inexistence of data only in the depth parameter
#warnings.filterwarnings("ignore")

# In case it is recquired to filter by minimum magnitude
def search_params(date_i, date_f, min_mag, center_coords, reg_rad):

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
        minmagnitude= 2,
        eventtype= "earthquake"
    )

    summary_events_df = get_summary_data_frame(events)
    utils.saving_data(summary_events_df, "bsc_events_info.csv", folder = "B_eq_raw")
    
    detail_events_df = get_detail_data_frame(events, get_all_magnitudes= True)
    utils.saving_data(detail_events_df, "dtl_mag_events_info.csv", folder = "B_eq_raw")

    return working_df(summary_events_df, detail_events_df), center_coords

def working_df(df1, df2):
    # The mean of this function is to create a working dataframe with the next variables:
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

    utils.saving_data(merged_df, "wrk_df.csv", folder = "B_eq_processed")

    return merged_df

# Example usage of the function
# search_params("2025-01-01 00:00", "2025-03-30 00:00", 4, (32.62691152238639, -116.34553204019909), 5000)

ref = ("2025-01-01 00:00", "2025-03-30 00:00", (32.62691152238639, -116.34553204019909), 500)
download_all_by_region(*ref)
