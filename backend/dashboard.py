from flask import Flask, render_template_string
import dash
from dash import html, dcc, dash_table, Output, Input
import plotly.graph_objs as go
import pandas as pd

# Cargar datos CSV
df = pd.read_csv('persona_fisica.csv')

# Crear app Flask principal
server = Flask(_name_)

# Template base de Flask (Home)
@server.route("/")
def home():
    return "<h1>Bienvenido a mi sitio Flask</h1><p>Ir al <a href='/dashboard'>Dashboard</a></p>"

# Inicializar Dash embebido en Flask
dash_app = dash.Dash(_name_, server=server, url_base_pathname='/dashboard/')

# Función para crear gráficos
def create_figure(graph_type):
    if graph_type == 'sexo' and 'sexo' in df.columns:
        sexo_counts = df['sexo'].value_counts()
        fig = go.Figure(data=[go.Pie(labels=sexo_counts.index, values=sexo_counts.values)])
        fig.update_layout(title="Distribución por Sexo")
        return fig

    elif graph_type == 'edad' and 'edad' in df.columns:
        fig = go.Figure(data=[go.Bar(x=df['edad'], y=[1]*len(df))])
        fig.update_layout(title="Distribución de Edades", xaxis_title="Edad", yaxis_title="Frecuencia")
        return fig

    elif graph_type == 'alcaldia' and 'alcaldia_catalogo' in df.columns:
        alcaldia_counts = df['alcaldia_catalogo'].value_counts().nlargest(10)
        fig = go.Figure(data=[go.Bar(x=alcaldia_counts.index, y=alcaldia_counts.values)])
        fig.update_layout(title="Top 10 Alcaldías", xaxis_title="Alcaldía", yaxis_title="Cantidad")
        return fig

    # Figura vacía por defecto
    return go.Figure()

# Layout del Dashboard
dash_app.layout = html.Div(children=[
    html.H1('Dashboard en /dashboard', style={'textAlign': 'center'}),

    html.H2('Tabla de Datos'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10, style_table={'overflowX': 'auto'}),

    html.H2('Selecciona un gráfico'),
    dcc.Dropdown(
        id='graph-selector',
        options=[
            {'label': 'Distribución por Sexo', 'value': 'sexo'},
            {'label': 'Distribución de Edades', 'value': 'edad'},
            {'label': 'Top 10 Alcaldías', 'value': 'alcaldia'}
        ],
        value='sexo',  # Inicial
        clearable=False
    ),

    dcc.Graph(id='graph-output')
])

# Callback de Dash
@dash_app.callback(
    Output('graph-output', 'figure'),
    Input('graph-selector', 'value')
)
def update_graph(selected_graph):
    return create_figure(selected_graph)

# Correr Flask
if _name_ == "_main_":
    server.run(debug=True, port=5000)