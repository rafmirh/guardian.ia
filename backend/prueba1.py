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
    
    df = pd.read_csv('persona_fisica.csv')
    df = df.dropna(subset=['alcaldia_catalogo'])

    data = []
    buttons = []
    visibility = []

    # Gráfico de pastel: Sexo
    if 'sexo' in df.columns:
        sexo_counts = df['sexo'].value_counts()
        pie_chart = go.Pie(labels=sexo_counts.index, values=sexo_counts.values, name="Distribución por Sexo", visible=True)
        data.append(pie_chart)
        visibility.append(True)

    # Gráfico de barras: Edad con número de personas
    if 'edad' in df.columns:
        edad_counts = df['edad'].value_counts().sort_index()
        edad_bar = go.Bar(
            x=edad_counts.index,
            y=edad_counts.values,
            name="Distribución de Edades",
            visible=False,
            hovertemplate="Edad: %{x}<br>Personas: %{y}"
        )
        data.append(edad_bar)
        visibility.append(False)

    # Gráfico de barras: Alcaldías con conteo, y solo si hay datos
    if 'alcaldia_catalogo' in df.columns and not df['alcaldia_catalogo'].empty:
        alcaldia_counts = df['alcaldia_catalogo'].value_counts().nlargest(10)
        alcaldia_bar = go.Bar(
            x=alcaldia_counts.index,
            y=alcaldia_counts.values,
            name="Top 10 Alcaldías",
            visible=False,
            hovertemplate="Alcaldía: %{x}<br>Conteo: %{y}"
        )
        data.append(alcaldia_bar)
        visibility.append(False)

    # Botones de interacción
    for i, trace in enumerate(data):
        vis = [False] * len(data)
        vis[i] = True
        button = dict(label=data[i].name, method="update", args=[{"visible": vis}, {"title": data[i].name}])
        buttons.append(button)

    # Layout de Plotly
    layout = go.Layout(
        title="Dashboard Interactivo - Análisis Detallado",
        updatemenus=[dict(type="buttons", direction="down", showactive=True, buttons=buttons)],
        hovermode='closest'
    )

    # Crear figura de Plotly
    fig = go.Figure(data=data, layout=layout)

    # Renderizar el gráfico interactivo
    plot_div = fig.to_html(full_html=False)

    return render_template('dashboard.html', plot_div=plot_div)

# Ejecutar la app Flask
if __name__ == '__main__':
    app.run(debug=True)
