# geometry_2.py - Version with points instead of lines
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import sys
from datetime import datetime

def generate_radiative_power_plot(df, output_file):
    """Generate the radiative power scatter plot"""
    fig = px.scatter(df, 
                    x='DateTime', 
                    y='Radiative_Power',
                    title='<b>Weekly Maximum Radiative Power</b><br><sup>La Palma Volcano (2021-2024) - Point Data</sup>',
                    template='plotly_white',
                    labels={
                        'DateTime': 'Date',
                        'Radiative_Power': 'Radiative Power (MW)'
                    },
                    hover_data={'DateTime': '|%B %d, %Y'},
                    opacity=0.7,
                    size_max=10)
    
    # Customize markers
    fig.update_traces(
        marker=dict(
            size=6,
            color='#413224',
            line=dict(width=1, color='DarkSlateGrey')
        ),
        selector=dict(mode='markers')
    )

    # Customize layout
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1 month", step="month", stepmode="backward"),
                    dict(count=6, label="6 months", step="month", stepmode="backward"),
                    dict(count=1, label="1 year", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ]),
                bgcolor='#f7f7f7'
            ),
            rangeslider=dict(visible=True),
            type="date",
            title_text='Date'
        ),
        yaxis=dict(
            title_text='Radiative Power (MW)',
            gridcolor='#f0f0f0'
        ),
        hovermode="x unified",
        plot_bgcolor='white',
        margin=dict(l=50, r=50, b=80, t=100),
        title_x=0.5,
        title_font=dict(size=20)
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
        font=dict(size=12, color="#E74C3C")
    )

    fig.write_html(output_file, include_plotlyjs='cdn')

def generate_3d_volcano_model(output_file):
    """Generate simplified 3D volcano model"""
    # Coordinates around Tajogaite volcano
    lat = np.linspace(28.55, 28.65, 100)
    lon = np.linspace(-17.9, -17.8, 100)
    lon_grid, lat_grid = np.meshgrid(lon, lat)
    
    # Base elevation (meters)
    base_elev = 700
    
    # Volcano cone simulation
    distance = np.sqrt((lat_grid-28.613)**2 + (lon_grid+17.873)**2)
    z = base_elev + 400 * np.exp(-distance/0.01)
    
    # Lava flows simulation
    lava1 = np.where((lat_grid > 28.60) & (lat_grid < 28.62) & (lon_grid > -17.88),
                    z - 50 + 20*np.random.rand(*z.shape), np.nan)
    
    lava2 = np.where((lat_grid > 28.59) & (lat_grid < 28.61) & (lon_grid > -17.87),
                    z - 30 + 15*np.random.rand(*z.shape), np.nan)

    fig = go.Figure()
    
    # Terrain
    fig.add_trace(go.Surface(
        z=z,
        x=lon_grid,
        y=lat_grid,
        colorscale='Viridis',
        name='Terrain',
        showscale=False,
        opacity=0.9
    ))
    
    # Lava flows
    fig.add_trace(go.Surface(
        z=lava1,
        x=lon_grid,
        y=lat_grid,
        colorscale='OrRd',
        name='Lava Flow 1',
        showscale=False,
        opacity=0.7
    ))
    
    fig.add_trace(go.Surface(
        z=lava2,
        x=lon_grid,
        y=lat_grid,
        colorscale='OrRd',
        name='Lava Flow 2',
        showscale=False,
        opacity=0.7
    ))

    fig.update_layout(
        title='<b>3D Simplified Model: Tajogaite Volcano</b><br>'
              '<sup>Approximate topography with simulated lava flows</sup>',
        scene=dict(
            xaxis_title='Longitude',
            yaxis_title='Latitude',
            zaxis_title='Elevation (m)',
            aspectratio=dict(x=1.5, y=1, z=0.3),
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8))
    )
    
    fig.write_html(output_file, include_plotlyjs='cdn')

def main():
    try:
        # Configure paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "00_data", "raw", "TIRVolcH_La_Palma_Dataset.xlsx")
        images_folder = os.path.join(base_dir, "04_web", "images")
        os.makedirs(images_folder, exist_ok=True)
        
        # 1. Generate radiative power plot
        df = pd.read_excel(data_path, sheet_name='LaPalma_TIRVolcH_Filtered_Data')
        df = df[['Date', 'Weekly_Max_VRP_TIR (MW)']].dropna()
        df = df.rename(columns={
            'Date': 'DateTime',
            'Weekly_Max_VRP_TIR (MW)': 'Radiative_Power'
        })
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        df = df.sort_values('DateTime')
        
        generate_radiative_power_plot(
            df, 
            os.path.join(images_folder, "radiative_power.html")
        )
        
        # 2. Generate simplified 3D model
        generate_3d_volcano_model(
            os.path.join(images_folder, "volcano_3d_model.html")
        )
        
        print(f"Visualizations generated in: {images_folder}")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)