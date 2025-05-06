import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd  # Importa pandas aquí

class Dashboard:
    def __init__(self):
        self.figures = []

    def add_bar_chart(self, x, y, title="Bar Chart", xaxis_title="", yaxis_title=""):
        fig = go.Figure(data=[go.Bar(x=x, y=y)])
        fig.update_layout(title=title, xaxis_title=xaxis_title, yaxis_title=yaxis_title)
        self.figures.append(fig)

    def add_line_chart(self, x, y, title="Line Chart", xaxis_title="", yaxis_title=""):
        fig = go.Figure(data=[go.Scatter(x=x, y=y, mode='lines+markers')])
        fig.update_layout(title=title, xaxis_title=xaxis_title, yaxis_title=yaxis_title)
        self.figures.append(fig)

    def add_pie_chart(self, labels, values, title="Pie Chart"):
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_layout(title=title)
        self.figures.append(fig)

    def render_dashboard(self):
        html_parts = [
            pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
            for fig in self.figures
        ]
        return "\n".join(html_parts)

def create_dashboard_from_csv(csv_filepath="persona_fisica.csv"):
    try:
        df = pd.read_csv(csv_filepath)
        dashboard = Dashboard()

        if 'sexo' in df.columns:
            sexo_counts = df['sexo'].value_counts()
            dashboard.add_pie_chart(labels=sexo_counts.index, values=sexo_counts.values, title="Distribución por Sexo")

        if 'edad' in df.columns:
            dashboard.add_bar_chart(x=df['edad'], y=[1]*len(df), title="Distribución de Edades", xaxis_title="Edad", yaxis_title="Frecuencia")

        if 'alcaldia_catalogo' in df.columns:
            alcaldia_counts = df['alcaldia_catalogo'].value_counts().nlargest(10)
            dashboard.add_bar_chart(x=alcaldia_counts.index, y=alcaldia_counts.values, title="Top 10 Alcaldías")

        return dashboard

    except FileNotFoundError:
        return None  # O podrías lanzar una excepción
    except Exception as e:
        print(f"Error al crear el dashboard: {e}")
        return None