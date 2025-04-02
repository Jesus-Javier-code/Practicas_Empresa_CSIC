import netCDF4

def explore_nc_file(file_path):
    try:
        # Open the .nc file
        dataset = netCDF4.Dataset(file_path, mode='r')
        print(f"File: {file_path}")
        print(f"Global Attributes: {dataset.ncattrs()}")
        print("\nGroups and Variables:")

        # Explore groups and variables
        def explore_group(group, indent=0):
            prefix = "  " * indent
            print(f"{prefix}Group: {group.path}")
            print(f"{prefix}  Attributes: {group.ncattrs()}")
            print(f"{prefix}  Dimensions: {list(group.dimensions.keys())}")
            print(f"{prefix}  Variables:")
            for var_name, var in group.variables.items():
                print(f"{prefix}    {var_name}: {var}")
            for subgroup_name, subgroup in group.groups.items():
                explore_group(subgroup, indent + 1)

        explore_group(dataset)

        # Close the dataset
        dataset.close()
    except Exception as e:
        print(f"Error: {e}")

# Example usage
file_path = "/Users/moni/Desktop/Practicas_Empresa_CSIC/00_data/raw/data_VJ/2025_085/VJ102IMG.A2025085.0218.021.2025085110108.nc"
explore_nc_file(file_path)