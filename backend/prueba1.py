from flask import Flask, render_template
from flask_cors import CORS
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, html, dash_table

# Crear la app Flask
app = Flask(__name__)
CORS(app)

# Ruta de Flask
@app.route('/')
def home():
    return render_template('index.html')

# Crear el Dash para la tabla
dash_app = Dash(__name__, server=app, url_base_pathname='/table_dash/')

# Leer el CSV
df = pd.read_csv('persona_fisica.csv')

# Configuración de la tabla Dash
dash_app.layout = html.Div(children=[
    html.H1('Mi tabla en Dash'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10)
])

# Configuración del Dashboard Plotly
@app.route('/dashboard')
def show_dashboard():
    df = pd.read_csv("persona_fisica.csv")
    data = []

    # Crear un gráfico de pastel para la distribución de 'sexo'
    if 'sexo' in df.columns:
        sexo_counts = df['sexo'].value_counts()
        pie_chart = go.Pie(labels=sexo_counts.index, values=sexo_counts.values, name="Distribución por Sexo", visible=True)
        data.append(pie_chart)

    # Crear el layout y gráfico de Plotly
    layout = go.Layout(
        title="Dashboard Interactivo"
    )

    fig = go.Figure(data=data, layout=layout)

    # Renderizar el gráfico en el HTML
    plot_div = fig.to_html(full_html=False)

    return render_template('dashboard.html', plot_div=plot_div)

# Ejecutar la app Flask
if __name__ == '__main__':
    app.run(debug=True)