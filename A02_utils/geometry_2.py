import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import json
import os
import sys
from shapely.geometry import Polygon, Point
from datetime import datetime

# Configuration
OUTLINE_COLOR = 'rgba(150, 0, 0, 1)'  # Dark red outline
FILL_COLOR = 'rgba(255, 50, 50, 0.5)'  # Semi-transparent red for lava area
MAPBOX_STYLE = "open-street-map"  # Base map style

def load_lava_perimeter():
    """Load lava flow perimeter from GeoJSON with absolute path"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        geojson_path = os.path.join(base_dir, "A00_data", "B_raw", "perimetro_dron_211123.geojson")
        
        with open(geojson_path) as f:
            data = json.load(f)
        
        return np.array(data['features'][0]['geometry']['coordinates'][0])
    
    except Exception:
        # Approximate coordinates of the main lava flow
        return np.array([
            [-17.8735, 28.6132], [-17.8730, 28.6130], [-17.8725, 28.6128],
            [-17.8720, 28.6125], [-17.8715, 28.6123], [-17.8710, 28.6120],
            [-17.8705, 28.6118], [-17.8700, 28.6115], [-17.8695, 28.6113],
            [-17.8690, 28.6110], [-17.8685, 28.6108], [-17.8680, 28.6105],
            [-17.8675, 28.6103], [-17.8670, 28.6100], [-17.8665, 28.6098],
            [-17.8660, 28.6095], [-17.8655, 28.6093], [-17.8650, 28.6090]
        ])

def generate_eruption_map(output_file):
    """Generate interactive eruption map with zoom controls"""
    # Load lava perimeter data
    lava_coords = load_lava_perimeter()
    
    # Create figure
    fig = go.Figure()
    
    # Initial view settings (zoomed out to show all Canary Islands)
    initial_zoom = 6
    initial_center = dict(lat=28.5, lon=-15.6)  # Centered on Canary Islands
    
    # MAIN VOLCANO MARKER (visible in all zoom levels)
    fig.add_trace(go.Scattermapbox(
        mode="markers+text",
        lon=[-17.873],
        lat=[28.613],
        marker=dict(
            size=12,
            color='red',
            symbol='circle',  # Usa este o 'circle'
            opacity=0.8,
        ),


        text=["Tajogaite"],
        textposition="top right",
        hoverinfo="text",
        name="Volcano Location",
        textfont=dict(size=10, color='black')
    ))  # <- Paréntesis cerrado correctamente aquí
    
    # DETAILED VOLCANO MARKER (only visible when zoomed in)
    fig.add_trace(go.Scattermapbox(
        mode="markers+text",
        lon=[-17.873],
        lat=[28.613],
        marker=dict(
            size=15,
            color='red',
            symbol='circle',
            opacity=1.0,
        ),
        text=["Tajogaite"],
        textposition="top right",
        hoverinfo="text",
        name="Volcano Location (detailed)",
        visible=False,
        textfont=dict(size=14, color='black')
    ))  # <- Paréntesis cerrado correctamente aquí
    
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
    ))  # Este paréntesis cierra el add_trace
    
    # Map layout configuration
    fig.update_layout(
        mapbox=dict(
            style=MAPBOX_STYLE,
            center=initial_center,
            zoom=initial_zoom,
            layers=[]
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        title_text="<b>La Palma Volcano Eruption Viewer</b>",
        title_x=0.5,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.5,
                y=1.15,
                showactive=True,
                buttons=list([
                    dict(
                        label="Hide Lava Area",
                        method="update",
                        args=[{"visible": [True, False, False]},
                             {"title": "La Palma - Normal View",
                              "mapbox.center": initial_center,
                              "mapbox.zoom": initial_zoom}]
                    ),
                    dict(
                        label="Show Lava Area",
                        method="update",
                        args=[{"visible": [False, True, True]},
                             {"title": "La Palma - Eruption Impact",
                              "mapbox.center": dict(lat=28.613, lon=-17.873),
                              "mapbox.zoom": 12}]
                    )
                ])
            )
        ]
    )  # Este paréntesis cierra update_layout
    
    # Save the file
    fig.write_html(output_file)
    print(f"Map generated successfully: {output_file}")


def generate_radiative_power_plot(df, output_file):
    """Generate the radiative power scatter plot"""
    fig = px.scatter(df, 
                    x='DateTime', 
                    y='Radiative_Power',
                    title='<b>Maximum Weekly Radiative Power</b><br><sup>La Palma Volcano (2021-2024)</sup>',
                    template='plotly_white',
                    labels={
                        'DateTime': 'Date',
                        'Radiative_Power': 'Radiative Power (MW)'
                    },
                    hover_data={'DateTime': '|%d/%m/%Y'},
                    opacity=0.7,
                    size_max=10)
    
    # Customize markers
    fig.update_traces(
        marker=dict(
            size=6,
            color='#E74C3C',  # Volcanic red
            line=dict(width=1, color='#413224')  # Brown border
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
        title_font=dict(size=20),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
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

    fig.write_html(output_file, include_plotlyjs='cdn')

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
        
        # Generate eruption map
        map_file = os.path.join(output_dir, "la_palma_eruption_viewer.html")
        generate_eruption_map(map_file)
        
        # Generate radiative power plot
        df = load_radiative_data()
        if df is not None:
            plot_file = os.path.join(output_dir, "radiative_power_plot.html")
            generate_radiative_power_plot(df, plot_file)
            print(f"Radiative power plot generated: {plot_file}")
        
        print("\nAll visualizations generated successfully in:")
        print(f"- Eruption map: {map_file}")
        if df is not None:
            print(f"- Radiative power plot: {plot_file}")
        
        return True
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)