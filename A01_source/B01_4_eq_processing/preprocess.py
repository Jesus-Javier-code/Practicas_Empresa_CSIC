import numpy as np
import pandas as pd
import sys
import os
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from A01_source.B01_2_eq_download import utils as utils
from A01_source.B01_2_eq_download import download as dwl

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

def trigger_index(L_method="Singh"):
    df = pd.read_csv("A00_data\B_eq_processed\wrk_df.csv")
    center_coords = dwl.ref[2]
    lat1 = center_coords[0]
    lon1 = center_coords[1]

    result_df = pd.DataFrame(columns=["id", "latitude", "longitude", "trigger_index", "distance", "magnitude", "magtype" ])
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Procesando filas"):
        lat2 = row["latitude"]
        lon2 = row["longitude"]
        mag = row["magnitude"]
        L = fault_length(mag, L_method= L_method)
        d = distance_calculation(lat1, lon1, lat2, lon2)[1]
        trigger_index = d / L

        result_df.loc[index] = [row["id"], row["latitude"], row["longitude"], trigger_index, d, row["magnitude"], row["magtype"]]
    
    utils.saving_data(result_df, "trigger_index.csv", folder="B_eq_processed")
    return result_df

trigger_index()