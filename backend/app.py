from flask import Flask, render_template, jsonify
from flask_cors import CORS
import pandas as pd
import os, sys
from bluesky_bot import BlueskyBot
from dotenv import load_dotenv
from datetime import datetime
from nodos import analyze_post_propagation, get_mock_data

load_dotenv()

BLUESKY_USERNAME = os.getenv('maxikilo.bsky.social')
BLUESKY_PASSWORD = os.getenv('3sja-q2r7-7ycr-s3ya')

# Initialize bot instance
bluesky_bot = BlueskyBot(BLUESKY_USERNAME, BLUESKY_PASSWORD)

# Load contacts on startup
bluesky_bot.load_contact_list()

# Crear la app Flask
app = Flask(__name__)
CORS(app)

# Manejar posibles errores de importación
try:
    from dashboard import create_dashboard
    # Register Dash app with Flask
    dash_app = create_dashboard(app)
    dashboard_error = None
except Exception as e:
    # Capturar el error para mostrar un mensaje
    dashboard_error = str(e)
    traceback.print_exc()
    print(f"Error al cargar el dashboard: {e}", file=sys.stderr)

# Rutas de Flask
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/content')
def content_page():
    return render_template('content.html')

@app.route('/perfil')
def perfil_page():
    return render_template('perfil.html')

#@app.route('/dashboard')
#def show_plotly_dashboard():
#    dashboard = create_dashboard_from_csv("persona_fisica.csv")
#    if dashboard:
#        plotly_html = dashboard.render_dashboard()
#        return render_template('dashboard.html', plot_div=plotly_html)
#    else:
#        return "Error al generar el dashboard.", 500
    
@app.route('/dashboard-status')
def dashboard_status():
    # Endpoint para verificar el estado del dashboard desde el frontend
    if 'dashboard_error' in globals() and dashboard_error:
        return jsonify({"status": "error", "message": dashboard_error})
    else:
        return jsonify({"status": "ok"})

# Add these imports to your Flask app
from flask import Flask, render_template, request, jsonify
import os
from bluesky_bot import BlueskyBot

# Initialize the bot (add this to your Flask app initialization)
# You'll need to set these environment variables or replace with your actual credentials
BLUESKY_USERNAME = os.getenv('BLUESKY_USERNAME', 'maxikilo.bsky.social')
BLUESKY_PASSWORD = os.getenv('BLUESKY_PASSWORD', '3sja-q2r7-7ycr-s3ya')

# Initialize bot instance
bluesky_bot = BlueskyBot(BLUESKY_USERNAME, BLUESKY_PASSWORD)

# Load contacts on startup
bluesky_bot.load_contact_list()

# Add/modify your trazabilidad route
@app.route('/trazabilidad', methods=['GET', 'POST'])
def trazabilidad():
    if request.method == 'GET':
        # Render the HTML template
        return render_template('trazabilidad.html')
    
    elif request.method == 'POST':
        try:
            # Get JSON data from request
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No se recibieron datos'
                }), 400
            
            message = data.get('message', '').strip()
            include_public = data.get('include_public', False)
            
            if not message:
                return jsonify({
                    'success': False,
                    'error': 'El mensaje no puede estar vacío'
                }), 400
            
            # Authenticate if not already authenticated
            if not bluesky_bot.session:
                auth_success = bluesky_bot.authenticate()
                if not auth_success:
                    return jsonify({
                        'success': False,
                        'error': 'Error de autenticación con Bluesky. Verifica las credenciales.'
                    }), 401
            
            # Add timestamp and source to message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"🤖 Guardián IA - Trazabilidad\n\n{message}\n\n📅 {timestamp}"
            
            # Broadcast message
            results = bluesky_bot.broadcast_message(
                formatted_message, 
                include_public_post=include_public
            )
            
            # Prepare response
            response_data = {
                'success': True,
                'message': 'Mensaje procesado exitosamente',
                'results': results,
                'public_post_sent': include_public
            }
            
            # Log the activity
            print(f"[{timestamp}] Message broadcasted: {results['success']}/{results['total']} sent successfully")
            
            return jsonify(response_data), 200
            
        except Exception as e:
            print(f"Error in trazabilidad route: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }), 500

# Optional: Add route to test bot connection
@app.route('/trazabilidad/test', methods=['POST'])
def test_bot_connection():
    """Test Bluesky bot connection"""
    try:
        # Test authentication
        auth_success = bluesky_bot.authenticate()
        
        if auth_success:
            return jsonify({
                'success': True,
                'message': 'Conexión con Bluesky exitosa',
                'username': bluesky_bot.username,
                'contacts_count': len(bluesky_bot.contact_list)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error de autenticación con Bluesky'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error de conexión: {str(e)}'
        }), 500
    
@app.route('/nodos')
def nodos():
    return render_template('nodos.html')

@app.route('/nodos/analyze', methods=['POST'])
def analyze_nodos():
    try:
        data = request.get_json()
        post_url = data.get('post_url', '')
        
        if not post_url:
            # Return mock data for demonstration
            graph_data = get_mock_data()
        else:
            # Analyze the actual post
            graph_data = analyze_post_propagation(post_url)
        
        return jsonify(graph_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run app
if __name__ == '__main__':
    # Verificar si el archivo CSV existe
    if not os.path.exists('usurpacion_etl.csv'):
        print("ADVERTENCIA: El archivo 'usurpacion_etl.csv' no se encuentra en el directorio. El dashboard utilizará datos de muestra.")
        
    app.run(debug=True)
