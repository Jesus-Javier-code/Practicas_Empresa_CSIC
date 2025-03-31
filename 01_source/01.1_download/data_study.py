import os
from netCDF4 import Dataset
import xlsxwriter
import numpy as np

# Open the .nc file
file_path = '/Users/moni/Desktop/Practicas_Empresa_CSIC-2/data/raw/data_VJ/2025_085/VJ102IMG.A2025085.0218.021.2025085110108.nc'
# Create an Excel workbook and worksheet outside the group iteration loop
excel_path = '/Users/moni/Desktop/Practicas_Empresa_CSIC-2/output.xlsx'
workbook = xlsxwriter.Workbook(excel_path)
worksheet = workbook.add_worksheet()

# Write headers
worksheet.write(0, 0, "Group Name")
worksheet.write(0, 1, "Variable Name")
worksheet.write(0, 2, "Global Attribute Name")
worksheet.write(0, 3, "Global Attribute Value")

row = 1

with Dataset(file_path, 'r') as nc_file:
    # Iterate through groups and display their contents
    for group_name in nc_file.groups:
        print(f"Group: {group_name}")
        group = nc_file.groups[group_name]
        print("Variables:", list(group.variables.keys()))
        
        # Iterate through variables in the group and show their values
        for var_name in group.variables.keys():
            var_data = group.variables[var_name][:]
            # Use numpy.ma.filled() to replace masked values with NaN
            var_data = np.ma.filled(var_data, np.nan)
            print(f"  Variable: {var_name}, Values: {var_data}")

            # Write the group and variable names to the Excel file
            worksheet.write(row, 0, group_name)
            worksheet.write(row, 1, var_name)
            row += 1

    # Write global attributes to the Excel file
    for attr_name in nc_file.ncattrs():
        value = getattr(nc_file, attr_name)
        # Check if the value is an array and convert it to a list or string
        if isinstance(value, (list, np.ndarray)):
            value = str(value.tolist())  # Convert to list and then to string
        worksheet.write(row, 2, attr_name)
        worksheet.write(row, 3, value)
        row += 1

# Close the workbook
workbook.close()

print(f"Data has been written to {excel_path}")


# Open the .nc file again to extract the specific variable
with Dataset(file_path, 'r') as nc_file:
    # Check if the group exists
    if 'observation_data' in nc_file.groups:
        # Access the group 'observation_data'
        observation_data_group = nc_file.groups['observation_data']
        
        # Check if 'I05_brightness_temperature_lut' exists within this group
        if 'I05_brightness_temperature_lut' in observation_data_group.variables:
            # Access the variable 'I05_brightness_temperature_lut' and handle masked values
            I05_brightness_temperature_lut = np.ma.filled(
                observation_data_group.variables['I05_brightness_temperature_lut'][:], np.nan
            )
            print("I05_brightness_temperature_lut has been saved as an array.")
        else:
            print("Variable 'I05_brightness_temperature_lut' not found in 'observation_data' group.")
    else:
        print("Group 'observation_data' not found in the file.")

mean_value = np.nanmean(I05_brightness_temperature_lut)

print("Mean value:", mean_value)




# Display global attributes and their values
with Dataset(file_path, 'r') as nc_file:
    print("Global Attributes:")
    for attr_name in nc_file.ncattrs():
        value = getattr(nc_file, attr_name)
        print(f"{attr_name}: {value}")