from flask import Flask, render_template
from flask_cors import CORS  # Permitir solicitudes desde Angular
import pandas as pd
from dashboard import create_dashboard_from_csv  # Importa la función

app = Flask(__name__)
CORS(app)  # Permitir solicitudes CORS (desde un servidor diferente)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/content', methods=['GET'])
def content_page():
    return render_template('content.html')

@app.route('/perfil', methods=['GET'])
def perfil_page():
    return render_template('perfil.html')

@app.route('/dashboard', methods=['GET'])
def show_plotly_dashboard():
    dashboard = create_dashboard_from_csv("persona_fisica.csv") # Especifica la ruta del CSV si es necesario
    if dashboard:
        plotly_html = dashboard.render_dashboard()
        return render_template('dashboard.html', plot_div=plotly_html)
    else:
        return "Error al generar el dashboard.", 500

if __name__ == '__main__':
    app.run(debug=True)