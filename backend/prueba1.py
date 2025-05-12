# Importar paquetes
from dash import Dash, html, dash_table, dcc
import pandas as pd
from dash.dependencies import Input, Output

# Incorporar datos
df = pd.read_csv('persona_fisica.csv')

# Inicializar la aplicación
app = Dash(_name_)

# Diseño de la aplicación
app.layout = html.Div([
    html.H1(children='Mi tabla en Dash', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'Todos los datos', 'value': 'all'},
            {'label': 'Primeras 10 filas', 'value': 'first_10'},
            {'label': 'Primeras 20 filas', 'value': 'first_20'}
        ],
        value='all',  # Valor por defecto
        style={'width': '50%', 'margin': 'auto'}
    ),
    html.Div(id='table-container', style={'width': '80%', 'margin': 'auto'})
])

# Callback para actualizar la tabla
@app.callback(
    Output('table-container', 'children'),
    [Input('dropdown', 'value')]
)
def update_table(selected_value):
    if selected_value == 'all':
        data = df.to_dict('records')
        page_size = len(df)  # Mostrar todos los datos en una sola página
    elif selected_value == 'first_10':
        data = df.head(10).to_dict('records')
        page_size = 10
    elif selected_value == 'first_20':
        data = df.head(20).to_dict('records')
        page_size = 20
    else:  # Manejar el caso donde no se selecciona nada
        data = []
        page_size = 0

    return dash_table.DataTable(
        id='data-table',
        columns=[{'name': col, 'id': col} for col in df.columns],
        data=data,
        page_size=page_size,
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        }
    )

# Ejecutar la aplicación
if _name_ == '_main_':
    app.run(debug=True)