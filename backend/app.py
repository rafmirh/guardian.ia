from flask import Flask, jsonify, render_template
from flask_cors import CORS  # Permitir solicitudes desde Angular
import pandas as pd

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

@app.route('/prueba1', methods=['GET'])
def prueba1():
    try:
        # Leer el archivo CSV
        df = pd.read_csv('persona_fisica.csv')  # Asegúrate de que la ruta es correcta

        # Convertir DataFrame a HTML con estilos de Bootstrap
        tabla_html = df.to_html(classes='table table-striped', index=False)

        # Renderizar el HTML en la plantilla dashboard.html
        return render_template('dashboard.html', plot_div=tabla_html)
    except FileNotFoundError:
        return "Error: El archivo persona_fisica.csv no se encontró.", 404
    except Exception as e:
        return f"Ocurrió un error al leer el archivo CSV: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)