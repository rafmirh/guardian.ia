from flask import Flask, jsonify, render_template
from dashboard import create_dashboard
from flask_cors import CORS  # Permitir solicitudes desde Angular

app = Flask(__name__)
CORS(app)  # Permitir solicitudes CORS (desde un servidor diferente)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/content', methods=['GET'])
def content_page():
    return render_template('content.html')  

@app.route('/dashboard', methods=['GET'])
def dashboard():
    plot_div = create_dashboard()
    return render_template('dashboard.html', plot_div=plot_div)

if __name__ == '__main__':
    app.run(debug=True)
