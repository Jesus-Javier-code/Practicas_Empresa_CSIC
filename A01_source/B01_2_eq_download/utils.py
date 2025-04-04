import os
import pandas as pd

def saving_data(df, filename, folder="eq_raw"):

    script_dir = os.path.dirname(os.path.abspath(__file__))  # Script path
    project_root = os.path.abspath(os.path.join(script_dir, "../../"))  # Project root path

    eq_dir = os.path.join(project_root, f"00_data/{folder}") # Eq. data folder

    if not os.path.exists(eq_dir):
        os.makedirs(eq_dir)

    filepath = os.path.join(eq_dir, filename) # File path to save the data

    df.to_csv(filepath, index=False)
       
    print(f"Data saved to {filepath}")