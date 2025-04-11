# geometry.py
import pandas as pd
import plotly.express as px
import os
import sys
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime
import numpy as np

# Configuration - La Palma volcano coordinates
VOLCANO_COORDS = {
    'latitude': 28.57,
    'longitude': -17.84,
    'region_radius': 100  # km around volcano
}

# Custom CSS for rounded corners
ROUNDED_CORNERS_CSS = """
<style>
    .plot-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 0 15px rgba(0,0,0,0.1);
        background: white;
        margin: 10px;
    }
    .plotly-graph-div {
        width: 100%;
        height: 100%;
        border-radius: 15px;
    }
    .modebar {
        top: 60px !important;
    }
</style>
"""

def add_rounded_corners(html_path):
    """Add rounded corners CSS to generated HTML files"""
    try:
        with open(html_path, 'r+', encoding='utf-8') as f:
            content = f.read()
            f.seek(0)
            # Add CSS and container div
            content = content.replace('<head>', '<head>' + ROUNDED_CORNERS_CSS)
            content = content.replace('<div id="', '<div class="plot-container"><div id="')
            content = content.replace('</body>', '</div></body>')
            f.write(content)
    except Exception as e:
        print(f"❌ Error adding rounded corners: {str(e)}", file=sys.stderr)

def load_data(file_name):
    """Load earthquake data from CSV with correct relative paths"""
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_path = os.path.join(base_dir, "A00_data", "B_eq_processed", file_name)
        
        print(f"🔄 Loading data from: {data_path}")
        
        if not os.path.exists(data_path):
            print(f"❌ File not found at: {data_path}")
            return pd.DataFrame()
        
        df = pd.read_csv(data_path)
        
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'], errors='coerce')
            df = df.dropna(subset=['time'])
        
        print(f"✅ Loaded {len(df)} records from {file_name}")
        return df
    
    except Exception as e:
        print(f"❌ Error loading {file_name}: {str(e)}", file=sys.stderr)
        return pd.DataFrame()

def generate_map(data, output_folder, is_filtered=False):
    """Generate earthquake map with Canary Islands focus"""
    try:
        output_path = os.path.join(output_folder, 
                                 "eq_map_filtered.html" if is_filtered else "eq_map.html")
        title = "Filtered Earthquakes" if is_filtered else "Earthquake Trigger Index"
        
        # Create base figure
        fig = go.Figure()
        
        # Add earthquake data
        fig.add_trace(go.Scattergeo(
            lon = data['longitude'],
            lat = data['latitude'],
            text = data['id'],
            marker = dict(
                size = data['magnitude']*3,
                color = data['trigger_index'],
                colorscale = 'Viridis',
                colorbar = dict(title='Trigger Index', thickness=15, len=0.5),
                line = dict(width=0.5, color='black'),
                opacity = 0.8
            ),
            name = 'Earthquakes',
            hoverinfo = 'text+lon+lat'
        ))
        
        # Add volcano marker
        fig.add_trace(go.Scattergeo(
            lon = [-17.84],
            lat = [28.57],
            text = ['Cumbre Vieja Volcano'],
            marker = dict(size=12, color='red', symbol='triangle-up'),
            name = 'Volcano',
            hoverinfo = 'text'
        ))
        
        # Configure map view
        fig.update_geos(
            resolution = 25,
            scope = 'europe',
            showcountries = True,
            countrycolor = 'black',
            showsubunits = True,
            subunitcolor = 'grey',
            showland = True,
            landcolor = 'rgb(243, 243, 243)',
            showocean = True,
            oceancolor = 'rgb(212, 212, 255)',
            coastlinewidth = 1.5,
            lataxis_range = [27.5, 29.8],  # Canary Islands latitude range
            lonaxis_range = [-18.5, -13.0] # Canary Islands longitude range
        
        )
        
        fig.update_layout(
            title = dict(text=f"{title}<br><sup>Canary Islands</sup>", x=0.5, font=dict(size=20)),
            margin = dict(l=0, r=0, t=60, b=0),
            geo = dict(bgcolor='white', subunitwidth=1)
        )
        
        os.makedirs(output_folder, exist_ok=True)
        fig.write_html(output_path)
        add_rounded_corners(output_path)
        
        print(f"✅ Map saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)

def generate_histogram(data, output_folder):
    """Generate trigger index histogram with range slider"""
    try:
        hist_html_path = os.path.join(output_folder, "eq_trigger_histogram.html")
        total_events = len(data)

        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=data["trigger_index"],
            nbinsx=60,
            marker_color="#1f77b4",
            marker_line_color='black',
            marker_line_width=0.5,
            opacity=0.8,
            name="Trigger Index",
            hovertemplate="Value: %{x}<br>Count: %{y}<extra></extra>"
        ))

        fig.update_layout(
            title=f"Trigger Index Distribution (Total: {total_events})",
            title_font=dict(size=22, family="Arial"),
            xaxis_title="Trigger Index Value",
            yaxis_title="Number of Events",
            bargap=0.1,
            plot_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridcolor='lightgray',
                gridwidth=0.5,
                rangeslider=dict(visible=True, thickness=0.05, bgcolor='lightgray'),
                zeroline=True,
                zerolinecolor='black'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='lightgray',
                gridwidth=0.5,
                zeroline=True,
                zerolinecolor='black'
            ),
            margin=dict(l=50, r=50, t=80, b=50),
            hovermode="x unified"
        )

        fig.write_html(hist_html_path, full_html=True, config={'scrollZoom': True})
        add_rounded_corners(hist_html_path)
        print(f"✅ Trigger index histogram saved to: {hist_html_path}")

    except Exception as e:
        print(f"❌ Error generating histogram: {str(e)}", file=sys.stderr)

def plot_events_histogram(output_folder):
    """Generate time-based histogram with consistent styling"""
    try:
        df = load_data("wrk_df.csv")
        if df.empty:
            return

        total_events = len(df)
        output_path = os.path.join(output_folder, "eq_histogram.html")

        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=df["time"],
            nbinsx=30,
            marker_color="#1f77b4",
            marker_line_color='black',
            marker_line_width=0.5,
            opacity=0.8,
            xbins=dict(start=df["time"].min(), end=df["time"].max(), size='M1'),
            name="Earthquakes"
        ))

        fig.update_layout(
            title=f"Earthquake Events Over Time (Total: {total_events})",
            title_font=dict(size=22, family="Arial"),
            xaxis_title="Date",
            yaxis_title="Number of Events",
            bargap=0.1,
            plot_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridcolor='lightgray',
                gridwidth=0.5,
                rangeslider=dict(visible=True, thickness=0.1, bgcolor='lightgray'),
                type='date',
                tickformat="%b %Y"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='lightgray',
                gridwidth=0.5,
                zeroline=True,
                zerolinecolor='black'
            ),
            margin=dict(l=50, r=50, t=80, b=50),
            hovermode="x unified"
        )

        pio.write_html(fig, output_path, full_html=True, config={'scrollZoom': True})
        add_rounded_corners(output_path)
        print(f"✅ Events timeline histogram saved to: {output_path}")

    except Exception as e:
        print(f"❌ Error generating events histogram: {str(e)}", file=sys.stderr)

def generate_table(data, output_folder):
    """Generate HTML table of earthquake data"""
    try:
        table_html_path = os.path.join(output_folder, "eq_table.html")
        
        html_table = data.head(100).to_html(
            index=False,
            border=0,
            classes="table table-striped",
            justify="center"
        )

        full_html = f"""
        <html>
        <head>
            <title>Earthquake Data Table</title>
            {ROUNDED_CORNERS_CSS}
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 20px;
                }}
                .table-container {{
                    border-radius: 15px;
                    overflow: hidden;
                    box-shadow: 0 0 15px rgba(0,0,0,0.1);
                    margin: 10px;
                }}
                .table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .table th, .table td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: center;
                }}
                .table th {{
                    background-color: #f2f2f2;
                    position: sticky;
                    top: 0;
                }}
                .table tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .table tr:hover {{
                    background-color: #f1f1f1;
                }}
            </style>
        </head>
        <body>
            <div class="table-container">
                <h1 style="text-align:center;">Earthquake Data</h1>
                {html_table}
            </div>
        </body>
        </html>
        """

        with open(table_html_path, "w", encoding="utf-8") as f:
            f.write(full_html)

        print(f"✅ Table saved to: {table_html_path}")

    except Exception as e:
        print(f"❌ Error generating table: {str(e)}", file=sys.stderr)

def main():
    try:
        print("\n" + "="*50)
        print("🌋 Earthquake Data Visualization Generator")
        print("="*50 + "\n")
        
        eq_data = load_data("wrk_df.csv")
        filtered_data = load_data("trigger_index_filtered.csv")
        
        if eq_data.empty:
            print("❌ No earthquake data loaded - check file paths", file=sys.stderr)
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            expected_path1 = os.path.join(base_dir, "A00_data", "B_eq_processed", "wrk_df.csv")
            expected_path2 = os.path.join(base_dir, "A00_data", "B_eq_processed", "trigger_index_filtered.csv")
            print(f"Expected files at:\n- {expected_path1}\n- {expected_path2}")
            return 1
        
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        output_folder = os.path.join(base_dir, "A04_web", "B_images")
        os.makedirs(output_folder, exist_ok=True)
        
        print("\n" + "="*50)
        print("🔄 Generating visualizations...")
        print("="*50 + "\n")
        
        generate_table(eq_data, output_folder)
        generate_map(eq_data, output_folder, is_filtered=False)
        generate_map(filtered_data, output_folder, is_filtered=True)
        generate_histogram(eq_data, output_folder)
        plot_events_histogram(output_folder)
        
        print("\n" + "="*50)
        print("✅ All visualizations generated successfully!")
        print(f"📁 Output folder: {output_folder}")
        print("="*50 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())