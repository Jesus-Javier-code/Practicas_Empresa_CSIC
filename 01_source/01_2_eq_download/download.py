from libcomcat.search import count, get_event_by_id, search
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd

def limit_region_coords(lat_cent, lon_cent, region_rad):
    
    R_earth = 6357.5 # km | mean between equatorial and polar radius

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
    
    return date

def download(date_i, date_f, min_mag, center_coords, reg_rad):

    lat_cent, lon_cent = center_coords
    lat_min, lat_max, lon_min, lon_max = limit_region_coords(lat_cent, lon_cent, reg_rad)

    date_i = date_format(date_i)
    date_f = date_format(date_f)

    date_i = datetime.strptime(date_i, "%Y,%m,%d,%H,%M")
    date_f = datetime.strptime(date_f, "%Y,%m,%d,%H,%M")

    # Creating magnitudes 
    magnitude_intervals= [
        (min_mag, 2),
        (max(min_mag, 2), 4),
        (max(min_mag, 4), 6),
        (max(min_mag, 6), 8),
        (max(min_mag, 8), 100) # Using 100 as no superior limit function
    ]
    
    all_eq_data = []

    for min_m, max_m in magnitude_intervals:
        search_params = {
            "starttime": date_i,
            "endtime": date_f,
            "minlatitude": lat_min,
            "maxlatitude": lat_max,
            "minlongitude": lon_min,
            "maxlongitude": lon_max,
            "minmagnitude": min_m,
            "eventtype": "earthquake"
        }
        if max_m is not None:
            search_params["maxmagnitude"] = max_m

        earthquakes = search(**search_params)

        if not earthquakes: 
            print(
                "There were no coincidences found that fullfilled the given conditions (looking for magnitudes up to %d)" %max_m  
                  )
            continue

        all_eq_data.extend([
            {
                "ID": ev.id,
                "Date": ev.time.strftime("%Y-%m-%d %H:%M"),
                "Magnitude": ev.magnitude,
                "Latitude": ev.latitude,
                "Longitude": ev.longitude,
                "Depth (km)": ev.depth,
            }
            for ev in earthquakes
        ])

    df = pd.DataFrame(all_eq_data)
    
    return df

download("2025-01-01 00:00", "2025-03-30 00:00", 2.5, (32.62691152238639, -116.34553204019909), 5000)

