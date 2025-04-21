import subprocess
from pathlib import Path
import sys
import os



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
    scripts_directory = script_path / "01_source"
    
    # Full path for each script that needs to be executed
    download_script = scripts_directory / "01_1_download" / "download.py"
    bt_script = scripts_directory / "01_3_processing" / "BT" / "BT_auto.py"
    ref_script = scripts_directory / "01_3_processing" / "REF" / "REF_auto.py"
    rp_script = scripts_directory / "01_3_processing" / "radiative_power" / "rp_daily.py"
    
    # Start the automation process
    print("Starting daily automation...")
    
    # Run the scripts in the correct order
    run_script(download_script)  # First, download the data
    run_script(bt_script)        # Then, convert it to brightness temperature (BT)
    run_script(ref_script)       # Next, calculate the REF
    run_script(rp_script)        # Finally, calculate the radiative power (FRP)

    print("Process completed successfully.")

if __name__ == "__main__":
    main()

    
    