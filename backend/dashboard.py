import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd  # Importa pandas aquí

# La función tiene parámetro opcional (csv_filepath), esta ruta se usará para leer un archivo csv
def create_dashboard_from_csv(csv_filepath="persona_fisica.csv"): 
    try: # Se ejecuta el código principal dentro del bloque (try), si ocurre algún error se pasa al bloque (except)
        df = pd.read_csv(csv_filepath)
        dashboard = Dashboard() # Creación del dashboard

        if 'sexo' in df.columns: # Gráfico de pastel para sexo, si existe una columna llamada (sexo), ejecuta lo demás
            sexo_counts = df['sexo'].value_counts() # Se cuentan los valores de la columna
            dashboard.add_pie_chart(labels=sexo_counts.index, values=sexo_counts.values, title="Distribución por Sexo") # Se crea un gráfico de pastel

        if 'edad' in df.columns: # Histograma de edades (como barra), si existe la columna (edad)
            # Se crea un gráfico donde el eje X es la edad y el eje Y es un conteo (1 por cada fila), pretende simular una distribución de frecuencias
            dashboard.add_bar_chart(x=df['edad'], y=[1]*len(df), title="Distribución de Edades", xaxis_title="Edad", yaxis_title="Frecuencia")

        if 'alcaldia_catalogo' in df.columns: # Gráfico de barras Top 10 Alcaldías
            # Si existe la columna (alcaldia_catalogo), cuenta cuántas veces aparece cada alcaldía.
            alcaldia_counts = df['alcaldia_catalogo'].value_counts().nlargest(10) # Selecciona las 10 más frecuentes
            dashboard.add_bar_chart(x=alcaldia_counts.index, y=alcaldia_counts.values, title="Top 10 Alcaldías") # Se muestra un gráfico con las 10 alcaldías

        return dashboard # Se devuelve el objeto (dashboard) con los gráficos agregados
    
    # Manejo de errores
    except FileNotFoundError:
        return None  # Si el archivo csv no se encuentra, se duelve (None)
    except Exception as e:
        print(f"Error al crear el dashboard: {e}")
        return None # Para otros errores, se imprime el mensaje y también se devuelve (None)