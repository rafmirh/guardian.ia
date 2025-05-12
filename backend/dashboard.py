import plotly.graph_objs as go
import pandas as pd

def create_interactive_dashboard(csv_filepath="persona_fisica.csv"):
    try:
        df = pd.read_csv(csv_filepath)

        # Listas para almacenar cada gráfico
        data = []
        buttons = []
        visibility = []

        # Gráfico de pastel: Distribución por Sexo
        if 'sexo' in df.columns:
            sexo_counts = df['sexo'].value_counts()
            pie_chart = go.Pie(labels=sexo_counts.index, values=sexo_counts.values, name="Distribución por Sexo", visible=True)
            data.append(pie_chart)
            visibility.append(True)

        # Gráfico de barras: Distribución de Edades
        if 'edad' in df.columns:
            edad_bar = go.Bar(x=df['edad'], y=[1]*len(df), name="Distribución de Edades", visible=False)
            data.append(edad_bar)
            visibility.append(False)

        # Gráfico de barras: Top 10 Alcaldías
        if 'alcaldia_catalogo' in df.columns:
            alcaldia_counts = df['alcaldia_catalogo'].value_counts().nlargest(10)
            alcaldia_bar = go.Bar(x=alcaldia_counts.index, y=alcaldia_counts.values, name="Top 10 Alcaldías", visible=False)
            data.append(alcaldia_bar)
            visibility.append(False)

        # Botones para controlar visibilidad
        for i, trace in enumerate(data):
            vis = [False] * len(data)
            vis[i] = True
            button = dict(label=data[i].name,
                          method="update",
                          args=[{"visible": vis},
                                {"title": data[i].name}])
            buttons.append(button)

        # Layout con botones
        layout = go.Layout(
            title="Dashboard Interactivo",
            updatemenus=[dict(type="buttons", direction="down", showactive=True, buttons=buttons)]
        )

        # Figura final
        fig = go.Figure(data=data, layout=layout)
        fig.show()

    except FileNotFoundError:
        print("Archivo CSV no encontrado.")
    except Exception as e:
        print(f"Error al crear el dashboard: {e}")

# Llamar a la función
create_interactive_dashboard("persona_fisica.csv")