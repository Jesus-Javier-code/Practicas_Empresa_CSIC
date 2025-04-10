import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import json
import os
import sys


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
    """Generate interactive eruption map focused on La Palma"""
    # Load lava perimeter data
    lava_coords = load_lava_perimeter()
    
    # Create figure
    fig = go.Figure()
    
    # Zoom level and center adjusted for the whole Canary Islands
    initial_zoom = 5  # Zoom out further to show the entire Canary Islands
    initial_center = dict(lat=28.5, lon=-15.6)  # Centered on the Canary Islands
    lava_zoom = 12  # Zoom level for the lava view
    lava_center = dict(lat=28.613, lon=-17.873)  # Centered on the lava area
    
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
        visible=False,  # Initially hidden
        hoverinfo="none"
    ))
    
    # Map layout configuration
    fig.update_layout(
        mapbox=dict(
            style=MAPBOX_STYLE,
            center=initial_center,
            zoom=initial_zoom,
            layers=[],
            # Set bounds to keep view focused on Canary Islands
            bounds=dict(
                west=-18.5,  # Westernmost point
                east=-13.5,  # Easternmost point
                south=27.5,  # Southernmost point
                north=29.5   # Northernmost point
            )
        ),
        margin=dict(l=0, r=0, t=0, b=0),  # No margins
        showlegend=False,
        updatemenus=[  # Menu for buttons
            dict(
                type="buttons",
                direction="right",
                x=0.02,  # Positioned at left side
                y=0.98,  # Positioned at top
                xanchor="left",
                yanchor="top",
                pad=dict(t=5, b=5, l=10, r=10),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#cccccc",
                borderwidth=1,
                font=dict(size=12, family="Arial"),
                buttons=[
                    dict(
                        label="Normal View",
                        method="relayout",
                        args=[{
                            "mapbox.center": initial_center, 
                            "mapbox.zoom": initial_zoom,
                            "mapbox.bounds": dict(
                                west=-18.5,
                                east=-13.5,
                                south=27.5,
                                north=29.5
                            )
                        }]
                    ),
                    dict(
                        label="Lava View",
                        method="update",
                        args=[{"visible": [True, "!visible"]},  # Toggle lava visibility
                              {"mapbox.center": lava_center, "mapbox.zoom": lava_zoom}],
                        args2=[{"visible": [True, False]},  # Second click hides lava but keeps zoom
                              {"mapbox.center": lava_center, "mapbox.zoom": lava_zoom}]
                    )
                ]
            )
        ]
    )
    
    # Generate HTML with rounded corners
    html_content = fig.to_html(full_html=True, include_plotlyjs='cdn', config={'responsive': True})
    
    # Add custom CSS for rounded corners and fixed buttons
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
            min-width: 100px !important;
            padding: 5px 10px !important;
            font-size: 12px !important;
            margin: 2px !important;
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


def generate_radiative_power_plot(df, output_file):
    """Generate the radiative power scatter plot with rounded corners"""
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
            size=8,
            color='#E74C3C',
            symbol='circle',
            line=dict(width=1, color='#413224'),
            opacity=0.8,
            sizemode='diameter'
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

    # Generate HTML with rounded corners
    html_content = fig.to_html(full_html=True, include_plotlyjs='cdn', config={'responsive': True})
    
    # Add custom CSS for rounded corners
    custom_css = """
    <style>
        .plot-container {
            border-radius: 15px !important;
            overflow: hidden !important;
            box-shadow: 0 0 10px rgba(0,0,0,0.1) !important;
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
    
    # Inject our custom CSS
    html_content = html_content.replace('<head>', '<head>' + custom_css)
    html_content = html_content.replace('<div id="', '<div class="plot-container"><div id="')
    html_content = html_content.replace('</body>', '</div></body>')
    
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

