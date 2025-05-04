from flask import Flask, jsonify, render_template
from dashboard import Dashboard
from flask_cors import CORS  # Permitir solicitudes desde Angular

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
    dash = Dashboard()  # Aquí se instancia correctamente
    dashboard_html = dash.render_dashboard('prueba1.py')

    return render_template('dashboard.html', plot_div=dashboard_html)

if __name__ == '__main__':
    app.run(debug=True)
