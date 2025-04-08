# process_eq_data.py
import pandas as pd
import plotly.express as px
from great_tables import GT, md
import os
import sys

def main():
    try:
        # Configure paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(current_dir))
        
        input_csv = os.path.join(base_dir, "A00_data", "B_eq_processed", "trigger_index.csv")
        output_folder = os.path.join(base_dir, "A04_web", "B_images")
        
        # Verify input file exists
        if not os.path.exists(input_csv):
            print(f"❌ Error: File not found at {input_csv}", file=sys.stderr)
            return 1
        
        # Create output folder
        os.makedirs(output_folder, exist_ok=True)
        
        # Load data
        eq_data = pd.read_csv(input_csv)
        print(f"✅ Data loaded successfully ({len(eq_data)} records)")
        
        # Generate outputs
        generate_table(eq_data, output_folder)
        generate_map(eq_data, output_folder)
        generate_histogram(eq_data, output_folder)
        
        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}", file=sys.stderr)
        return 1

def generate_table(data, output_folder):
    try:
        table_html_path = os.path.join(output_folder, "eq_table.html")
        table = (
            GT(data.head(100))
            .fmt_number(columns=["latitude", "longitude"], decimals=4)
            .fmt_number(columns=["distance"], decimals=2, pattern="{x} km")
            .fmt_number(columns=["trigger_index"], decimals=2)
            .tab_header(title=md("**Earthquake Trigger Index**"))
        )
        
        with open(table_html_path, "w", encoding="utf-8") as f:
            f.write(str(table))
        print(f"✅ Table saved to: {table_html_path}")
    except Exception as e:
        print(f"❌ Error generating table: {str(e)}", file=sys.stderr)
        raise

def generate_map(data, output_folder):
    try:
        map_html_path = os.path.join(output_folder, "eq_map.html")
        fig = px.scatter_geo(
            data,
            lat='latitude',
            lon='longitude',
            size=data['magnitude']*2,
            color='trigger_index',
            color_continuous_scale='Viridis',
            hover_name='id',
            projection='natural earth'
        )
        fig.write_html(map_html_path, full_html=False)
        print(f"✅ Map saved to: {map_html_path}")
    except Exception as e:
        print(f"❌ Error generating map: {str(e)}", file=sys.stderr)
        raise

def generate_histogram(data, output_folder):
    try:
        hist_html_path = os.path.join(output_folder, "eq_histogram.html")
        fig = px.histogram(
            data,
            x='trigger_index',
            nbins=30,
            title='Trigger Index Distribution'
        )
        fig.write_html(hist_html_path, full_html=False)
        print(f"✅ Histogram saved to: {hist_html_path}")
    except Exception as e:
        print(f"❌ Error generating histogram: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    sys.exit(main())