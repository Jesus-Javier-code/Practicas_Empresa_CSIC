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
                    title='<b>Potencia Radiativa Semanal Máxima</b><br><sup>Volcán de La Palma (2021-2024)</sup>',
                    template='plotly_white',
                    labels={
                        'DateTime': 'Fecha',
                        'Radiative_Power': 'Potencia Radiativa (MW)'
                    },
                    hover_data={'DateTime': '|%d/%m/%Y'},
                    opacity=0.7,
                    size_max=10)
    
    # Customize markers
    fig.update_traces(
        marker=dict(
            size=6,
            color='#E74C3C',  # Rojo volcánico
            line=dict(width=1, color='#413224')  # Borde marrón
        ),
        selector=dict(mode='markers')
    )

    # Customize layout
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1 mes", step="month", stepmode="backward"),
                    dict(count=6, label="6 meses", step="month", stepmode="backward"),
                    dict(count=1, label="1 año", step="year", stepmode="backward"),
                    dict(step="all", label="Todo")
                ]),
                bgcolor='#f7f7f7'
            ),
            rangeslider=dict(visible=True),
            type="date",
            title_text='Fecha'
        ),
        yaxis=dict(
            title_text='Potencia Radiativa (MW)',
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
        text=f"Máximo: {max_power:.0f} MW",
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

def generate_3d_la_palma_model(output_file):
    """Generate 3D model of La Palma island"""
    # Coordinates for La Palma island (whole island)
    lat = np.linspace(28.40, 28.90, 200)  # Mayor resolución
    lon = np.linspace(-18.10, -17.60, 200)
    lon_grid, lat_grid = np.meshgrid(lon, lat)
    
    # Base elevation (sea level)
    base_elev = 0
    
    # Simulate the whole island topography
    # 1. Main ridge (Cumbre Vieja + Cumbre Nueva)
    ridge_dist = np.sqrt((lat_grid-28.58)**2 + (lon_grid+17.85)**2)
    z_ridge = 2400 * np.exp(-ridge_dist/0.04)  # Más alto y estrecho
    
    # 2. Caldera de Taburiente
    caldera_dist = np.sqrt((lat_grid-28.73)**2 + (lon_grid+17.88)**2)
    z_caldera = np.where(caldera_dist < 0.025, 
                        -800 * (1 - caldera_dist/0.025),  # Más profunda
                        0)
    
    # 3. Tajogaite volcano (2021 eruption)
    volcano_dist = np.sqrt((lat_grid-28.613)**2 + (lon_grid+17.873)**2)
    z_volcano = 600 * np.exp(-volcano_dist/0.003)  # Más pronunciado
    
    # Combine all elements
    z = base_elev + z_ridge + z_volcano + z_caldera
    
    # Lava flows simulation (2021 eruption) - Más precisión geográfica
    lava_mask = ((lat_grid > 28.60) & (lat_grid < 28.63) & 
                (lon_grid > -17.88) & (lon_grid < -17.82))
    lava_flow = np.where(lava_mask, z - 30 + 10*np.random.rand(*z.shape), np.nan)

    fig = go.Figure()
    
    # Island terrain with custom colorscale
    fig.add_trace(go.Surface(
        z=z,
        x=lon_grid,
        y=lat_grid,
        colorscale=[
            [0, 'rgb(12,51,131)'],    # Mar profundo
            [0.01, 'rgb(75,154,212)'], # Mar costero
            [0.02, 'rgb(237,248,217)'], # Playa
            [0.1, 'rgb(166,219,160)'],  # Vegetación baja
            [0.3, 'rgb(26,152,80)'],    # Vegetación media
            [0.6, 'rgb(102,60,20)'],    # Montaña baja
            [1.0, 'rgb(60,30,10)']      # Montaña alta
        ],
        name='Relieve',
        showscale=True,
        opacity=1,
        contours_z=dict(
            show=True, 
            width=3, 
            color='#413224',  # Color marrón
            highlightcolor="#E74C3C"  # Color rojo para resaltar
        )
    ))
    
    # Lava flows with better visualization
    if np.any(~np.isnan(lava_flow)):
        fig.add_trace(go.Surface(
            z=lava_flow,
            x=lon_grid,
            y=lat_grid,
            colorscale=[
                [0, 'rgb(250,50,10)'],  # Rojo intenso
                [1, 'rgb(150,20,5)']    # Rojo oscuro
            ],
            name='Coladas 2021',
            showscale=False,
            opacity=0.85,
            surfacecolor=np.ones_like(lava_flow)  # Color uniforme
        ))

    # Layout configuration
    fig.update_layout(
        title='<b>Modelo 3D de La Palma</b><br>'
              '<sup>Topografía completa con la erupción del Tajogaite</sup>',
        scene=dict(
            xaxis_title='Longitud Oeste',
            yaxis_title='Latitud Norte',
            zaxis_title='Elevación (m)',
            aspectratio=dict(x=1.8, y=1, z=0.25),  # Formato más panorámico
            camera=dict(
                eye=dict(x=1.8, y=1.8, z=0.7),  # Vista más aérea
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=-0.1)
            ),
            zaxis=dict(
                range=[-1000, 2500],  # Incluye la caldera
                nticks=10,
                backgroundcolor='rgb(200,230,255)'
            ),
            xaxis=dict(gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(gridcolor='rgba(0,0,0,0.1)')
        ),
        margin=dict(l=0, r=0, b=0, t=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.7)'
        ),
        coloraxis_colorbar=dict(
            title='Altitud (m)',
            thickness=25,
            len=0.6,
            yanchor='top',
            y=0.8,
            xanchor='left',
            x=1.05
        )
    )
    
    fig.write_html(output_file, include_plotlyjs='cdn')

def main():
    try:
        # Configure paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "A00_data", "B_raw", "TIRVolcH_La_Palma_Dataset.xlsx")
        images_folder = os.path.join(base_dir, "A04_web", "B_images")
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
            os.path.join(images_folder, "potencia_radiativa.html")
        )
        
        # 2. Generate 3D model
        generate_3d_la_palma_model(
            os.path.join(images_folder, "la_palma_3d.html")
        )
        
        print(f"Visualizaciones generadas en: {images_folder}")
        print(f"- Gráfico de potencia radiativa: potencia_radiativa.html")
        print(f"- Modelo 3D de La Palma: la_palma_3d.html")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)