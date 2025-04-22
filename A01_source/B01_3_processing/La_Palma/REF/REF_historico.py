import os
import glob
import numpy as np
import xarray as xr
import rioxarray
from tqdm import tqdm
from datetime import datetime
import calendar
from pathlib import Path
from dateutil.relativedelta import relativedelta

# === CONFIGURATION ===
# Resolve the current script's path
script_path = Path(__file__).resolve()

# Dynamically locate the root project directory based on its name
project_dir = next(p for p in script_path.parents if p.name == "Practicas_Empresa_CSIC")

# Define input and output directories for brightness temperature data and REF results
base_path = project_dir / "00_data" / "processed" / "BT_daily_pixels"
output_dir = project_dir / "00_data" / "processed" / "REF"
output_dir.mkdir(parents=True, exist_ok=True)

# === VOLCANO REGION (La Palma) ===
# Define the geographic bounding box for the area of interest (the volcano region)
lat_min = 28.55
lat_max = 28.65
lon_min = -17.93
lon_max = -17.80

# === DATE RANGE TO PROCESS ===
# Set the initial and final dates for which REF files should be generated
start_date = datetime(2021, 12, 1)
end_date = datetime(2025, 2, 1)
current_date = start_date

# === MAIN LOOP: iterate month by month ===
while current_date <= end_date:
    year_ref = current_date.year
    month_ref = current_date.month

    try:
        print(f"\n=== Generating REF for {year_ref}-{month_ref:02d} ===")

        # Calculate Julian day range for the current month
        first_day = datetime(year_ref, month_ref, 1)
        last_day = datetime(year_ref, month_ref, calendar.monthrange(year_ref, month_ref)[1])
        julian_start = first_day.timetuple().tm_yday
        julian_end = last_day.timetuple().tm_yday

        # === FIND DAILY FILES ===
        # Collect all brightness temperature files for the current month
        files = []
        for julian_day in range(julian_start, julian_end + 1):
            folder = os.path.join(base_path, f"{year_ref}_{julian_day:03d}")
            files += glob.glob(os.path.join(folder, f"BT_LaPalma_VJ102IMG_{year_ref}_*.nc"))

        print(f"Files found: {len(files)}")

        # Skip this month if no files are available
        if len(files) == 0:
            print("No files. Skipping this month.")
            current_date += relativedelta(months=1)
            continue

        # === CREATE TEMPLATE GRID FROM FIRST FILE ===
        # Use the first file as a template to define the grid and CRS for reprojection
        ds_ref = xr.open_dataset(files[0])
        bt = ds_ref["BT_I05"]
        bt_template = xr.DataArray(
            data=bt.data,
            dims=("y", "x"),
            coords={"y": np.arange(bt.shape[0]), "x": np.arange(bt.shape[1])},
            name="brightness_temperature"
        )
        bt_template.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
        bt_template.rio.write_crs("EPSG:4326", inplace=True)

        # === PROCESS EACH SCENE ===
        # For each file: reproject, clip to volcano region, filter by quality
        stack_reprojected = []
        valid_files = []

        for file in tqdm(files):
            ds = xr.open_dataset(file)
            bt = ds["BT_I05"]
            lat = ds["latitude"]
            lon = ds["longitude"]

            # Build a new DataArray with proper spatial metadata
            bt_scene = xr.DataArray(
                data=bt.data,
                dims=("y", "x"),
                coords={"y": np.arange(bt.shape[0]), "x": np.arange(bt.shape[1])},
                name="brightness_temperature"
            )
            bt_scene.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
            bt_scene.rio.write_crs("EPSG:4326", inplace=True)

            # Reproject to match the template grid
            bt_aligned = bt_scene.rio.reproject_match(bt_template)

            # Use latitude and longitude arrays to identify the area of interest
            lat_vals = lat.values
            lon_vals = lon.values
            mask = (
                (lat_vals >= lat_min) & (lat_vals <= lat_max) &
                (lon_vals >= lon_min) & (lon_vals <= lon_max)
            )

            if not np.any(mask):
                print(f"{os.path.basename(file)} → Cropped area is empty. Skipping.")
                continue

            # Get the bounding box of the masked region
            y_indices, x_indices = np.where(mask)
            y_min, y_max = y_indices.min(), y_indices.max()
            x_min, x_max = x_indices.min(), x_indices.max()

            # Clip the brightness temperature scene to the volcano area
            y_dim, x_dim = bt_aligned.dims
            bt_clipped = bt_aligned.isel(
                **{y_dim: slice(y_min, y_max + 1), x_dim: slice(x_min, x_max + 1)}
            )

            # Apply quality filters based on statistics
            minval = np.nanmin(bt_clipped.values)
            stdval = np.nanstd(bt_clipped.values)
            if stdval > 3 and minval > 210:
                stack_reprojected.append(bt_clipped)
                valid_files.append(os.path.basename(file))
                print(f"{os.path.basename(file)} OK (min={minval:.2f}, std={stdval:.2f})")
            else:
                print(f"{os.path.basename(file)} DISCARDED (min={minval:.2f}, std={stdval:.2f})")

        print(f"Accepted scenes: {len(stack_reprojected)} / {len(files)}")

        if len(stack_reprojected) == 0:
            print("No valid scenes. Skipping this month.")
            current_date += relativedelta(months=1)
            continue

        # === COMPUTE MONTHLY MEAN (REF) ===
        stack = xr.concat(stack_reprojected, dim="time")
        stack["time"] = np.arange(len(stack_reprojected))
        ref = stack.mean(dim="time", skipna=True)

        # === SAVE REF DATASET ===
        ref_ds = ref.to_dataset(name="brightness_temperature_REF")
        ref_ds["brightness_temperature_REF"].attrs["units"] = "K"
        ref_ds.attrs["description"] = "Monthly reference over volcano area (std > 3 and min > 210)"
        ref_ds.attrs["used_files"] = ", ".join(valid_files)

        # Save the NetCDF file
        output_filename = f"Ref_{year_ref}_{month_ref:02d}.nc"
        output_path_final = output_dir / output_filename

        try:
            if output_path_final.exists():
                output_path_final.unlink()
            ref_ds.to_netcdf(output_path_final, mode="w")
            print(f"REF saved to: {output_path_final}")
        except PermissionError:
            # If the file is in use, save an alternative version
            alt_path = output_dir / f"Ref_{year_ref}_{month_ref:02d}_v2.nc"
            ref_ds.to_netcdf(alt_path, mode="w")
            print(f"REF saved as alternative version: {alt_path}")

    except Exception as e:
        print(f"Error processing {year_ref}-{month_ref:02d}: {e}")

    # Move to the next month
    current_date += relativedelta(months=1)