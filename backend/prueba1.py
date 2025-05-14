from dash import Dash, html, dash_table
import pandas as pd

# Incorporar datos
df = pd.read_csv('persona_fisica.csv')

# Inicializar la app
app = Dash(__name__)

# Layout de la app
app.layout = html.Div(children=[
    html.H1('Mi tabla en Dash'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10, style_table={'overflowX': 'auto'}),
])

# Ejecutar la app
if __name__ == '__main__':
    app.run_server(debug=True)