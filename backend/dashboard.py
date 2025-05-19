import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, callback_context
import dash_bootstrap_components as dbc
from flask import Flask
import numpy as np
from dash.exceptions import PreventUpdate
import os

# Cargar y preparar datos
def load_data():
    # Comprobar si el archivo existe
    file_path = 'usurpacion_etl.csv'
    if not os.path.exists(file_path):
        # Si el archivo no existe, crear un DataFrame de muestra
        print(f"ADVERTENCIA: Archivo {file_path} no encontrado. Usando datos de muestra.")
        # Crear datos de muestra basados en las primeras filas proporcionadas
        data = {
            'fecha_hecho': ['2019-01-04', '2018-12-20', '2019-01-03', '2019-01-08'],
            'delito': ['USURPACIÓN DE IDENTIDAD'] * 4,
            'sexo': [0, 1, 0, 1],
            'edad': [42, 41, 53, 55],
            'colonia_catalogo': ['San Pedro De Los Pinos', 'Tenorios', 'Centro', 'Centro'],
            'alcaldia_catalogo': ['Álvaro Obregón', 'Iztapalapa', 'Cuauhtémoc', 'Cuauhtémoc'],
            'latitud': [19.38951, 19.3301, 19.43338, 19.43426],
            'longitud': [-99.19018, -99.02099, -99.13518, -99.14089],
            'anio_hecho': [2019, 2018, 2019, 2019],
            'mes_hecho': [1, 12, 1, 1],
            'dia_hecho': [4, 20, 3, 8],
            'indice_alcaldia': [15, 7, 4, 4]
        }
        df = pd.DataFrame(data)
    else:
        # Si el archivo existe, cargarlo normalmente
        df = pd.read_csv(file_path)
    
    # Mapear valores de sexo (0=Hombre, 1=Mujer)
    df['sexo_texto'] = df['sexo'].map({0: 'Hombre', 1: 'Mujer'})
    # Agrupar edades en rangos
    bins = [0, 18, 30, 40, 50, 60, 100]
    labels = ['0-18', '19-30', '31-40', '41-50', '51-60', '61+']
    df['rango_edad'] = pd.cut(df['edad'], bins=bins, labels=labels, right=False)
    return df

# Aplicación Dash
def init_dashboard(server):
    # Tema oscuro con Bootstrap
    dash_app = Dash(
        server=server,
        routes_pathname_prefix='/dashboard/',
        external_stylesheets=[dbc.themes.DARKLY],
        suppress_callback_exceptions=True
    )
    
    # Cargar datos
    df = load_data()
    
    # Obtener valores únicos para los filtros
    sexos = [{'label': 'Todos', 'value': 'Todos'}] + [{'label': s, 'value': s} for s in df['sexo_texto'].unique()]
    alcaldias = [{'label': 'Todas', 'value': 'Todas'}] + [{'label': a, 'value': a} for a in sorted(df['alcaldia_catalogo'].unique())]
    años = [{'label': 'Todos', 'value': 'Todos'}] + [{'label': str(a), 'value': a} for a in sorted(df['anio_hecho'].unique())]
    meses = [{'label': 'Todos', 'value': 'Todos'}] + [{'label': str(m), 'value': m} for m in range(1, 13)]
    
    # Diseño del dashboard
    dash_app.layout = html.Div([
        dbc.Container([
            # Título del dashboard
            html.H1("Dashboard de Usurpación de Identidad", className="text-center my-4", 
                   style={'color': '#B026FF', 'text-shadow': '0 0 10px #B026FF, 0 0 20px #B026FF'}),
            
            # Filtros
            dbc.Row([
                dbc.Col([
                    html.Label("Sexo:", style={'color': '#ffffff'}),
                    dcc.Dropdown(id='sexo-filter', options=sexos, value='Todos', 
                                className='mb-3', 
                                style={'backgroundColor': '#222', 'color': '#000'})
                ], width=3),
                dbc.Col([
                    html.Label("Alcaldía:", style={'color': '#ffffff'}),
                    dcc.Dropdown(id='alcaldia-filter', options=alcaldias, value='Todas', 
                                className='mb-3', 
                                style={'backgroundColor': '#222', 'color': '#000'})
                ], width=3),
                dbc.Col([
                    html.Label("Año:", style={'color': '#ffffff'}),
                    dcc.Dropdown(id='anio-filter', options=años, value='Todos', 
                                className='mb-3', 
                                style={'backgroundColor': '#222', 'color': '#000'})
                ], width=3),
                dbc.Col([
                    html.Label("Mes:", style={'color': '#ffffff'}),
                    dcc.Dropdown(id='mes-filter', options=meses, value='Todos', 
                                className='mb-3', 
                                style={'backgroundColor': '#222', 'color': '#000'})
                ], width=3)
            ], className="mb-4"),
            
            # Gráficos - Primera fila
            dbc.Row([
                # Gráfico de pastel - Distribución por sexo
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Distribución por Sexo", style={'backgroundColor': '#390c53', 'color': 'white'}),
                        dbc.CardBody([
                            dcc.Graph(id='pie-sexo', style={'height': '30vh', 'width': '62vh'})
                        ])
                    ], style={'height': '100%', 'backgroundColor': '#222', 'borderColor': '#B026FF'})
                ], width=4),
                
                # Gráfico de barras - Distribución por edad
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Distribución por Edad", style={'backgroundColor': '#390c53', 'color': 'white'}),
                        dbc.CardBody([
                            dcc.Graph(id='bar-edad', style={'height': '30vh', 'width': '62vh'})
                        ])
                    ], style={'height': '100%', 'backgroundColor': '#222', 'borderColor': '#B026FF'})
                ], width=4)
            ], className="mb-4"),
            
            # Gráficos - Segunda fila
            dbc.Row([
                # Gráfico de línea - Tendencia anual
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Tendencia por Año", style={'backgroundColor': '#390c53', 'color': 'white'}),
                        dbc.CardBody([
                            dcc.Graph(id='line-anio', style={'height': '30vh', 'width': '62vh'})
                        ])
                    ], style={'height': '100%', 'backgroundColor': '#222', 'borderColor': '#B026FF'})
                ], width=4),
                
                # Diagrama de árbol - Colonias
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Distribución por Colonia", style={'backgroundColor': '#390c53', 'color': 'white'}),
                        dbc.CardBody([
                            dcc.Graph(id='treemap-colonia', style={'height': '30vh', 'width': '62vh'})
                        ])
                    ], style={'height': '100%', 'backgroundColor': '#222', 'borderColor': '#B026FF'})
                ], width=4)
            ])
        ], fluid=True, style={'backgroundColor': '#0d1117', 'minHeight': '100vh', 'padding': '20px'})
    ])
    
    # Definir callbacks para actualizar gráficos
    @dash_app.callback(
        [Output('pie-sexo', 'figure'),
         Output('bar-edad', 'figure'),
         Output('line-anio', 'figure'),
         Output('treemap-colonia', 'figure')],
        [Input('sexo-filter', 'value'),
         Input('alcaldia-filter', 'value'),
         Input('anio-filter', 'value'),
         Input('mes-filter', 'value')]
    )
    def update_graphs(sexo, alcaldia, anio, mes):
        # Filtrar datos según selección
        filtered_df = df.copy()
        
        if sexo != 'Todos':
            filtered_df = filtered_df[filtered_df['sexo_texto'] == sexo]
        if alcaldia != 'Todas':
            filtered_df = filtered_df[filtered_df['alcaldia_catalogo'] == alcaldia]
        if anio != 'Todos':
            filtered_df = filtered_df[filtered_df['anio_hecho'] == anio]
        if mes != 'Todos':
            filtered_df = filtered_df[filtered_df['mes_hecho'] == mes]
        
        # Si no hay datos después de filtrar
        if filtered_df.empty:
            # Crear gráficos vacíos con mensaje
            empty_fig = go.Figure()
            empty_fig.update_layout(
                plot_bgcolor='#222',
                paper_bgcolor='#222',
                font=dict(color='white'),
                title_text='No hay datos para los filtros seleccionados',
                title_font=dict(color='#B026FF')
            )
            return empty_fig, empty_fig, empty_fig, empty_fig
        
        # Crear gráfico de pastel para la distribución de sexo
        sexo_counts = filtered_df['sexo_texto'].value_counts().reset_index()
        sexo_counts.columns = ['Sexo', 'Cantidad']
        pie_fig = px.pie(
            sexo_counts, 
            values='Cantidad', 
            names='Sexo',
            color_discrete_sequence=['#B026FF', '#58FAF4'],
            hole=0.4
        )
        pie_fig.update_layout(
            plot_bgcolor='#222',
            paper_bgcolor='#222',
            font=dict(color='white'),
            margin=dict(t=10, b=10, l=10, r=10)
        )
        pie_fig.update_traces(textinfo='percent+label')
        
        # Crear gráfico de barras para la distribución de edad
        edad_counts = filtered_df['rango_edad'].value_counts().reset_index()
        edad_counts.columns = ['Rango de Edad', 'Cantidad']
        edad_counts = edad_counts.sort_values('Rango de Edad')
        bar_fig = px.bar(
            edad_counts, 
            x='Rango de Edad', 
            y='Cantidad',
            color_discrete_sequence=['#B026FF']
        )
        bar_fig.update_layout(
            plot_bgcolor='#222',
            paper_bgcolor='#222',
            font=dict(color='white'),
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis=dict(title='Rango de Edad', title_font=dict(color='white')),
            yaxis=dict(title='Frecuencia', title_font=dict(color='white'))
        )
        
        # gráfico de línea para la tendencia anual
        anio_counts = filtered_df.groupby(['anio_hecho', 'mes_hecho']).size().reset_index(name='Cantidad')
        anio_counts['Fecha'] = pd.to_datetime(anio_counts['anio_hecho'].astype(str) + '-' + anio_counts['mes_hecho'].astype(str) + '-01')
        anio_counts = anio_counts[anio_counts['anio_hecho'] >= 2015] # filtra para tener mejor visibilidad
        anio_counts = anio_counts.sort_values('Fecha')
        line_fig = px.line(
            anio_counts, 
            x='Fecha', 
            y='Cantidad',
            markers=True,
            color_discrete_sequence=['#B026FF']
        )
        line_fig.update_layout(
            plot_bgcolor='#222',
            paper_bgcolor='#222',
            font=dict(color='white'),
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis=dict(title='Fecha', title_font=dict(color='white')),
            yaxis=dict(title='Frecuencia', title_font=dict(color='white'))
        )
        
        # Crear diagrama de árbol para la frecuencia de colonias para las top 15
        colonia_counts = filtered_df['colonia_catalogo'].value_counts().reset_index()
        colonia_counts.columns = ['Colonia', 'Cantidad']
        colonia_counts = colonia_counts.sort_values('Cantidad', ascending=False).head(15)
        
        treemap_fig = px.treemap(
            colonia_counts,
            path=['Colonia'],
            values='Cantidad',
            color='Cantidad',
            color_continuous_scale=['#390c53', '#B026FF', '#E0AAFF'],
            hover_data=['Colonia', 'Cantidad']
        )
        treemap_fig.update_layout(
            plot_bgcolor='#222',
            paper_bgcolor='#222',
            font=dict(color='white'),
            margin=dict(t=10, b=10, l=10, r=10)
        )
        
        return pie_fig, bar_fig, line_fig, treemap_fig
    
    return dash_app

# Función para ser importada por app.py
def create_dashboard(server):
    return init_dashboard(server)