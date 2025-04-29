from flask import Flask, jsonify, render_template
from flask_cors import CORS  # Permitir solicitudes desde Angular

app = Flask(__name__)
CORS(app)  # Permitir solicitudes CORS (desde un servidor diferente)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    # Datos de ejemplo para el gráfico
    datos = {
        "x": [1, 2, 3, 4, 5],
        "y": [10, 15, 13, 17, 20]
    }
    return jsonify(datos)

if __name__ == '__main__':
    app.run(debug=True)
