import libcomcat as lcc
import numpy as np
import pandas as pd

def limit_region_coords(lat_cent, lon_cent, region_rad):
    R_earth = 6357.5 # km | mean between equatorial and polar radius

    d_theta = region_rad / R_earth # Differential of angle from the centre in rads
    d_lat = np.degrees(d_theta)  # Variación en latitud
    d_lon = np.degrees(d_theta) / np.cos(np.radians(lat_cent))

    lat_min = lat_cent - d_lat
    lat_max = lat_cent + d_lat
    lon_min = lon_cent - d_lon
    lon_max = lon_cent + d_lon
    
    return lat_min, lat_max, lon_min, lon_max

def download    (date_i, date_f, min_mag, center_coords, reg_rad):
    lat_cent = center_coords[0]
    lon_cent = center_coords[1]

    lat_min, lat_max, lon_min, lon_max = limit_region_coords(lat_cent, lon_cent, reg_rad)

    events = lcc.search(
            starttime = date_i,
            endtime =date_f, 
            minlatitude = lat_min,
            maxlatitude = lat_max,
            minlongitude = lon_min,
            maxlongitude = lon_max,
            minmagnitude = min_mag
    )

    eq_data = [
        {
            "ID": ev.id,
            "Date": ev.time.strftime("%Y-%m-%d %H_%M:%S"),
            "Magnitude": ev.magnitude,
            "Latitude": ev.latitude,
            "Longitude": ev.longitude,
            "Depth (km)": ev.depth
        }
        for ev in events
    ]

    df = pd.DataFrame(eq_data)
    return df


# d/sqrt(L*W)