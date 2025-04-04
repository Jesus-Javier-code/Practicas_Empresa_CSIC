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
        )  # Aquí faltaba este paréntesis
    )
    
    fig.write_html(output_file, include_plotlyjs='cdn')