from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os
import sys
import traceback

# Create Flask app
app = Flask(__name__)
CORS(app)

# Manejar posibles errores de importación
try:
    from dashboard import create_dashboard
    # Register Dash app with Flask
    dash_app = create_dashboard(app)
    dashboard_error = None
except Exception as e:
    # Capturar el error para mostrar un mensaje mejor
    dashboard_error = str(e)
    traceback.print_exc()
    print(f"Error al cargar el dashboard: {e}", file=sys.stderr)

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/content')
def content_page():
    return render_template('content.html')

@app.route('/perfil')
def perfil_page():
    return render_template('perfil.html')

@app.route('/trazabilidad')
def trazabilidad_page():
    return render_template('trazabilidad.html')

# The Dash app will now handle the /dashboard/ route directly.
# @app.route('/dashboard')
# def show_plotly_dashboard():
#     # Si hubo un error al cargar el dashboard, pasar el error a la plantilla
#     return render_template('dashboard.html', dashboard_error=dashboard_error if 'dashboard_error' in globals() else None)
@app.route('/dashboard-status')
def dashboard_status():
    # Endpoint para verificar el estado del dashboard desde el frontend
    if 'dashboard_error' in globals() and dashboard_error:
        return jsonify({"status": "error", "message": dashboard_error})
    else:
        return jsonify({"status": "ok"})

# Run app
if __name__ == '__main__':
    # Verificar si el archivo CSV existe
    if not os.path.exists('usurpacion_etl.csv'):
        print("ADVERTENCIA: El archivo 'usurpacion_etl.csv' no se encuentra en el directorio. El dashboard utilizará datos de muestra.")
    
    app.run(debug=True)