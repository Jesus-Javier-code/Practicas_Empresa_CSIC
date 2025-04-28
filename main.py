import subprocess
from pathlib import Path
import sys
import os
import netCDF4


def run_script(script_path):
    """
    Executes a given Python script through the command line using the current Python executable.

    Args:
        script_path (Path): The full path to the Python script that needs to be executed.

    Raises:
        subprocess.CalledProcessError: If an error occurs during script execution.
    """
    try:
        print(f"Running: {script_path}")
        # Execute the script with the current Python executable
        subprocess.run([sys.executable, str(script_path)], check=True)
        print(f"Successfully executed: {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error while running {script_path}: {e}")
        sys.exit(1)  # Stop the execution if an error occurs

def main():
    """
    Main function that organizes and runs all the scripts in sequence to process the data.
    1. Runs the data download script.
    2. Converts the downloaded data to brightness temperature.
    3. Calculates the REF using the data for the month.
    4. Calculates the radiative power based on brightness temperature.
    """
    # Get the base path where the main script is located
    script_path = Path(__file__).resolve().parent
    
    # Directory where all scripts are located
    scripts_directory = script_path / "A01_source"
    
    # Full path for each script that needs to be executed
    download_script_LaPalma = scripts_directory / "B01_1_download" / "La_Palma" / "download_LaPalma.py"
    download_script_Teide = scripts_directory / "B01_1_download" / "Teide" / "download_Teide.py"
    #bt_script_LaPalma = scripts_directory / "B01_3_processing" / "La_Palma" / "BT" / "BT_auto.py"
    #bt_script_Teide = scripts_directory / "B01_3_processing" /  "Teide" / "BT" / "BT_auto.py"
    #ref_script_LaPalma = scripts_directory / "B01_3_processing" / "La_Palma" / "REF" / "REF_auto.py"
    #ref_script_Teide = scripts_directory / "B01_3_processing" / "Teide" / "REF" / "REF_auto.py"
    rp_script_LaPalma = scripts_directory / "B01_3_processing" / "La_Palma" / "radiative_power" / "RP_auto.py"
    rp_script_Teide = scripts_directory / "B01_3_processing" / "Teide" / "radiative_power" / "RP_auto.py"

   
    # Start the automation process
    print("Starting daily automation...")
    
    # Run the scripts in the correct order
    run_script(download_script_LaPalma)  # First, download the data
    run_script(download_script_Teide)
    #run_script(bt_script_LaPalma)        # Then, convert it to brightness temperature (BT)
    #run_script(bt_script_Teide)        # Then, convert it to brightness temperature (BT)
    #run_script(ref_script_LaPalma)       # Next, calculate the REF
    #run_script(ref_script_Teide)       # Next, calculate the REF
    run_script(rp_script_LaPalma)        # Finally, calculate the radiative power (FRP)
    run_script(rp_script_Teide)        # Finally, calculate the radiative power (FRP)


    print("Process completed successfully.")

if __name__ == "__main__":
    main()

    
    