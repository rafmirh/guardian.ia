from flask import Flask, render_template
from flask_cors import CORS
from dashboard import create_dashboard_from_csv
from dash import dash_table  # Importar Dash Table si la quieres
import pandas as pd

app = Flask(__name__)
CORS(app)

# Integrar Dash Table en Flask
create_dash_table(app)

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
    dashboard = create_dashboard_from_csv("persona_fisica.csv")
    if dashboard:
        plotly_html = dashboard.render_dashboard()
        return render_template('dashboard.html', plot_div=plotly_html)
    else:
        return "Error al generar el dashboard.", 500

if __name__ == '__main__':
    app.run(debug=True)