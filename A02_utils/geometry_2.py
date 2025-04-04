# geometry_2.py - Versión con colada real de 2021
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import sys
from datetime import datetime
from shapely.geometry import Polygon
from shapely.geometry import Point

# Configuración de la colada
LAVA_THICKNESS = 30  # Espesor promedio en metros
LAVA_COLORSCALE = [[0, 'rgb(180,40,30)'], [1, 'rgb(100,20,10)']]  # Color lava

def load_lava_perimeter():
    """Cargar el perímetro de la colada desde el GeoJSON"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        geojson_path = os.path.join(base_dir, "A00_data", "B_raw", "perimetro_dron_211123.geojson")
        
        with open(geojson_path) as f:
            data = json.load(f)
        
        # Extraer coordenadas del polígono principal
        coordinates = data['features'][0]['geometry']['coordinates'][0]
        return np.array(coordinates)
    
    except Exception as e:
        print(f"Error cargando GeoJSON: {str(e)}")
        return None

def create_lava_mask(lon_grid, lat_grid, dem_transform=None):
    """Crear máscara para la colada de lava"""
    lava_coords = load_lava_perimeter()
    if lava_coords is None:
        return None
    
    # Crear polígono Shapely
    polygon = Polygon(lava_coords)
    
    # Convertir coordenadas a puntos en la rejilla
    mask = np.zeros_like(lon_grid, dtype=bool)
    
    # Ajustar según si es DEM real o simulado
    if dem_transform is None:  # Datos simulados
        lon_min, lon_max = -18.10, -17.60
        lat_min, lat_max = 28.40, 28.90
    else:  # Datos reales
        lon_min, lat_min = dem_transform * (0, 0)
        lon_max, lat_max = dem_transform * (lon_grid.shape[1], lon_grid.shape[0])
    
    # Generar máscara
    for i in range(lon_grid.shape[0]):
        for j in range(lon_grid.shape[1]):
            point = (lon_grid[i,j], lat_grid[i,j])
            if polygon.contains(Point(point)):
                mask[i,j] = True
                
    return mask

def generate_3d_la_palma_model(output_file):
    """Generate 3D model with real lava flow"""
    lon_grid, lat_grid, z_real = load_real_dem_data()
    dem_transform = None
    
    if z_real is None:
        # Crear datos simulados
        lat = np.linspace(28.40, 28.90, 300)
        lon = np.linspace(-18.10, -17.60, 300)
        lon_grid, lat_grid = np.meshgrid(lon, lat)
        
        # Base elevation (sea level)
        base_elev = 0
        
        # Simulate the whole island topography with improved accuracy
        # 1. Main ridge (Cumbre Vieja + Cumbre Nueva)
        ridge_dist = np.sqrt((lat_grid-28.58)**2 + (lon_grid+17.85)**2)
        z_ridge = 2400 * np.exp(-ridge_dist/0.035)  # Más realista
        
        # 2. Caldera de Taburiente (more accurate shape)
        caldera_dist = np.sqrt((lat_grid-28.73)**2 + (lon_grid+17.88)**2)
        z_caldera = np.where(caldera_dist < 0.025, 
                            -900 * (1 - caldera_dist/0.025)**2,  # Forma más real
                            0)
        
        # 3. Tajogaite volcano (2021 eruption) - more accurate cone
        volcano_dist = np.sqrt((lat_grid-28.66)**2 + (lon_grid+17.81)**2)
        z_volcano = np.where(volcano_dist < 0.02, 
                            1000 * (1 - volcano_dist/0.02)**2,  # Forma real
                            0)
        
        # Combining the different terrain features
        z = base_elev + z_ridge + z_caldera + z_volcano
    else:
        # Use real DEM data if available
        z = z_real
    
    # Crear máscara de la colada
    lava_mask = create_lava_mask(lon_grid, lat_grid, dem_transform)
    
    # Aplicar espesor de lava
    if lava_mask is not None:
        lava_flow = np.where(lava_mask, z + LAVA_THICKNESS, np.nan)
    else:
        lava_flow = np.full_like(z, np.nan)
    
    # Visualización 3D de La Palma
    fig = go.Figure()

    # Agregar la superficie de la isla
    fig.add_trace(go.Surface(
        z=z,
        x=lon_grid,
        y=lat_grid,
        colorscale='Viridis',
        opacity=0.7,
        surfacecolor=z,
        name='Topografía'
    ))

    # Agregar la superficie de la lava
    if np.any(~np.isnan(lava_flow)):
        fig.add_trace(go.Surface(
            z=lava_flow,
            x=lon_grid,
            y=lat_grid,
            colorscale=LAVA_COLORSCALE,
            name='Colada 2021',
            showscale=False,
            opacity=0.95,
            surfacecolor=np.ones_like(lava_flow),
            lighting=dict(
                ambient=0.7,
                diffuse=0.5,
                roughness=0.9,
                specular=0.1
            ),
            contours_z=dict(
                show=True, 
                width=2, 
                color='rgb(80,20,10)',
                highlightcolor="rgb(200,50,30)",
                highlightwidth=3
            )
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Longitud'),
            yaxis=dict(title='Latitud'),
            zaxis=dict(title='Elevación'),
            aspectmode='cube'
        ),
        title='Modelo 3D de La Palma',
        margin=dict(l=0, r=0, b=0, t=40),
        showlegend=True
    )

    fig.write_html(output_file)

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

def load_real_dem_data():
    """Try to load real DEM data if available"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dem_path = os.path.join(base_dir, "A00_data", "B_raw", "DEM_LaPalma.tif")
        
        if os.path.exists(dem_path):
            import rasterio
            with rasterio.open(dem_path) as src:
                dem = src.read(1)
                transform = src.transform
                bounds = src.bounds
                
                # Create coordinates
                rows, cols = dem.shape
                x = np.linspace(bounds.left, bounds.right, cols)
                y = np.linspace(bounds.bottom, bounds.top, rows)
                xx, yy = np.meshgrid(x, y)
                
                return xx, yy, dem
                
    except Exception as e:
        print(f"Warning: No se pudo cargar DEM real. Usando datos simulados. Error: {str(e)}")
    
    return None, None, None

if __name__ == "__main__":
    # Generación del modelo 3D
    output_file = "output/la_palma_3d_model.html"
    generate_3d_la_palma_model(output_file)
    print(f"Modelo 3D generado y guardado en {output_file}")
    
    # Generación de gráfico de potencia radiativa
    data = pd.read_csv('radiative_power_data.csv')
    radiative_power_file = "output/radiative_power_plot.html"
    generate_radiative_power_plot(data, radiative_power_file)
    print(f"Gráfico de potencia radiativa guardado en {radiative_power_file}")
