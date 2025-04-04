from libcomcat.search import search, get_event_by_id
from libcomcat.dataframes import get_summary_data_frame, get_magnitude_data_frame, get_detail_data_frame
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
from IPython.display import display, HTML
import pandas as pd
from libcomcat.bin.getcsv import main
from B01_2_eq_download.utils import saving_data
R_earth = 6357.5 # km | mean between equatorial and polar radius

def mw_to_mo(mw):
     return 10**(3/2 * mw + 16.1)

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

def date_format(date):
        
    date = date.replace("-", ",")
    date = date.replace(" ", ",")
    date = date.replace(":", ",")
    date = date.replace("/", ",")
    
    return date

def search_params(date_i, date_f, min_mag, center_coords, reg_rad):

    # Center coordinates must be given as (latitude, longitude) form
    lat_cent, lon_cent = center_coords
    lat_min, lat_max, lon_min, lon_max = limit_region_coords(lat_cent, lon_cent, reg_rad)

    date_i = datetime.strptime(date_format(date_i), "%Y,%m,%d,%H,%M")
    date_f = datetime.strptime(date_format(date_f), "%Y,%m,%d,%H,%M")

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
    saving_data(summary_events_df, "bsc_events_info.csv", folder = "eq_raw")

    detail_events_df = get_detail_data_frame(events, get_all_magnitudes= True)
    saving_data(detail_events_df, "dtl_mag_events_info.csv", folder = "eq_raw")

    return working_df(summary_events_df, detail_events_df)

def working_df(df1, df2):
    # The mean of this function is to create a working dataframe with the next variables:
    # ID, Date, Magnitude, Magtype, Latitude, Longitude, Depth (km)
    
    variables = ["id", "time", "magnitude", "magtype", "latitude", "longitude", "depth"]

    for col in df1.columns:
        if col not in variables:
            df1.drop(columns= col, inplace= True)

    for col in df2.columns:
        if col not in variables:
            df2.drop(columns= col, inplace= True)
    
    merged_df = pd.merge(df1, df2, on= "id", how= "inner")

    for col in variables:
        if col != "id" and f"{col}_y" in merged_df.columns:
            merged_df[col] = merged_df[f"{col}_y"]
            merged_df.drop(columns=[f"{col}_x", f"{col}_y"], inplace=True)
    
    saving_data(merged_df, "wrk_df.csv", folder = "eq_processed")

    return merged_df

# Example usage of the function
search_params("2024-01-01 00:00", "2025-03-30 00:00", 6, (32.62691152238639, -116.34553204019909), 5000)