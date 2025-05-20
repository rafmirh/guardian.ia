import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from flask import Flask
import numpy as np
from dash.exceptions import PreventUpdate
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures # Importación añadida

# Cargar y preparar datos
def load_data():
    file_path = 'usurpacion_etl.csv'
    if not os.path.exists(file_path):
        print(f"ADVERTENCIA: Archivo {file_path} no encontrado. Usando datos de muestra.")
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
        df = pd.read_csv(file_path)

    df['sexo_texto'] = df['sexo'].map({0: 'Hombre', 1: 'Mujer'})
    bins = [18, 30, 40, 50, 60, 100] # Modificado: el primer bin ahora empieza en 17
    labels = ['18-29', '30-39', '40-49', '50-59', '60+'] # Modificado: etiquetas ajustadas a los nuevos bins
    df['rango_edad'] = pd.cut(df['edad'], bins=bins, labels=labels, right=False)
    return df

# Aplicación Dash
def init_dashboard(server):
    external_stylesheets = [
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=Audiowide&display=swap"
    ]

    dash_app = Dash(
        server=server,
        routes_pathname_prefix='/dashboard/',
        external_stylesheets=external_stylesheets,
        suppress_callback_exceptions=True
    )

    df = load_data()
    sexos = [{'label': 'Todos', 'value': 'Todos'}] + [{'label': s, 'value': s} for s in df['sexo_texto'].unique()]
    alcaldias = [{'label': 'Todas', 'value': 'Todas'}] + [{'label': a, 'value': a} for a in sorted(df['alcaldia_catalogo'].unique())]
    años = [{'label': 'Todos', 'value': 'Todos'}] + [{'label': str(a), 'value': a} for a in sorted(df['anio_hecho'].unique())]
    meses = [{'label': 'Todos', 'value': 'Todos'}] + [{'label': str(m), 'value': m} for m in range(1, 13)]

    dash_app.layout = html.Div([
        # CSS adicional
        html.Link(rel='stylesheet', href='/static/css/dashboard.css'),

        # Header personalizado
        html.Div([
            html.Div(className='header_nav', children=[
                html.Div(className='contenedor', children=[
                    html.H1("Guardian IA", style={'fontFamily': 'Audiowide, cursive'}),
                    html.Nav([
                        html.A("Contenido", href="/content"),
                        html.A("Perfil de riesgo", href="/perfil"),
                        html.A("Trazabilidad", href="/trazabilidad")
                    ])
                ])
            ])
        ], className='bg_animate'),

        # Contenido del dashboard
        dbc.Container([
            
            dbc.Row([
                dbc.Col([
                    html.Label("Sexo:", style={'color': '#ffffff'}),
                    dcc.Dropdown(id='sexo-filter', options=sexos, value='Todos', 
                        className='mb-3', style={'backgroundColor': '#222', 'color': '#000'})
                ], width=3),
                dbc.Col([
                    html.Label("Alcaldía:", style={'color': '#ffffff'}),
                    dcc.Dropdown(id='alcaldia-filter', options=alcaldias, value='Todas', 
                        className='mb-3', style={'backgroundColor': '#222', 'color': '#000'})
                ], width=3),
                dbc.Col([
                    html.Label("Año:", style={'color': '#ffffff'}),
                    dcc.Dropdown(id='anio-filter', options=años, value='Todos', 
                        className='mb-3', style={'backgroundColor': '#222', 'color': '#000'})
                ], width=3),
                dbc.Col([
                    html.Label("Mes:", style={'color': '#ffffff'}),
                    dcc.Dropdown(id='mes-filter', options=meses, value='Todos', 
                        className='mb-3', style={'backgroundColor': '#222', 'color': '#000'})
                ], width=3)
            ], className="mb-4"),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Distribución por Sexo", style={'backgroundColor': '#390c53', 'color': 'white'}),
                        dbc.CardBody([dcc.Graph(id='pie-sexo', style={'height': '30vh'}, config={'responsive': True})])
                    ], style={'height': '100%', 'backgroundColor': '#222', 'borderColor': '#B026FF'})
                ], width=4),

                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Distribución por Edad", style={'backgroundColor': '#390c53', 'color': 'white'}),
                        dbc.CardBody([dcc.Graph(id='bar-edad', style={'height': '30vh'}, config={'responsive': True})])
                    ], style={'height': '100%', 'backgroundColor': '#222', 'borderColor': '#B026FF'})
                ], width=4)
            ], className="mb-4"),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Tendencia por Año", style={'backgroundColor': '#390c53', 'color': 'white'}),
                        dbc.CardBody([dcc.Graph(id='line-anio', style={'height': '30vh'}, config={'responsive': True})])
                    ], style={'height': '100%', 'backgroundColor': '#222', 'borderColor': '#B026FF'})
                ], width=4),

                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Distribución por Colonia", style={'backgroundColor': '#390c53', 'color': 'white'}),
                        dbc.CardBody([dcc.Graph(id='treemap-colonia', style={'height': '30vh'}, config={'responsive': True})])
                    ], style={'height': '100%', 'backgroundColor': '#222', 'borderColor': '#B026FF'})
                ], width=4)
            ])
        ], fluid=True, style={'backgroundColor': '#0d1117', 'minHeight': '100vh', 'padding': '20px'})
    ])

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
        filtered_df = df.copy()
        if sexo != 'Todos': filtered_df = filtered_df[filtered_df['sexo_texto'] == sexo]
        if alcaldia != 'Todas': filtered_df = filtered_df[filtered_df['alcaldia_catalogo'] == alcaldia]
        if anio != 'Todos': filtered_df = filtered_df[filtered_df['anio_hecho'] == anio]
        if mes != 'Todos': filtered_df = filtered_df[filtered_df['mes_hecho'] == mes]

        if filtered_df.empty:
            empty_fig = go.Figure()
            empty_fig.update_layout(
                plot_bgcolor='#222', paper_bgcolor='#222',
                font=dict(color='white'),
                title_text='No hay datos para los filtros seleccionados',
                title_font=dict(color='#B026FF')
            )
            return empty_fig, empty_fig, empty_fig, empty_fig

        sexo_counts = filtered_df['sexo_texto'].value_counts().reset_index()
        sexo_counts.columns = ['Sexo', 'Cantidad']
        pie_fig = px.pie(sexo_counts, values='Cantidad', names='Sexo',
                         color_discrete_sequence=['#B026FF', '#58FAF4'], hole=0.4)
        pie_fig.update_layout(plot_bgcolor='#222', paper_bgcolor='#222', font=dict(color='white'),
                              margin=dict(t=10, b=10, l=10, r=10))
        pie_fig.update_traces(textinfo='percent+label')

        edad_counts = filtered_df['rango_edad'].value_counts().reset_index()
        edad_counts.columns = ['Rango de Edad', 'Cantidad']
        edad_counts = edad_counts.sort_values('Rango de Edad')
        bar_fig = px.bar(edad_counts, x='Rango de Edad', y='Cantidad',
                         color_discrete_sequence=['#B026FF'])
        bar_fig.update_layout(plot_bgcolor='#222', paper_bgcolor='#222', font=dict(color='white'),
                              margin=dict(t=10, b=10, l=10, r=10),
                              xaxis=dict(title='Rango de Edad', title_font=dict(color='white')),
                              yaxis=dict(title='Frecuencia', title_font=dict(color='white')))

        anio_counts = filtered_df.groupby(['anio_hecho', 'mes_hecho']).size().reset_index(name='Cantidad')
        anio_counts['Fecha'] = pd.to_datetime(anio_counts['anio_hecho'].astype(str) + '-' + anio_counts['mes_hecho'].astype(str) + '-01')
        anio_counts = anio_counts[anio_counts['anio_hecho'] >= 2018].sort_values('Fecha')
        
        line_fig = px.line(anio_counts, x='Fecha', y='Cantidad',
                           markers=True, color_discrete_sequence=['#B026FF'])
        line_fig.update_layout(plot_bgcolor='#222', paper_bgcolor='#222', font=dict(color='white'),
                               margin=dict(t=10, b=10, l=10, r=10),
                               showlegend=False, # Ocultar leyenda para este gráfico
                               xaxis=dict(title='Fecha', title_font=dict(color='white')),
                               yaxis=dict(title='Frecuencia', title_font=dict(color='white')))

        # Añadir línea de tendencia polinómica de 3er grado si hay suficientes datos (al menos 4 puntos)
        if not anio_counts.empty and len(anio_counts) >= 4:
            # Preparar datos para la regresión (X original son los números ordinales de las fechas)
            X_reg = anio_counts['Fecha'].map(pd.Timestamp.toordinal).values.reshape(-1, 1)
            y_reg = anio_counts['Cantidad'].values

            # Crear características polinómicas de grado 3
            poly = PolynomialFeatures(degree=3)
            X_poly_reg = poly.fit_transform(X_reg)

            model = LinearRegression()
            model.fit(X_poly_reg, y_reg)

            # Generar fechas para la línea de tendencia extendida (Ene 2018 - Ago 2024)
            start_date_trend = pd.Timestamp('2018-01-01')
            end_date_trend = pd.Timestamp('2025-12-01') # Extender hasta Diciembre de 2025
            trend_dates = pd.date_range(start=start_date_trend, end=end_date_trend, freq='MS') # MS para inicio de mes

            X_trend_ordinal = trend_dates.map(pd.Timestamp.toordinal).values.reshape(-1, 1)
            # Transformar las fechas de la tendencia a características polinómicas
            X_poly_trend = poly.transform(X_trend_ordinal)
            y_trend_pred = model.predict(X_poly_trend)
            y_trend_pred = np.maximum(0, y_trend_pred) # Evitar predicciones negativas para cantidades

            # Simular efecto neón: línea de brillo (detrás)
            line_fig.add_trace(go.Scatter(
                x=trend_dates,
                y=y_trend_pred,
                mode='lines',
                line=dict(color='rgba(255, 255, 150, 0.4)', width=7), # Amarillo pálido, más ancho, semitransparente
                hoverinfo='skip',
                showlegend=False 
            ))
            # Línea de tendencia principal (amarilla, encima)
            line_fig.add_trace(go.Scatter(
                x=trend_dates,
                y=y_trend_pred,
                mode='lines',
                line=dict(color='yellow', width=3),
                showlegend=False # Asegurar que esta traza no aparezca en leyenda
            ))
            
            # Ajustar el rango del eje X para asegurar que toda la tendencia sea visible
            min_data_date = anio_counts['Fecha'].min()
            max_data_date = anio_counts['Fecha'].max()
            
            overall_min_x = min(min_data_date, start_date_trend)
            overall_max_x = max(max_data_date, end_date_trend)
            line_fig.update_xaxes(range=[overall_min_x, overall_max_x])

        colonia_counts = filtered_df['colonia_catalogo'].value_counts().reset_index()
        colonia_counts.columns = ['Colonia', 'Cantidad']
        colonia_counts = colonia_counts.sort_values('Cantidad', ascending=False).head(15)
        treemap_fig = px.treemap(colonia_counts, path=['Colonia'], values='Cantidad',
                                 color='Cantidad', color_continuous_scale=['#390c53', '#B026FF', '#E0AAFF'])
        treemap_fig.update_layout(plot_bgcolor='#222', paper_bgcolor='#222', font=dict(color='white'),
                                  margin=dict(t=10, b=10, l=10, r=10))

        return pie_fig, bar_fig, line_fig, treemap_fig

    return dash_app

# Función para ser importada por app.py
def create_dashboard(server):
    return init_dashboard(server)
