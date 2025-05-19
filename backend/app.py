from flask import Flask, render_template
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
CORS(app)

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

@app.route('/dashboard')
def show_plotly_dashboard():
    return render_template('dashboard.html')


# Run app
if __name__ == '__main__':
    app.run(debug=True)
