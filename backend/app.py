from flask import Flask, render_template
from flask_cors import CORS
import pandas as pd
from dashboard import create_dashboard_from_csv

# Dash para la tabla
from dash import Dash, html, dash_table

# Crear la app Flask
app = Flask(__name__)
CORS(app)

# Rutas de Flask
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/content')
def content_page():
    return render_template('content.html')

@app.route('/perfil')
def perfil_page():
    return render_template('perfil.html')

@app.route('/dashboard')
def show_plotly_dashboard():
    dashboard = create_dashboard_from_csv("persona_fisica.csv")
    if dashboard:
        plotly_html = dashboard.render_dashboard()
        return render_template('dashboard.html', plot_div=plotly_html)
    else:
        return "Error al generar el dashboard.", 500

# Tabla con Dash (respetando tus códigos base)
dash_app = Dash(__name__, server=app, url_base_pathname='/table_dash/')

df = pd.read_csv('persona_fisica.csv')

dash_app.layout = html.Div(children=[
    html.H1('Mi tabla en Dash'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10)
])

if __name__ == '__main__':
    app.run(debug=True)