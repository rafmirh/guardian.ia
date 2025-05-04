from flask import Flask, render_template
import pandas as pd
from dashboard import Dashboard  # Asegúrate de que 'dashboard.py' esté en el mismo directorio

app = Flask(__name__)

@app.route('/dashboard')
def show_plotly_dashboard():
    try:
        df = pd.read_csv('persona_fisica.csv')

        dashboard = Dashboard()

        # Gráfico de barras: Conteo de delitos
        delito_counts = df['delito'].value_counts().nlargest(10) # Mostrar los 10 delitos más comunes
        dashboard.add_bar_chart(x=delito_counts.index, y=delito_counts.values, title="Top 10 Delitos")

        # Gráfico de pastel: Distribución por sexo
        sexo_counts = df['sexo'].value_counts()
        dashboard.add_pie_chart(labels=sexo_counts.index, values=sexo_counts.values, title="Distribución por Sexo")

        # Histograma: Distribución de edades
        dashboard.add_bar_chart(x=df['edad'], y=[1]*len(df), title="Distribución de Edades", xaxis_title="Edad", yaxis_title="Frecuencia")

        # Gráfico de barras: Conteo por tipo de persona
        tipo_persona_counts = df['tipo_persona'].value_counts()
        dashboard.add_bar_chart(x=tipo_persona_counts.index, y=tipo_persona_counts.values, title="Distribución por Tipo de Persona")

        # Gráfico de barras: Conteo por alcaldía (top 10)
        alcaldia_counts = df['alcaldia_catalogo'].value_counts().nlargest(10)
        dashboard.add_bar_chart(x=alcaldia_counts.index, y=alcaldia_counts.values, title="Top 10 Alcaldías")

        plotly_html = dashboard.render_dashboard()
        return render_template('plotly_dashboard.html', plotly_div=plotly_html)

    except FileNotFoundError:
        return "Error: El archivo persona_fisica.csv no se encontró.", 404
    except Exception as e:
        return f"Ocurrió un error: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)