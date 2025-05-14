# table_dash_app.py

from dash import Dash, html, dash_table
import pandas as pd

def create_dash_table(server):
    df = pd.read_csv('persona_fisica.csv')

    dash_app = Dash(__name__, server=server, url_base_pathname='/table_dash/')

    dash_app.layout = html.Div(children=[
        html.H1('Mi tabla en Dash'),
        dash_table.DataTable(data=df.to_dict('records'), page_size=10)
    ])

    return dash_app