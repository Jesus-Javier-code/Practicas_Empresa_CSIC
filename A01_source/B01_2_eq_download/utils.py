import os
import pandas as pd
import numpy as np
from datetime import datetime
from libcomcat.search import search
from libcomcat.dataframes import get_summary_data_frame, get_detail_data_frame
from tqdm import tqdm


# Constants
R_earth = 6378.1 # km | Equatorial radius (source: NASA's Earth Fact Sheet)

def saving_data(df, filename, folder="B_eq_raw"):

    script_dir = os.path.dirname(os.path.abspath(__file__))  # Script path
    project_root = os.path.abspath(os.path.join(script_dir, "../../"))  # Project root path

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

def mw_to_mo(mw):
     return 10**(3/2 * mw + 16.1)

def get_lat_lot_from_file(file="wrk_df.csv"):
    path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(path, "..", ".."))

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
