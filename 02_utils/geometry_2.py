# geometry_2.py - Versión con puntos en lugar de líneas
import pandas as pd
import plotly.express as px
import os
import sys
from datetime import datetime

def main():
    try:
        # Configurar rutas
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "00_data", "raw", "TIRVolcH_La_Palma_Dataset.xlsx")
        carpeta_imagenes = os.path.join(base_dir, "04_web", "images")
        os.makedirs(carpeta_imagenes, exist_ok=True)
        archivo_salida = os.path.join(carpeta_imagenes, "potencia_radiativa.html")

        # Leer datos del Excel
        df = pd.read_excel(data_path, sheet_name='LaPalma_TIRVolcH_Filtered_Data')
        
        # Limpiar y preparar datos
        df = df[['Date', 'Weekly_Max_VRP_TIR (MW)']].dropna()
        df = df.rename(columns={
            'Date': 'Fecha_Hora',
            'Weekly_Max_VRP_TIR (MW)': 'Potencia_Radiativa'
        })
        
        # Convertir a datetime y ordenar
        df['Fecha_Hora'] = pd.to_datetime(df['Fecha_Hora'])
        df = df.sort_values('Fecha_Hora')

        # Crear gráfica de puntos (scatter plot)
        fig = px.scatter(df, 
                        x='Fecha_Hora', 
                        y='Potencia_Radiativa',
                        title='<b>Potencia Radiativa Máxima Semanal</b><br><sup>Volcán de La Palma (2021-2024) - Datos Puntuales</sup>',
                        template='plotly_white',
                        labels={
                            'Fecha_Hora': 'Fecha',
                            'Potencia_Radiativa': 'Potencia Radiativa (MW)'
                        },
                        hover_data={'Fecha_Hora': '|%B %d, %Y'},
                        opacity=0.7,
                        size_max=10)
        
        # Personalizar marcadores
        fig.update_traces(
            marker=dict(
                size=6,
                color='#E74C3C',  # Rojo volcánico
                line=dict(width=1, color='DarkSlateGrey')
            ),
            selector=dict(mode='markers')
        )

        # Personalizar diseño
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
            title_font=dict(size=20)
        )

        # Añadir anotación con valor máximo
        max_potencia = df['Potencia_Radiativa'].max()
        max_fecha = df.loc[df['Potencia_Radiativa'].idxmax(), 'Fecha_Hora']
        fig.add_annotation(
            x=max_fecha,
            y=max_potencia,
            text=f"Máximo: {max_potencia:.0f} MW",
            showarrow=True,
            arrowhead=1,
            ax=-50,
            ay=-40,
            font=dict(size=12, color="#E74C3C")
        )

        # Guardar gráfica
        fig.write_html(archivo_salida, include_plotlyjs='cdn')
        print(f"Gráfica generada en: {archivo_salida}")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)