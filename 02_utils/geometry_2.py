import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
import numpy as np
import argparse

def configurar_rutas():
    """Configura las rutas de manera robusta"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        carpeta_imagenes = os.path.join(base_dir, "04_web", "images")
        
        if not os.path.exists(carpeta_imagenes):
            os.makedirs(carpeta_imagenes)
            print(f"✔ Carpeta creada: {carpeta_imagenes}")
        
        return os.path.join(carpeta_imagenes, "potencia_radiativa.html")
    except Exception as e:
        print(f"✖ Error configurando rutas: {e}")
        raise

def generar_datos(dias=7):
    """Genera datos de prueba con variación diurna"""
    try:
        fecha_inicio = datetime.now() - timedelta(days=dias)
        timestamps = pd.date_range(fecha_inicio, periods=dias*24, freq='h')
        
        # Datos simulados con variación diurna
        base = np.linspace(100, 180, len(timestamps))
        variacion = 50 * np.sin(np.linspace(0, dias*2*np.pi, len(timestamps)))
        ruido = np.random.normal(0, 10, len(timestamps))
        
        potencia = base + variacion + ruido
        
        return pd.DataFrame({
            'Fecha_Hora': timestamps,
            'Potencia_Radiativa': np.clip(potencia, 50, 250).round(2)
        })
    except Exception as e:
        print(f"✖ Error generando datos: {e}")
        raise

def crear_grafica_interactiva(df, dias):
    """Crea la gráfica con controles interactivos"""
    try:
        fig = px.line(
            df, 
            x='Fecha_Hora', 
            y='Potencia_Radiativa',
            title=f'Potencia Radiativa vs Tiempo (Últimos {dias} días)',
            labels={'Potencia_Radiativa': 'Potencia (W/m²)', 'Fecha_Hora': 'Tiempo'},
            template='plotly_white'
        )
        
        # Configuración del layout principal
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1d", step="day", stepmode="backward"),
                        dict(count=3, label="3d", step="day", stepmode="backward"),
                        dict(count=7, label="1w", step="day", stepmode="backward"),
                        dict(step="all", label="Todo")
                    ]),
                    bgcolor='lightgray',
                    activecolor='blue',
                    font=dict(size=12)
                ),
                rangeslider=dict(
                    visible=True,
                    thickness=0.1
                ),
                type="date"
            ),
            yaxis_title="Potencia Radiativa (W/m²)",
            hovermode="x unified",
            showlegend=False,
            height=600,
            margin=dict(l=50, r=50, b=100, t=80, pad=10),
            plot_bgcolor='rgba(240,240,240,0.9)'
        )
        
        return fig
    except Exception as e:
        print(f"✖ Error creando gráfica: {e}")
        raise

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(
            description='Genera gráficas interactivas de potencia radiativa'
        )
        parser.add_argument(
            '--dias', 
            type=int, 
            default=7,
            help='Número de días a visualizar (por defecto: 7)'
        )
        args = parser.parse_args()
        
        print("\n=== Iniciando generación de gráfica ===")
        
        # 1. Configurar rutas
        archivo_salida = configurar_rutas()
        
        # 2. Generar datos
        print(f"\nℹ Generando datos para {args.dias} días...")
        datos = generar_datos(args.dias)
        
        # 3. Crear gráfica
        print("\nℹ Creando gráfica interactiva...")
        fig = crear_grafica_interactiva(datos, args.dias)
        
        # 4. Guardar con configuración correcta
        config = {
            'responsive': True,
            'displayModeBar': True,
            'modeBarButtonsToAdd': [
                'zoom2d',
                'pan2d',
                'select2d',
                'lasso2d',
                'zoomIn2d',
                'zoomOut2d',
                'resetScale2d',
                'toImage'
            ],
            'scrollZoom': True
        }
        
        fig.write_html(
            archivo_salida,
            include_plotlyjs='cdn',
            config=config
        )
        
        print(f"\n✔ Gráfica guardada exitosamente en: {archivo_salida}")
        print("✅ Proceso completado con éxito")
        
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        sys.exit(1)