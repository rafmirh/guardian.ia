import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_table

# La función tiene parámetro opcional (csv_filepath), esta ruta se usará para leer un archivo csv
def create_dashboard_from_csv(csv_filepath="persona_fisica.csv"):
    try:  # Se ejecuta el código principal dentro del bloque (try), si ocurre algún error se pasa al bloque (except)
        df = pd.read_csv(csv_filepath)
        dashboard = {}  # Cambiamos a un diccionario para almacenar DataFrames

        if 'sexo' in df.columns:  # Gráfico de pastel para sexo, si existe una columna llamada (sexo), ejecuta lo demás
            sexo_counts = df['sexo'].value_counts()  # Se cuentan los valores de la columna
            dashboard['sexo'] = pd.DataFrame({
                'labels': sexo_counts.index,
                'values': sexo_counts.values
            })  # Se crea un DataFrame

        if 'edad' in df.columns:  # Histograma de edades (como barra), si existe la columna (edad)
            # Se crea un DataFrame con la distribución de edades
            edad_df = df['edad'].value_counts().reset_index()
            edad_df.columns = ['edad', 'frecuencia']
            dashboard['edad'] = edad_df

        if 'alcaldia_catalogo' in df.columns:  # Gráfico de barras Top 10 Alcaldías
            # Si existe la columna (alcaldia_catalogo), cuenta cuántas veces aparece cada alcaldía.
            alcaldia_counts = df['alcaldia_catalogo'].value_counts().nlargest(
                10)  # Selecciona las 10 más frecuentes
            dashboard['alcaldia'] = pd.DataFrame({
                'alcaldia': alcaldia_counts.index,
                'conteo': alcaldia_counts.values
            })  # Se crea un DataFrame

        return dashboard  # Se devuelve el objeto (dashboard) con los DataFrames

    # Manejo de errores
    except FileNotFoundError:
        print(
            f"Error: No se pudo encontrar el archivo CSV en la ruta especificada.")
        return None  # Si el archivo csv no se encuentra, se duelve (None)
    except Exception as e:
        print(f"Error al crear el dashboard: {e}")
        return None  # Para otros errores, se imprime el mensaje y también se devuelve (None)



def create_dash_app(dashboard_data):
    app = dash.Dash(_name_)

    # Define el diseño de la aplicación
    app.layout = html.Div([
        html.H1("Dashboard Interactivo", style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='data-selection',
            options=[{'label': k, 'value': k} for k in dashboard_data.keys()],
            value=list(dashboard_data.keys())[0]  # Valor inicial
        ),
        html.Div(id='table-container')
    ])

    # Define la función de callback para actualizar la tabla
    @app.callback(
        Output('table-container', 'children'),
        [Input('data-selection', 'value')]
    )
    def update_table(selected_data):
        df = dashboard_data[selected_data]
        return dash_table.DataTable(
            id='data-table',
            columns=[{'name': col, 'id': col} for col in df.columns],
            data=df.to_dict('records'),
            page_size=10,  # Define el número de filas por página
            style_cell={'textAlign': 'left'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )

    return app



if _name_ == "_main_":
    dashboard_data = create_dashboard_from_csv()
    if dashboard_data:
        app = create_dash_app(dashboard_data)
        app.run_server(debug=True)
    else:
        print("No se pudo crear el dashboard.")