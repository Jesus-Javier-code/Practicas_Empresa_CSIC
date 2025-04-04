
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
        
        # ... [resto de la simulación topográfica existente] ...
    
    # Crear máscara de la colada
    lava_mask = create_lava_mask(lon_grid, lat_grid, dem_transform)
    
    # Aplicar espesor de lava
    if lava_mask is not None:
        lava_flow = np.where(lava_mask, z_real + LAVA_THICKNESS if z_real is not None else z + LAVA_THICKNESS, np.nan)
    else:
        lava_flow = np.full_like(z_real if z_real is not None else z, np.nan)
    
    # ... [resto del código de visualización existente] ...
    
    # Modificar el trace de la lava
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

    # ... [resto del layout] ...

# ... [resto del código main() sin cambios] ...
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

def generate_3d_la_palma_model(output_file):
    """Generate 3D model of La Palma island with real or simulated data"""
    # Try to load real DEM data first
    lon_grid, lat_grid, z_real = load_real_dem_data()
    
    if z_real is None:
        # Create simulated data if real DEM not available
        print("Generando modelo con datos topográficos simulados...")
        
        # Coordinates for La Palma island (whole island)
        lat = np.linspace(28.40, 28.90, 300)  # Alta resolución
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
        volcano_dist = np.sqrt((lat_grid-28.613)**2 + (lon_grid+17.873)**2)
        z_volcano = 500 * np.exp(-volcano_dist/0.0025)  # Cono más pronunciado
        
        # 4. Add secondary peaks
        roque_dist = np.sqrt((lat_grid-28.75)**2 + (lon_grid+17.89)**2)
        z_roque = 600 * np.exp(-roque_dist/0.01)  # Roque de los Muchachos
        
        # Combine all elements with weighted contributions
        z = base_elev + z_ridge*0.7 + z_volcano + z_caldera + z_roque*0.5
        
        # Add realistic terrain noise
        z += 100 * (np.sin(lon_grid*15) * np.cos(lat_grid*15))
        
        # Ensure sea level at 0
        z = np.maximum(z, 0)
    else:
        print("Usando datos DEM reales para el modelo 3D")
        z = z_real
    
    # Lava flows simulation (2021 eruption) - georeferenced
    lava_mask = ((lat_grid > 28.60) & (lat_grid < 28.63) & 
                (lon_grid > -17.88) & (lon_grid < -17.82))
    lava_flow = np.where(lava_mask, z + 5 + 3*np.random.rand(*z.shape), np.nan)  # 5-8m thick

    fig = go.Figure()
    
    # Custom colorscale based on real elevation colors
    colorscale = [
        [0.00, 'rgb(12,51,131)'],    # Mar profundo
        [0.01, 'rgb(57,144,218)'],   # Mar costero
        [0.02, 'rgb(234,236,198)'],  # Playa
        [0.05, 'rgb(169,204,153)'],  # Vegetación baja
        [0.15, 'rgb(88,161,75)'],    # Zonas medias
        [0.30, 'rgb(35,89,44)'],     # Montaña
        [0.60, 'rgb(102,60,20)'],    # Alta montaña 
        [1.00, 'rgb(150,150,150)']   # Cumbres
    ]
    
    # Island terrain
    fig.add_trace(go.Surface(
        z=z,
        x=lon_grid,
        y=lat_grid,
        colorscale=colorscale,
        name='Relieve',
        showscale=True,
        opacity=1,
        contours_z=dict(
            show=True, 
            width=3, 
            color='#413224',
            highlightcolor="#E74C3C",
            highlightwidth=5
        ),
        lighting=dict(
            ambient=0.8,
            diffuse=0.6,
            fresnel=0.2,
            roughness=0.8,
            specular=0.2
        )
    ))
    
    # Lava flows with realistic texture
    if np.any(~np.isnan(lava_flow)):
        fig.add_trace(go.Surface(
            z=lava_flow,
            x=lon_grid,
            y=lat_grid,
            colorscale=[[0, 'rgb(200,50,30)'], [1, 'rgb(100,20,10)']],
            name='Coladas 2021',
            showscale=False,
            opacity=0.9,
            surfacecolor=np.ones_like(lava_flow),
            lighting=dict(
                ambient=0.7,
                diffuse=0.7,
                roughness=0.9,
                specular=0.1
            )
        ))

    # Layout configuration
    fig.update_layout(
        title='<b>Modelo 3D Topográfico de La Palma</b><br>'
              '<sup>Datos del IGN y simulaciones de la erupción</sup>',
        scene=dict(
            xaxis_title='Longitud Oeste',
            yaxis_title='Latitud Norte',
            zaxis_title='Altitud (msnm)',
            aspectratio=dict(x=1.8, y=1, z=0.3),
            camera=dict(
                eye=dict(x=1.5, y=-1.8, z=0.6),  # Vista desde el SW
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=-0.2)
            ),
            zaxis=dict(
                range=[-1000 if z_real is None else np.nanmin(z), 
                      2500 if z_real is None else np.nanmax(z)],
                nticks=10,
                backgroundcolor='rgb(200,230,255)'
            ),
            xaxis=dict(
                gridcolor='rgba(100,100,100,0.2)',
                showspikes=False
            ),
            yaxis=dict(
                gridcolor='rgba(100,100,100,0.2)',
                showspikes=False
            )
        ),
        margin=dict(l=0, r=0, b=0, t=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
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
        
        # 2. Generate 3D model (will use real DEM if available)
        generate_3d_la_palma_model(
            os.path.join(images_folder, "la_palma_3d.html")
        )
        
        print(f"\nVisualizaciones generadas en: {images_folder}")
        print(f"- Gráfico de potencia radiativa: potencia_radiativa.html")
        print(f"- Modelo 3D de La Palma: la_palma_3d.html\n")
        
        # Instructions if DEM file not found
        if not os.path.exists(os.path.join(base_dir, "A00_data", "B_raw", "DEM_LaPalma.tif")):
            print("Para mayor precisión, descargue datos DEM del IGN y guárdelos como:")
            print("A00_data/B_raw/DEM_LaPalma.tif")
            print("Enlace recomendado: https://www.ign.es/web/ign/portal/descargas-territorio")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)