# Importaciones
import plotly.graph_objs as go
import pandas as pd

# Definición de la función, tiene un parámetro opcional (csv_filepath)
def create_interactive_dashboard(csv_filepath="persona_fisica.csv"):
    try: # Se ejecuta el código principal dentro del bloque (try), si ocurre algún error se pasa al bloque (except)

        df = pd.read_csv(csv_filepath)

        # Listas para almacenar cada gráfico
        data = [] # Almacena los gráficos
        buttons = [] # Almacena los botones de interacción
        visibility = [] # Controlar qué gráfico es visible inicialmente

        # Gráfico de pastel: Distribución por Sexo
        if 'sexo' in df.columns: # Verifica si la columna sexo está en df.columns
            sexo_counts = df['sexo'].value_counts() # Se cuentan los valores de la columna
            # Crea un gráfico de pastel (go.pie) con esas categorías.
            pie_chart = go.Pie(labels=sexo_counts.index, values=sexo_counts.values, name="Distribución por Sexo", visible=True)
            data.append(pie_chart) # Se agrega el gráfico a la lista data
            visibility.append(True) # Se marca como visible incialmente

        # Gráfico de barras: Distribución de Edades
        if 'edad' in df.columns: # Verifica si la columna edad está en df.columns
            # Se crea un gráfico de barra, en el eje X va al edad y el Y es un conteo (1 por cada fila),
            # es decir, cada edad representa un individuo.
            edad_bar = go.Bar(x=df['edad'], y=[1]*len(df), name="Distribución de Edades", visible=False)
            data.append(edad_bar) # Se agrega el gráfico a la lista data
            visibility.append(False) # Se marca como no visible incialmente

        # Gráfico de barras: Top 10 Alcaldías
        if 'alcaldia_catalogo' in df.columns: # Verifica si la columna alcaldia_catalogo está en df.columns
            # Si existe la columna (alcaldia_catalogo), cuenta cuántas veces aparece cada alcaldía.
            alcaldia_counts = df['alcaldia_catalogo'].value_counts().nlargest(10) # Selecciona las 10 más frecuentes
            # Crea un gráfico de barras con los nombres y frecuencias de esas alcaldías.
            alcaldia_bar = go.Bar(x=alcaldia_counts.index, y=alcaldia_counts.values, name="Top 10 Alcaldías", visible=True)
            data.append(alcaldia_bar) # Se agrega el gráfico a la lista data
            visibility.append(True) # Se marca como visible incialmente

        # Botones interactivos
        for i, trace in enumerate(data): # Se itera sobre cada gráfico (trace) en data
            # Se crea una lista (vis) con todos (False) excepto el índice actual (i)
            # Significa que se está creando una lista de booleanos (False) con una longitud igual
            # al número de gráficos almacenados en la lista (data).
            vis = [False] * len(data)
            vis[i] = True # Será (True) esto asegura que solo un gráfico sea visible a la vez.
            # Se crea un botón que actualiza la visibilidad y el título del gráfico
            button = dict(label=data[i].name,
                          method="update",
                          args=[{"visible": vis},
                                {"title": data[i].name}])
            buttons.append(button) # Se agrega el botón a la lista

        # Layout con botones
        layout = go.Layout(
            title="Dashboard Interactivo",
            updatemenus=[dict(type="buttons", direction="down", showactive=True, buttons=buttons)]
        ) # Se añade un menú de botones desplegables con los botones definidos.

        # Creación y visualización del dashboard
        # Se crea una variable (Figure) que contiene los datos (data) y diseño (layout).
        fig = go.Figure(data=data, layout=layout)
        fig.show() # Se muestra el gráfico de forma interactiva

    # Manejo de errores
    except FileNotFoundError:
        print("Archivo CSV no encontrado.")
    except Exception as e:
        print(f"Error al crear el dashboard: {e}")

# Llamar a la función
create_interactive_dashboard("persona_fisica.csv")