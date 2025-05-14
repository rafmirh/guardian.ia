import plotly.graph_objs as go
import pandas as pd

class Dashboard:
    def __init__(self, figure):
        self.figure = figure

    def render_dashboard(self):
        return self.figure.to_html(full_html=False)

def create_dashboard_from_csv(csv_filepath="persona_fisica.csv"):
    try:
        df = pd.read_csv(csv_filepath)

        data = []
        buttons = []
        visibility = []

        # Gráfico de pastel: Sexo
        if 'sexo' in df.columns:
            sexo_counts = df['sexo'].value_counts()
            pie_chart = go.Pie(labels=sexo_counts.index, values=sexo_counts.values, name="Distribución por Sexo", visible=True)
            data.append(pie_chart)
            visibility.append(True)

        # Gráfico de barras: Edad
        if 'edad' in df.columns:
            edad_bar = go.Bar(x=df['edad'], y=[1]*len(df), name="Distribución de Edades", visible=False)
            data.append(edad_bar)
            visibility.append(False)

        # Gráfico de barras: Alcaldías
        if 'alcaldia_catalogo' in df.columns:
            alcaldia_counts = df['alcaldia_catalogo'].value_counts().nlargest(10)
            alcaldia_bar = go.Bar(x=alcaldia_counts.index, y=alcaldia_counts.values, name="Top 10 Alcaldías", visible=False)
            data.append(alcaldia_bar)
            visibility.append(False)

        # Botones de interacción
        for i, trace in enumerate(data):
            vis = [False] * len(data)
            vis[i] = True
            button = dict(label=data[i].name, method="update", args=[{"visible": vis}, {"title": data[i].name}])
            buttons.append(button)

        # Layout
        layout = go.Layout(
            title="Dashboard Interactivo",
            updatemenus=[dict(type="buttons", direction="down", showactive=True, buttons=buttons)]
        )

        fig = go.Figure(data=data, layout=layout)
        return Dashboard(fig)

    except FileNotFoundError:
        print("Archivo CSV no encontrado.")
    except Exception as e:
        print(f"Error al crear el dashboard: {e}")
        return None