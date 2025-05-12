# Import packages
from dash import Dash, html, dash_table
import pandas as pd

# Incorporate data
df = pd.read_csv('persona_fisica.csv')

# Initialize the app
app = Dash(_name)  # Es buena práctica pasar __name_

# App layout
app.layout = html.Div(children=[
    html.H1('Mi tabla en Dash'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10)
])

# Run the app
if _name_ == '_main_':
    app.run_server(debug=True)