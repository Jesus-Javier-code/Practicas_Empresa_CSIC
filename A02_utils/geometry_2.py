import xarray as xr
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import json
import os
import sys
from datetime import datetime

# Configuration
OUTLINE_COLOR = 'rgba(150, 0, 0, 1)'
FILL_COLOR = 'rgba(255, 50, 50, 0.5)'
MAPBOX_STYLE = "open-street-map"

# Eruption period
ERUPTION_START = '2021-09-19'
ERUPTION_END = '2021-12-13'
ERUPTION_COLOR = 'rgba(255, 0, 0, 0.2)'

def load_lava_perimeter():
    """Load lava flow perimeter from GeoJSON"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        geojson_path = os.path.join(base_dir, "A00_data", "B_raw", "perimetro_dron_211123.geojson")
        
        with open(geojson_path) as f:
            data = json.load(f)
        
        return np.array(data['features'][0]['geometry']['coordinates'][0])
    
    except Exception:
        return np.array([
            [-17.8735, 28.6132], [-17.8730, 28.6130], [-17.8725, 28.6128],
            [-17.8720, 28.6125], [-17.8715, 28.6123], [-17.8710, 28.6120],
            [-17.8705, 28.6118], [-17.8700, 28.6115], [-17.8695, 28.6113],
            [-17.8690, 28.6110], [-17.8685, 28.6108], [-17.8680, 28.6105],
            [-17.8675, 28.6103], [-17.8670, 28.6100], [-17.8665, 28.6098],
            [-17.8660, 28.6095], [-17.8655, 28.6093], [-17.8650, 28.6090]
        ])

#LA PALMA VISUALIZATION

def load_netcdf_data():
    """Load and process netCDF data with fallback"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Try multiple possible paths
        possible_paths = [
            os.path.join(base_dir, "A00_data", "B_processed","La_Palma", "Radiative_Power_by_Year_Month_Day", "radiative_power.nc"),
            os.path.join(base_dir, "A00_data", "B_raw", "radiative_power.nc"),
            os.path.join(base_dir, "A00_data", "radiative_power.nc")
        ]
        
        for nc_path in possible_paths:
            if os.path.exists(nc_path):
                print(f"Found netCDF file at: {nc_path}")
                ds = xr.open_dataset(nc_path)
                df = ds.to_dataframe().reset_index()
                
                # Check available columns
                available_cols = df.columns.tolist()
                print("Available columns in netCDF:", available_cols)
                
                # Prepare result DataFrame
                result = pd.DataFrame({
                    'Date': pd.to_datetime(df['time']),
                    'Radiative_Power': df['FRP'] if 'FRP' in df else df['radiative_power'] if 'radiative_power' in df else df.iloc[:, 1]
                }).dropna()
                
                return result
        
        print("No netCDF file found in any of the searched locations")
        return None
    
    except Exception as e:
        print(f"\nError loading netCDF data: {str(e)}")
        return None

def generate_netcdf_visualization(df, output_file):
    """Generate interactive visualization for netCDF data with eruption period"""
    if df is None or df.empty:
        print("No data available for visualization")
        return
    
    # Create figure using plotly express for consistent styling
    fig = px.scatter(df, 
                    x='Date', 
                    y='Radiative_Power',
                    title='<b>Daily Radiative Power</b><br><sup>Tajogaite Volcano (2021-Present) - Red background shows eruption period</sup>',
                    template='plotly_white',
                    labels={
                        'Date': 'Date',
                        'Radiative_Power': 'Radiative Power (MW)'
                    },
                    hover_data={'Date': '|%d/%m/%Y'},
                    opacity=0.7,
                    size_max=10)
    
    # Customize markers to match weekly plot
    fig.update_traces(
        marker=dict(
            size=8,
            color='#3498DB',
            symbol='circle',
            line=dict(width=1, color='#413224'),
            opacity=0.8,
            sizemode='diameter'
        ),
        selector=dict(mode='markers'),
        name='Radiative Power',
        showlegend=True
    )

    # Add eruption period background
    fig.add_vrect(
        x0=ERUPTION_START, 
        x1=ERUPTION_END,
        fillcolor=ERUPTION_COLOR,
        opacity=0.5,
        layer="below",
        line_width=0,
        annotation_text="Eruption Period",
        annotation_position="bottom left",
        annotation_font_size=12,
        annotation_font_color="red"
    )
    
    # Add maximum value annotation
    max_power = df['Radiative_Power'].max()
    max_date = df.loc[df['Radiative_Power'].idxmax(), 'Date']
    fig.add_annotation(
        x=max_date,
        y=max_power,
        text=f"Maximum: {max_power:.0f} MW",
        showarrow=True,
        arrowhead=1,
        ax=-50,
        ay=-40,
        font=dict(size=12, color="#E74C3C"),
        bordercolor="#413224",
        borderwidth=1,
        borderpad=4,
        bgcolor="white"
    )
    
    # Update layout to match weekly plot
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date",
            title_text='Date',
            gridcolor='#f0f0f0'
        ),
        yaxis=dict(
            title_text='Radiative Power (MW)',
            gridcolor='#f0f0f0'
        ),
        hovermode="x unified",
        plot_bgcolor='white',
        margin=dict(l=50, r=50, b=80, t=100),
        title_x=0.5,
        title_font=dict(size=20),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1,
            font=dict(size=12),
            itemclick=False,
            itemdoubleclick=False
        )
    )
    
    # Add custom date range selector
    date_selector_html = """
    <div class="date-selector-container">
        <style>
            .date-selector-container {
                position: absolute;
                top: 70px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 1000;
                background: rgba(255,255,255,0.9);
                padding: 8px 15px;
                border-radius: 20px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                font-family: Arial, sans-serif;
                display: flex;
                align-items: center;
                gap: 10px;
                border: 1px solid #ddd;
            }
            .date-selector-container label {
                font-weight: bold;
                font-size: 12px;
                white-space: nowrap;
            }
            .date-selector-container input {
                padding: 5px;
                width: 120px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
            .date-selector-container button {
                padding: 5px 12px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                white-space: nowrap;
                transition: background-color 0.3s;
            }
            .date-selector-container button:hover {
                background-color: #45a049;
            }
            .date-selector-container button.reset-btn {
                background-color: #f44336;
            }
            .date-selector-container button.reset-btn:hover {
                background-color: #d32f2f;
            }
        </style>
        <label>From:</label>
        <input type="date" id="custom-start-date">
        <label>To:</label>
        <input type="date" id="custom-end-date">
        <button id="custom-apply-dates">Apply</button>
        <button id="custom-reset-dates" class="reset-btn">Reset</button>
    </div>
    <script>
        // Set default dates (last 180 days)
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - 180);
        
        document.getElementById('custom-start-date').valueAsDate = startDate;
        document.getElementById('custom-end-date').valueAsDate = endDate;
        
        // Function to update the plot
        function updatePlotDateRange() {
            const start = document.getElementById('custom-start-date').value;
            const end = document.getElementById('custom-end-date').value;
            
            if (start && end) {
                const plotDiv = document.querySelector('.plotly-graph-div');
                Plotly.relayout(plotDiv, {
                    'xaxis.range': [start, end]
                });
            }
        }
        
        // Function to reset to full range
        function resetPlotDateRange() {
            const plotDiv = document.querySelector('.plotly-graph-div');
            Plotly.relayout(plotDiv, {
                'xaxis.autorange': true
            });
        }
        
        // Event listeners
        document.getElementById('custom-apply-dates').addEventListener('click', updatePlotDateRange);
        document.getElementById('custom-reset-dates').addEventListener('click', resetPlotDateRange);
        
        // Also apply on Enter key in date inputs
        document.getElementById('custom-start-date').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') updatePlotDateRange();
        });
        document.getElementById('custom-end-date').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') updatePlotDateRange();
        });
    </script>
    """
    
    # Generate HTML with rounded corners
    html_content = fig.to_html(full_html=True, include_plotlyjs='cdn', config={'responsive': True})
    
    # Add custom CSS for rounded corners
    custom_css = """
    <style>
        .plot-container {
            border-radius: 15px !important;
            overflow: hidden !important;
            box-shadow: 0 0 10px rgba(0,0,0,0.1) !important;
            position: relative;
        }
        .plotly-graph-div {
            width: 100% !important;
            height: 100% !important;
            border-radius: 15px !important;
        }
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
        }
    </style>
    """
    
    # Inject our custom CSS and date selector
    html_content = html_content.replace('<head>', '<head>' + custom_css)
    html_content = html_content.replace('<div id="', '<div class="plot-container"><div id="')
    html_content = html_content.replace('</body>', date_selector_html + '</div></body>')
    
    # Write the modified HTML to file
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Daily radiative power visualization saved to: {output_file}")


#TEIDE VISUALIZATION

def load_netcdf_data_TEIDE():
    """Load and process netCDF data with fallback"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Try multiple possible paths
        possible_paths = [
            os.path.join(base_dir, "A00_data", "B_processed", "Teide", "Radiative_Power_by_Year_Month_Day", "radiative_power_teide.nc"),
            os.path.join(base_dir, "A00_data", "B_raw", "radiative_power_teide.nc"),
            os.path.join(base_dir, "A00_data", "radiative_power_teide.nc")
        ]
        
        for nc_path in possible_paths:
            if os.path.exists(nc_path):
                print(f"Found netCDF file at: {nc_path}")
                ds = xr.open_dataset(nc_path)
                df = ds.to_dataframe().reset_index()
                
                # Check available columns
                available_cols = df.columns.tolist()
                print("Available columns in netCDF:", available_cols)
                
                # Prepare result DataFrame
                result = pd.DataFrame({
                    'Date': pd.to_datetime(df['time']),
                    'Radiative_Power': df['FRP'] if 'FRP' in df else df['radiative_power'] if 'radiative_power' in df else df.iloc[:, 1]
                }).dropna()
                
                return result
        
        print("No netCDF file found in any of the searched locations")
        return None
    
    except Exception as e:
        print(f"\nError loading netCDF data: {str(e)}")
        return None

def generate_netcdf_visualization_teide(df, output_file):
    """Generate interactive visualization for netCDF data with eruption period"""
    if df is None or df.empty:
        print("No data available for visualization")
        return
    
    # Create figure using plotly express for consistent styling
    fig = px.scatter(df, 
                    x='Date', 
                    y='Radiative_Power',
                    title='<b>Daily Radiative Power</b><br><sup>Fumarolic activity at Mount Teide (2021-Present)</sup>',
                    template='plotly_white',
                    labels={
                        'Date': 'Date',
                        'Radiative_Power': 'Radiative Power (MW)'
                    },
                    hover_data={'Date': '|%d/%m/%Y'},
                    opacity=0.7,
                    size_max=10)
    
    # Customize markers to match weekly plot
    fig.update_traces(
        marker=dict(
            size=8,
            color='#3498DB',
            symbol='circle',
            line=dict(width=1, color='#413224'),
            opacity=0.8,
            sizemode='diameter'
        ),
        selector=dict(mode='markers'),
        name='Radiative Power',
        showlegend=True
    )
    
    # Add maximum value annotation
    max_power = df['Radiative_Power'].max()
    max_date = df.loc[df['Radiative_Power'].idxmax(), 'Date']
    fig.add_annotation(
        x=max_date,
        y=max_power,
        text=f"Maximum: {max_power:.0f} MW",
        showarrow=True,
        arrowhead=1,
        ax=-200,
        ay=10,
        font=dict(size=12, color="#E74C3C"),
        bordercolor="#413224",
        borderwidth=1,
        borderpad=4,
        bgcolor="white"
    )
    
    # Update layout to match weekly plot
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date",
            title_text='Date',
            gridcolor='#f0f0f0'
        ),
        yaxis=dict(
            title_text='Radiative Power (MW)',
            gridcolor='#f0f0f0'
        ),
        hovermode="x unified",
        plot_bgcolor='white',
        margin=dict(l=50, r=50, b=80, t=100),
        title_x=0.5,
        title_font=dict(size=20),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1,
            font=dict(size=12),
            itemclick=False,
            itemdoubleclick=False
        )
    )
    
    # Add custom date range selector
    date_selector_html = """
    <div class="date-selector-container">
        <style>
            .date-selector-container {
                position: absolute;
                top: 70px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 1000;
                background: rgba(255,255,255,0.9);
                padding: 8px 15px;
                border-radius: 20px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                font-family: Arial, sans-serif;
                display: flex;
                align-items: center;
                gap: 10px;
                border: 1px solid #ddd;
            }
            .date-selector-container label {
                font-weight: bold;
                font-size: 12px;
                white-space: nowrap;
            }
            .date-selector-container input {
                padding: 5px;
                width: 120px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
            .date-selector-container button {
                padding: 5px 12px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                white-space: nowrap;
                transition: background-color 0.3s;
            }
            .date-selector-container button:hover {
                background-color: #45a049;
            }
            .date-selector-container button.reset-btn {
                background-color: #f44336;
            }
            .date-selector-container button.reset-btn:hover {
                background-color: #d32f2f;
            }
        </style>
        <label>From:</label>
        <input type="date" id="custom-start-date">
        <label>To:</label>
        <input type="date" id="custom-end-date">
        <button id="custom-apply-dates">Apply</button>
        <button id="custom-reset-dates" class="reset-btn">Reset</button>
    </div>
    <script>
        // Set default dates (last 180 days)
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - 180);
        
        document.getElementById('custom-start-date').valueAsDate = startDate;
        document.getElementById('custom-end-date').valueAsDate = endDate;
        
        // Function to update the plot
        function updatePlotDateRange() {
            const start = document.getElementById('custom-start-date').value;
            const end = document.getElementById('custom-end-date').value;
            
            if (start && end) {
                const plotDiv = document.querySelector('.plotly-graph-div');
                Plotly.relayout(plotDiv, {
                    'xaxis.range': [start, end]
                });
            }
        }
        
        // Function to reset to full range
        function resetPlotDateRange() {
            const plotDiv = document.querySelector('.plotly-graph-div');
            Plotly.relayout(plotDiv, {
                'xaxis.autorange': true
            });
        }
        
        // Event listeners
        document.getElementById('custom-apply-dates').addEventListener('click', updatePlotDateRange);
        document.getElementById('custom-reset-dates').addEventListener('click', resetPlotDateRange);
        
        // Also apply on Enter key in date inputs
        document.getElementById('custom-start-date').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') updatePlotDateRange();
        });
        document.getElementById('custom-end-date').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') updatePlotDateRange();
        });
    </script>
    """
    
    # Generate HTML with rounded corners
    html_content = fig.to_html(full_html=True, include_plotlyjs='cdn', config={'responsive': True})
    
    # Add custom CSS for rounded corners
    custom_css = """
    <style>
        .plot-container {
            border-radius: 15px !important;
            overflow: hidden !important;
            box-shadow: 0 0 10px rgba(0,0,0,0.1) !important;
            position: relative;
        }
        .plotly-graph-div {
            width: 100% !important;
            height: 100% !important;
            border-radius: 15px !important;
        }
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
        }
    </style>
    """
    
    # Inject our custom CSS and date selector
    html_content = html_content.replace('<head>', '<head>' + custom_css)
    html_content = html_content.replace('<div id="', '<div class="plot-container"><div id="')
    html_content = html_content.replace('</body>', date_selector_html + '</div></body>')
    
    # Write the modified HTML to file
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Daily radiative power visualization saved to: {output_file}")


#LANZAROTE VISUALIZATION

def load_netcdf_data_lanzarote():
    """Load and process netCDF data with fallback"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Try multiple possible paths
        possible_paths = [
            os.path.join(base_dir, "A00_data", "B_processed", "Lanzarote", "Radiative_Power_by_Year_Month_Day", "radiative_power_lanzarote.nc"),
            os.path.join(base_dir, "A00_data", "B_raw", "radiative_power_lanzarote.nc"),
            os.path.join(base_dir, "A00_data", "radiative_power_lanzarote.nc")
        ]
        
        for nc_path in possible_paths:
            if os.path.exists(nc_path):
                print(f"Found netCDF file at: {nc_path}")
                ds = xr.open_dataset(nc_path)
                df = ds.to_dataframe().reset_index()
                
                # Check available columns
                available_cols = df.columns.tolist()
                print("Available columns in netCDF:", available_cols)
                
                # Prepare result DataFrame
                result = pd.DataFrame({
                    'Date': pd.to_datetime(df['time']),
                    'Radiative_Power': df['FRP'] if 'FRP' in df else df['radiative_power'] if 'radiative_power' in df else df.iloc[:, 1]
                }).dropna()
                
                return result
        
        print("No netCDF file found in any of the searched locations")
        return None
    
    except Exception as e:
        print(f"\nError loading netCDF data: {str(e)}")
        return None

def generate_netcdf_visualization_lanzarote(df, output_file):
    """Generate interactive visualization for netCDF data with eruption period"""
    if df is None or df.empty:
        print("No data available for visualization")
        return
    
    # Create figure using plotly express for consistent styling
    fig = px.scatter(df, 
                    x='Date', 
                    y='Radiative_Power',
                    title='<b>Daily Radiative Power</b><br><sup>Fumarolic activity at Mount Timanfaya (2025-Present)</sup>',
                    template='plotly_white',
                    labels={
                        'Date': 'Date',
                        'Radiative_Power': 'Radiative Power (MW)'
                    },
                    hover_data={'Date': '|%d/%m/%Y'},
                    opacity=0.7,
                    size_max=10)
    
    # Customize markers to match weekly plot
    fig.update_traces(
        marker=dict(
            size=8,
            color='#3498DB',
            symbol='circle',
            line=dict(width=1, color='#413224'),
            opacity=0.8,
            sizemode='diameter'
        ),
        selector=dict(mode='markers'),
        name='Radiative Power',
        showlegend=True
    )
    
    # Add maximum value annotation
    max_power = df['Radiative_Power'].max()
    max_date = df.loc[df['Radiative_Power'].idxmax(), 'Date']
    fig.add_annotation(
        x=max_date,
        y=max_power,
        text=f"Maximum: {max_power:.0f} MW",
        showarrow=True,
        arrowhead=1,
        ax=-200,
        ay=10,
        font=dict(size=12, color="#E74C3C"),
        bordercolor="#413224",
        borderwidth=1,
        borderpad=4,
        bgcolor="white"
    )
    
    # Update layout to match weekly plot
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date",
            title_text='Date',
            gridcolor='#f0f0f0'
        ),
        yaxis=dict(
            title_text='Radiative Power (MW)',
            gridcolor='#f0f0f0'
        ),
        hovermode="x unified",
        plot_bgcolor='white',
        margin=dict(l=50, r=50, b=80, t=100),
        title_x=0.5,
        title_font=dict(size=20),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1,
            font=dict(size=12),
            itemclick=False,
            itemdoubleclick=False
        )
    )
    
    # Add custom date range selector
    date_selector_html = """
    <div class="date-selector-container">
        <style>
            .date-selector-container {
                position: absolute;
                top: 70px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 1000;
                background: rgba(255,255,255,0.9);
                padding: 8px 15px;
                border-radius: 20px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                font-family: Arial, sans-serif;
                display: flex;
                align-items: center;
                gap: 10px;
                border: 1px solid #ddd;
            }
            .date-selector-container label {
                font-weight: bold;
                font-size: 12px;
                white-space: nowrap;
            }
            .date-selector-container input {
                padding: 5px;
                width: 120px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
            .date-selector-container button {
                padding: 5px 12px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                white-space: nowrap;
                transition: background-color 0.3s;
            }
            .date-selector-container button:hover {
                background-color: #45a049;
            }
            .date-selector-container button.reset-btn {
                background-color: #f44336;
            }
            .date-selector-container button.reset-btn:hover {
                background-color: #d32f2f;
            }
        </style>
        <label>From:</label>
        <input type="date" id="custom-start-date">
        <label>To:</label>
        <input type="date" id="custom-end-date">
        <button id="custom-apply-dates">Apply</button>
        <button id="custom-reset-dates" class="reset-btn">Reset</button>
    </div>
    <script>
        // Set default dates (last 180 days)
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - 180);
        
        document.getElementById('custom-start-date').valueAsDate = startDate;
        document.getElementById('custom-end-date').valueAsDate = endDate;
        
        // Function to update the plot
        function updatePlotDateRange() {
            const start = document.getElementById('custom-start-date').value;
            const end = document.getElementById('custom-end-date').value;
            
            if (start && end) {
                const plotDiv = document.querySelector('.plotly-graph-div');
                Plotly.relayout(plotDiv, {
                    'xaxis.range': [start, end]
                });
            }
        }
        
        // Function to reset to full range
        function resetPlotDateRange() {
            const plotDiv = document.querySelector('.plotly-graph-div');
            Plotly.relayout(plotDiv, {
                'xaxis.autorange': true
            });
        }
        
        // Event listeners
        document.getElementById('custom-apply-dates').addEventListener('click', updatePlotDateRange);
        document.getElementById('custom-reset-dates').addEventListener('click', resetPlotDateRange);
        
        // Also apply on Enter key in date inputs
        document.getElementById('custom-start-date').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') updatePlotDateRange();
        });
        document.getElementById('custom-end-date').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') updatePlotDateRange();
        });
    </script>
    """
    
    # Generate HTML with rounded corners
    html_content = fig.to_html(full_html=True, include_plotlyjs='cdn', config={'responsive': True})
    
    # Add custom CSS for rounded corners
    custom_css = """
    <style>
        .plot-container {
            border-radius: 15px !important;
            overflow: hidden !important;
            box-shadow: 0 0 10px rgba(0,0,0,0.1) !important;
            position: relative;
        }
        .plotly-graph-div {
            width: 100% !important;
            height: 100% !important;
            border-radius: 15px !important;
        }
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
        }
    </style>
    """
    
    # Inject our custom CSS and date selector
    html_content = html_content.replace('<head>', '<head>' + custom_css)
    html_content = html_content.replace('<div id="', '<div class="plot-container"><div id="')
    html_content = html_content.replace('</body>', date_selector_html + '</div></body>')
    
    # Write the modified HTML to file
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Daily radiative power visualization saved to: {output_file}")


#MAPS

def generate_eruption_map(output_file):
    """Generate interactive eruption map focused on La Palma"""
    # Load lava perimeter data
    lava_coords = load_lava_perimeter()
    
    # Create figure
    fig = go.Figure()
    
    # Ajusta el zoom y centro para mostrar solo La Palma
    initial_zoom = 9  # Zoom más cercano que antes (6.5)
    initial_center = dict(lat=28.65, lon=-17.85)  # Coordenadas ajustadas para centrar mejor La Palma
    
    lava_zoom = 12  # Zoom para vista detallada del flujo de lava
    lava_center = dict(lat=28.613, lon=-17.9)  # Coordenadas del volcán Tajogaite
    
    # MAIN VOLCANO MARKER
    fig.add_trace(go.Scattermapbox(
        mode="markers+text",
        lon=[-17.873],
        lat=[28.613],
        marker=dict(
            size=12,
            color='red',
            symbol='circle',
            opacity=0.8,
        ),
        text=["Tajogaite"],
        textposition="top right",
        hoverinfo="text",
        name="Volcano Location",
        textfont=dict(size=10, color='black')
    ))
    
    # Lava perimeter trace with filled area (initially hidden)
    fig.add_trace(go.Scattermapbox(
        mode="lines",
        lon=np.append(lava_coords[:,0], lava_coords[0,0]),
        lat=np.append(lava_coords[:,1], lava_coords[0,1]),
        fill='toself',
        fillcolor=FILL_COLOR,
        line=dict(color=OUTLINE_COLOR, width=2),
        name="Lava Flow Area",
        visible=False,
        hoverinfo="none"
    ))
    
    # Map layout configuration
    fig.update_layout(
        mapbox=dict(
            style=MAPBOX_STYLE,
            center=initial_center,
            zoom=initial_zoom,
            layers=[],
            bounds=dict(
                west=-19.0,
                east=-13.0,
                south=27.6,
                north=29.5
            )
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.02,
                y=0.98,
                xanchor="left",
                yanchor="top",
                pad=dict(t=5, b=5, l=10, r=10),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#cccccc",
                borderwidth=1,
                font=dict(size=12, family="Arial", color="black"),
                buttons=[
                    dict(
                        label="General View",
                        method="relayout",
                        args=[{
                            "mapbox.center": initial_center, 
                            "mapbox.zoom": initial_zoom,
                            "mapbox.bounds": dict(
                                west=-19.0,
                                east=-13.0,
                                south=27.6,
                                north=29.5
                            )
                        }]
                    ),
                    dict(
                        label="Lava View",
                        method="update",
                        args=[{"visible": [True, "!visible"]},
                              {"mapbox.center": lava_center, "mapbox.zoom": lava_zoom}],
                        args2=[{"visible": [True, False]},
                              {"mapbox.center": lava_center, "mapbox.zoom": lava_zoom}]
                    )
                ]
            )
        ]
    )
    
    # Generate HTML with improved CSS for buttons
    html_content = fig.to_html(full_html=True, include_plotlyjs='cdn', config={'responsive': True})
    
    # CSS mejorado para los botones
    custom_css = """
    <style>
        .plot-container {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            position: relative;
            width: 100%;
            height: 100%;
        }
        .plotly-graph-div {
            width: 100% !important;
            height: 100% !important;
        }
        .updatemenu {
            position: absolute !important;
            left: 10px !important;
            top: 10px !important;
            z-index: 1000 !important;
        }
        .updatemenu .btn {
            min-width: 140px !important;
            padding: 12px 15px !important;
            font-size: 14px !important;
            margin: 6px 0 !important;
            background-color: rgba(255,255,255,0.95) !important;
            border: 2px solid #cccccc !important;
            border-radius: 6px !important;
            color: black !important;
            height: auto !important;
            line-height: 1.2 !important;
            white-space: nowrap !important;
            text-align: center !important;
            font-weight: bold !important;
        }
        .updatemenu .btn-group {
            display: flex !important;
            flex-direction: column !important;
            gap: 8px !important;
        }
        .updatemenu .btn:hover {
            background-color: #f0f0f0 !important;
            transform: scale(1.02) !important;
        }
        .updatemenu .btn.active {
            background-color: #e0e0e0 !important;
            box-shadow: inset 0 0 5px rgba(0,0,0,0.2) !important;
        }
        .updatemenu-container {
            pointer-events: none !important;
        }
        .updatemenu-container * {
            pointer-events: auto !important;
        }
    </style>
    """
    
    # Inject our custom CSS
    html_content = html_content.replace('<head>', '<head>' + custom_css)
    html_content = html_content.replace('<div id="', '<div class="plot-container"><div id="')
    html_content = html_content.replace('</body>', '</div></body>')
    
    # Write the modified HTML to file
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Map generated successfully: {output_file}")



def generate_lanzarote_map(output_file):
    # Coordenadas del Teide (fumarola)
    lanzarote_lat, lanzarote_lon = 29.0036, -13.7310

    fig = go.Figure()

    # Vista general y cráter
    general_view = dict(lat=29.0036, lon=-13.7310, zoom=9)
    crater_view = dict(lat=lanzarote_lat, lon=lanzarote_lon, zoom=13)

    # Punto rojo para la fumarola
    fig.add_trace(go.Scattermapbox(
        mode="markers+text",
        lon=[lanzarote_lon],
        lat=[lanzarote_lat],
        marker=dict(
            size=16,
            color='red',
            symbol='circle',
            opacity=0.9
        ),
        text=["Fumarole"],
        textposition="top right",
        hoverinfo="text",
        name="Fumarole Location",
        textfont=dict(size=12, color='black')
    ))

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=general_view['lat'], lon=general_view['lon']),
            zoom=general_view['zoom']
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.02,
                y=0.98,
                xanchor="left",
                yanchor="top",
                pad=dict(t=5, b=5, l=10, r=10),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#cccccc",
                borderwidth=1,
                font=dict(size=12),
                buttons=[
                    dict(
                        label="General View",
                        method="relayout",
                        args=[{"mapbox.center": dict(lat=general_view['lat'], lon=general_view['lon']),
                               "mapbox.zoom": general_view['zoom']}]
                    ),
                    dict(
                        label="Crater View",
                        method="relayout",
                        args=[{"mapbox.center": dict(lat=crater_view['lat'], lon=crater_view['lon']),
                               "mapbox.zoom": crater_view['zoom']}]
                    )
                ]
            )
        ]
    )

    # CSS para bordes redondeados
    custom_css = """
    <style>
        .plot-container {
            border-radius: 15px !important;
            overflow: hidden !important;
            box-shadow: 0 0 10px rgba(0,0,0,0.1) !important;
            position: relative;
        }
        .plotly-graph-div {
            width: 100% !important;
            height: 100% !important;
            border-radius: 15px !important;
        }
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
        }
    </style>
    """

    # HTML con CSS
    html_content = fig.to_html(full_html=True, include_plotlyjs='cdn', config={'responsive': True})
    html_content = html_content.replace('<head>', '<head>' + custom_css)
    html_content = html_content.replace('<div id="', '<div class="plot-container"><div id="')
    html_content = html_content.replace('</body>', '</div></body>')

    # Guardar archivo
    with open(output_file, 'w') as f:
        f.write(html_content)



def generate_teide_map(output_file):
    # Coordenadas del Teide (fumarola)
    teide_lat, teide_lon = 28.2724, -16.6425

    fig = go.Figure()

    # Vista general y cráter
    general_view = dict(lat=28.29, lon=-16.59, zoom=8.3)
    crater_view = dict(lat=teide_lat, lon=teide_lon, zoom=13)

    # Punto rojo para la fumarola
    fig.add_trace(go.Scattermapbox(
        mode="markers+text",
        lon=[teide_lon],
        lat=[teide_lat],
        marker=dict(
            size=16,
            color='red',
            symbol='circle',
            opacity=0.9
        ),
        text=["Fumarole"],
        textposition="top right",
        hoverinfo="text",
        name="Fumarole Location",
        textfont=dict(size=12, color='black')
    ))

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=general_view['lat'], lon=general_view['lon']),
            zoom=general_view['zoom']
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.02,
                y=0.98,
                xanchor="left",
                yanchor="top",
                pad=dict(t=5, b=5, l=10, r=10),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#cccccc",
                borderwidth=1,
                font=dict(size=12),
                buttons=[
                    dict(
                        label="General View",
                        method="relayout",
                        args=[{"mapbox.center": dict(lat=general_view['lat'], lon=general_view['lon']),
                               "mapbox.zoom": general_view['zoom']}]
                    ),
                    dict(
                        label="Crater View",
                        method="relayout",
                        args=[{"mapbox.center": dict(lat=crater_view['lat'], lon=crater_view['lon']),
                               "mapbox.zoom": crater_view['zoom']}]
                    )
                ]
            )
        ]
    )

    # CSS para bordes redondeados
    custom_css = """
    <style>
        .plot-container {
            border-radius: 15px !important;
            overflow: hidden !important;
            box-shadow: 0 0 10px rgba(0,0,0,0.1) !important;
            position: relative;
        }
        .plotly-graph-div {
            width: 100% !important;
            height: 100% !important;
            border-radius: 15px !important;
        }
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
        }
    </style>
    """

    # HTML con CSS
    html_content = fig.to_html(full_html=True, include_plotlyjs='cdn', config={'responsive': True})
    html_content = html_content.replace('<head>', '<head>' + custom_css)
    html_content = html_content.replace('<div id="', '<div class="plot-container"><div id="')
    html_content = html_content.replace('</body>', '</div></body>')

    # Guardar archivo
    with open(output_file, 'w') as f:
        f.write(html_content)




def generate_radiative_power_plot(df, output_file):
    """Generate the radiative power scatter plot with eruption period highlighted"""
    fig = px.scatter(df, 
                    x='DateTime', 
                    y='Radiative_Power',
                    title='<b>Weekly Radiative Power</b><br><sup>Tajogaite Volcano (2021-2024) - Red background shows eruption period</sup>',
                    template='plotly_white',
                    labels={
                        'DateTime': 'Date',
                        'Radiative_Power': 'Radiative Power (MW)'
                    },
                    hover_data={'DateTime': '|%d/%m/%Y'},
                    opacity=0.7,
                    size_max=10)
    
    # Add eruption period background
    fig.add_vrect(
        x0=ERUPTION_START, 
        x1=ERUPTION_END,
        fillcolor=ERUPTION_COLOR,
        opacity=0.5,
        layer="below",
        line_width=0,
        annotation_text="Eruption Period",
        annotation_position="bottom left",
        annotation_font_size=12,
        annotation_font_color="red"
    )
    
    # Customize markers and legend
    fig.update_traces(
        marker=dict(
            size=8,
            color='#3498DB',
            symbol='circle',
            line=dict(width=1, color='#413224'),
            opacity=0.8,
            sizemode='diameter'
        ),
        selector=dict(mode='markers'),
        name='Radiative Power',  # This sets the legend name
        showlegend=True  # Ensure it shows in legend
    )

    # Customize layout with proper legend settings
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date",
            title_text='Date',
            gridcolor='#f0f0f0'
        ),
        yaxis=dict(
            title_text='Radiative Power (MW)',
            gridcolor='#f0f0f0'
        ),
        hovermode="x unified",
        plot_bgcolor='white',
        margin=dict(l=50, r=50, b=80, t=100),
        title_x=0.5,
        title_font=dict(size=20),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1,
            font=dict(size=12),
            itemclick=False,
            itemdoubleclick=False
        )
    )

    # Add maximum value annotation
    max_power = df['Radiative_Power'].max()
    max_date = df.loc[df['Radiative_Power'].idxmax(), 'DateTime']
    fig.add_annotation(
        x=max_date,
        y=max_power,
        text=f"Maximum: {max_power:.0f} MW",
        showarrow=True,
        arrowhead=1,
        ax=-50,
        ay=-40,
        font=dict(size=12, color="#E74C3C"),
        bordercolor="#413224",
        borderwidth=1,
        borderpad=4,
        bgcolor="white"
    )
    
    # Save the figure
    fig.write_html(output_file)
    print(f"Radiative power plot saved to: {output_file}")
    # Add custom date range selector
    date_selector_html = """
    <div class="date-selector-container">
        <style>
            .date-selector-container {
                position: absolute;
                top: 70px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 1000;
                background: rgba(255,255,255,0.9);
                padding: 8px 15px;
                border-radius: 20px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                font-family: Arial, sans-serif;
                display: flex;
                align-items: center;
                gap: 10px;
                border: 1px solid #ddd;
            }
            .date-selector-container label {
                font-weight: bold;
                font-size: 12px;
                white-space: nowrap;
            }
            .date-selector-container input {
                padding: 5px;
                width: 120px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
            .date-selector-container button {
                padding: 5px 12px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                white-space: nowrap;
                transition: background-color 0.3s;
            }
            .date-selector-container button:hover {
                background-color: #45a049;
            }
            .date-selector-container button.reset-btn {
                background-color: #f44336;
            }
            .date-selector-container button.reset-btn:hover {
                background-color: #d32f2f;
            }
        </style>
        <label>From:</label>
        <input type="date" id="custom-start-date">
        <label>To:</label>
        <input type="date" id="custom-end-date">
        <button id="custom-apply-dates">Apply</button>
        <button id="custom-reset-dates" class="reset-btn">Reset</button>
    </div>
    <script>
        // Set default dates (last 180 days)
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - 180);
        
        document.getElementById('custom-start-date').valueAsDate = startDate;
        document.getElementById('custom-end-date').valueAsDate = endDate;
        
        // Function to update the plot
        function updatePlotDateRange() {
            const start = document.getElementById('custom-start-date').value;
            const end = document.getElementById('custom-end-date').value;
            
            if (start && end) {
                const plotDiv = document.querySelector('.plotly-graph-div');
                Plotly.relayout(plotDiv, {
                    'xaxis.range': [start, end]
                });
            }
        }
        
        // Function to reset to full range
        function resetPlotDateRange() {
            const plotDiv = document.querySelector('.plotly-graph-div');
            Plotly.relayout(plotDiv, {
                'xaxis.autorange': true
            });
        }
        
        // Event listeners
        document.getElementById('custom-apply-dates').addEventListener('click', updatePlotDateRange);
        document.getElementById('custom-reset-dates').addEventListener('click', resetPlotDateRange);
        
        // Also apply on Enter key in date inputs
        document.getElementById('custom-start-date').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') updatePlotDateRange();
        });
        document.getElementById('custom-end-date').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') updatePlotDateRange();
        });
    </script>
    """
    
    # Generate HTML with rounded corners
    html_content = fig.to_html(full_html=True, include_plotlyjs='cdn', config={'responsive': True})
    
    # Add custom CSS for rounded corners
    custom_css = """
    <style>
        .plot-container {
            border-radius: 15px !important;
            overflow: hidden !important;
            box-shadow: 0 0 10px rgba(0,0,0,0.1) !important;
            position: relative;
        }
        .plotly-graph-div {
            width: 100% !important;
            height: 100% !important;
            border-radius: 15px !important;
        }
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
        }
    </style>
    """
    
    # Inject our custom CSS and date selector
    html_content = html_content.replace('<head>', '<head>' + custom_css)
    html_content = html_content.replace('<div id="', '<div class="plot-container"><div id="')
    html_content = html_content.replace('</body>', date_selector_html + '</div></body>')
    
    # Write the modified HTML to file
    with open(output_file, 'w') as f:
        f.write(html_content)

def load_radiative_data():
    """Load and prepare radiative power data"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "A00_data", "B_raw", "TIRVolcH_La_Palma_Dataset.xlsx")
        
        df = pd.read_excel(data_path, sheet_name='LaPalma_TIRVolcH_Filtered_Data')
        df = df[['Date', 'Weekly_Max_VRP_TIR (MW)']].dropna()
        df = df.rename(columns={
            'Date': 'DateTime',
            'Weekly_Max_VRP_TIR (MW)': 'Radiative_Power'
        })
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        return df.sort_values('DateTime')
    
    except Exception as e:
        print(f"Error loading radiative data: {str(e)}")
        return None

def main():
    try:
        # Configure output path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, "A04_web", "B_images")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate eruption map focused on La Palma
        map_file = os.path.join(output_dir, "la_palma_eruption_viewer.html")
        generate_eruption_map(map_file)

        # Generate eruption map focused on TEIDE
        map_file_teide = os.path.join(output_dir, "teide_map.html")
        generate_teide_map(map_file_teide)

        # Generate eruption map focused on TEIDE
        map_file_lanzarote = os.path.join(output_dir, "lanzarote_map.html")
        generate_lanzarote_map(map_file_lanzarote)
        
        # Generate netCDF visualization
        nc_data = load_netcdf_data()
        if nc_data is not None:
            nc_file = os.path.join(output_dir, "radiative_power_daily.html")
            generate_netcdf_visualization(nc_data, nc_file)

        nc_data_teide = load_netcdf_data_TEIDE()
        if nc_data_teide is not None:
            nc_file_teide = os.path.join(output_dir, "radiative_power_teide_daily.html")
            generate_netcdf_visualization_teide(nc_data_teide, nc_file_teide)
        
        nc_data_lanzarote = load_netcdf_data_lanzarote()
        if nc_data_lanzarote is not None:
            nc_file_lanzarote = os.path.join(output_dir, "radiative_power_lanzarote_daily.html")
            generate_netcdf_visualization_lanzarote(nc_data_lanzarote, nc_file_lanzarote)
        
        # Generate radiative power plot
        df = load_radiative_data()
        if df is not None:
            plot_file = os.path.join(output_dir, "radiative_power_plot.html")
            generate_radiative_power_plot(df, plot_file)
            print(f"Radiative power plot generated: {plot_file}")
        
        print("\nAll visualizations generated successfully in:")
        print(f"- Eruption map: {map_file}")
        if nc_data is not None:
            print(f"- Daily radiative power: {nc_file}")
        if nc_data_teide is not None:
            print(f"- Daily radiative power Teide: {nc_file_teide}")
        if nc_data_lanzarote is not None:
            print(f"- Daily radiative power Lanzarote: {nc_file_lanzarote}")
        if df is not None:
            print(f"- Weekly radiative power plot: {plot_file}")
        
        return True
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

