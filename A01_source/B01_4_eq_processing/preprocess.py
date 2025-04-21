import numpy as np
import pandas as pd
import sys
import os
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from A01_source.B01_2_eq_download import utils as utils
from A01_source.B01_2_eq_download import download as dwl
from A01_source.B01_2_eq_download.download import ref

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

    distance = utils.R_earth * c
    return id, distance

# This function must be called only after the working_df function, it uses the wrk_df.csv file
def trigger_index(L_method="Singh", file_name="wrk_df.csv"):

    file_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(file_path, "..", ".."))

    file_path = os.path.join(project_root, f"A00_data/B_eq_processed/{file_name}")

    df = pd.read_csv(file_path)
    center_coords = dwl.ref[2]
    lat1 = center_coords[0]
    lon1 = center_coords[1]

    result_df = pd.DataFrame(columns=["id","time", "magnitude", "magtype", "depth", "latitude", "longitude", "distance", "trigger_index" ])
    
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Procesando filas"):
        lat2 = row["latitude"]
        lon2 = row["longitude"]
        mag = row["magnitude"]
        L = fault_length(mag, L_method= L_method)
        d = distance_calculation(lat1, lon1, lat2, lon2)[1]
        trigger_index = round(d / L, 3)

        result_df.loc[index] = [row["id"], row["time"], row["magnitude"], row["magtype"], row["depth"], row["latitude"], row["longitude"], round(d, 3), trigger_index]
    
    utils.saving_data(result_df, "wrk_df.csv", folder="B_eq_processed")
    return result_df

def discard_by_max_trigger_index(file="wrk_df.csv", max_trigger_index= 40.0):
    
    trigger_index(L_method="Singh")
    
    path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(path, "..", ".."))

    file_path = os.path.join(project_root, f"A00_data/B_eq_processed/{file}")

    df = pd.read_csv(file_path)
    result_df = df[df["trigger_index"] <= max_trigger_index]

    if result_df.empty==True:
        print(f"There are no records that fulldfill the condition of trigger index > {max_trigger_index}")
    else:
        print(f"There were {len(result_df)} records saved")

    utils.saving_data(result_df, "trigger_index_filtered.csv", folder="B_eq_processed")
    return result_df
 
def get_all_events(answer="no"):
    if answer == "yes":
        dwl.download_all_by_region(*ref)
        trigger_index(L_method="Singh", file_name="all_events_wrk_df.csv")
        discard_by_max_trigger_index("all_events_wrk_df.csv", 40)
        return print("All vents downloaded in 'all_events_wrk_df.csv'")
    elif answer == "no":
        dwl.download_optimized(*ref)
        trigger_index(L_method="Singh")
        discard_by_max_trigger_index("wrk_df.csv", 40)
        return print("Only relevants events downloaded in 'wrk_df.csv'")

get_all_events("no")