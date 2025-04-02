# geometry_2.py - Version with points instead of lines
import pandas as pd
import plotly.express as px
import os
import sys
from datetime import datetime

def main():
    try:
        # Configure paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "00_data", "raw", "TIRVolcH_La_Palma_Dataset.xlsx")
        images_folder = os.path.join(base_dir, "04_web", "images")
        os.makedirs(images_folder, exist_ok=True)
        output_file = os.path.join(images_folder, "radiative_power.html")

        # Read data from Excel
        df = pd.read_excel(data_path, sheet_name='LaPalma_TIRVolcH_Filtered_Data')
        
        # Clean and prepare data
        df = df[['Date', 'Weekly_Max_VRP_TIR (MW)']].dropna()
        df = df.rename(columns={
            'Date': 'DateTime',
            'Weekly_Max_VRP_TIR (MW)': 'Radiative_Power'
        })
        
        # Convert to datetime and sort
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        df = df.sort_values('DateTime')

        # Create scatter plot
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
                color='#413224',  # Dark brown color
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

        # Save plot
        fig.write_html(output_file, include_plotlyjs='cdn')
        print(f"Plot generated at: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)