import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
import numpy as np
import argparse
import sys

def configurar_rutas():
    """Configura y verifica las rutas de guardado"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    carpeta_imagenes = os.path.join(base_dir, "04_web", "images")
    
    if not os.path.exists(carpeta_imagenes):
        try:
            os.makedirs(carpeta_imagenes)
            print(f"✔ Carpeta creada: {carpeta_imagenes}")
        except Exception as e:
            print(f"✖ Error al crear carpeta: {e}")
            sys.exit(1)
    
    archivo_salida = os.path.join(carpeta_imagenes, "potencia_radiativa.html")
    return archivo_salida

def generar_datos_reales(dias=7):
    """Simula datos reales (aquí cargarías tus datos actuales)"""
    try:
        fecha_inicio = datetime.now() - timedelta(days=dias)
        timestamps = pd.date_range(fecha_inicio, periods=dias*24, freq='h')
        potencia = np.random.uniform(50, 200, size=len(timestamps)) * \
                  (1 + 0.1 * np.sin(np.linspace(0, dias*np.pi, len(timestamps))))
        
        return pd.DataFrame({
            'Fecha_Hora': timestamps,
            'Potencia_Radiativa': potencia.round(2)
        })
    except Exception as e:
        print(f"✖ Error generando datos: {e}")
        sys.exit(1)

def crear_grafica(df, dias, archivo_salida, mostrar=False):
    """Crea y guarda la gráfica interactiva"""
    try:
        fig = px.line(df, x='Fecha_Hora', y='Potencia_Radiativa',
                     title=f'Potencia Radiativa vs Tiempo (Últimos {dias} días)',
                     labels={'Potencia_Radiativa': 'Potencia (W/m²)', 'Fecha_Hora': 'Tiempo'},
                     template='plotly_white')
        
        fig.update_layout(
            hovermode="x unified",
            xaxis_title="Fecha y Hora",
            yaxis_title="Potencia Radiativa (W/m²)",
            showlegend=False
        )
        
        # Guardar archivo
        fig.write_html(archivo_salida, include_plotlyjs='cdn')
        print(f"✔ Gráfica guardada en: {archivo_salida}")
        
        # Mostrar si se solicita
        if mostrar:
            fig.show()
            
        return True
    except Exception as e:
        print(f"✖ Error creando gráfica: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generador de gráficas de potencia radiativa')
    parser.add_argument('--dias', type=int, default=7, help='Días a visualizar (default: 7)')
    parser.add_argument('--mostrar', action='store_true', help='Mostrar gráfica interactiva')
    args = parser.parse_args()
    
    print("\n=== Iniciando generación de gráfica ===")
    
    # 1. Configurar rutas
    archivo_salida = configurar_rutas()
    
    # 2. Generar datos
    print(f"\nℹ Generando datos para {args.dias} días...")
    datos = generar_datos_reales(args.dias)
    
    # 3. Crear y guardar gráfica
    print("\nℹ Creando gráfica interactiva...")
    if crear_grafica(datos, args.dias, archivo_salida, args.mostrar):
        print("\n✅ Proceso completado con éxito")
    else:
        print("\n❌ Error en el proceso")
        sys.exit(1)