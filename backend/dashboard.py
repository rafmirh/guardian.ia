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

        # Gráfico de pastel: Sexo
        if 'sexo' in df.columns:
            sexo_counts = df['sexo'].value_counts()
            pie_chart = go.Pie(labels=sexo_counts.index, values=sexo_counts.values, name="Distribución por Sexo", visible=True)
            data.append(pie_chart)

        # Gráfico de barras: Edades detalladas
        if 'edad' in df.columns:
            edad_counts = df['edad'].value_counts().sort_index()
            edad_bar = go.Bar(x=edad_counts.index, y=edad_counts.values, name="Distribución de Edades", visible=False)
            data.append(edad_bar)

        # Gráfico de barras: Alcaldías (Top 10)
        if 'alcaldia_catalogo' in df.columns:
            df['alcaldia_catalogo'] = df['alcaldia_catalogo'].astype(str).str.strip()
            alcaldia_counts = df['alcaldia_catalogo'][df['alcaldia_catalogo'] != ''].value_counts().nlargest(10)
            alcaldia_bar = go.Bar(x=alcaldia_counts.index, y=alcaldia_counts.values, name="Top 10 Alcaldías", visible=False)
            data.append(alcaldia_bar)

        # Botones para cambiar entre gráficos
        for i, trace in enumerate(data):
            vis = [False] * len(data)
            vis[i] = True
            button = dict(label=trace.name, method="update", args=[{"visible": vis}, {"title": trace.name}])
            buttons.append(button)

        layout = go.Layout(
            title="Dashboard Interactivo",
            updatemenus=[dict(type="buttons", direction="down", buttons=buttons, showactive=True)]
        )

        fig = go.Figure(data=data, layout=layout)
        return Dashboard(fig)

    except FileNotFoundError:
        print("Archivo CSV no encontrado.")
    except Exception as e:
        print(f"Error al crear el dashboard: {e}")
        return None