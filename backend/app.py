from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import os, sys
import traceback # Added import
from bluesky_bot import BlueskyBot
from dotenv import load_dotenv
from datetime import datetime
from nodos import analyze_post_propagation, get_mock_data
from perfil import leer_datos_csv, calcular_probabilidad_riesgo, validar_inputs, obtener_alcaldias


load_dotenv()
app = Flask(__name__) # Moved Flask app initialization up
CORS(app)

# Correctly initialize Bluesky Bot once using .env variables
# These environment variables (BLUESKY_USERNAME, BLUESKY_PASSWORD) should be defined in your .env file
BLUESKY_USERNAME_ENV = os.getenv('BLUESKY_USERNAME')
BLUESKY_PASSWORD_ENV = os.getenv('BLUESKY_PASSWORD')

# Initialize bot instance
bluesky_bot = BlueskyBot(BLUESKY_USERNAME_ENV, BLUESKY_PASSWORD_ENV)
# Load contacts on startup
bluesky_bot.load_contact_list()

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

# Modificar la ruta existente /perfil para manejar GET y POST
@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    alcaldias = obtener_alcaldias()
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            sexo = int(request.form.get('sexo', -1))
            edad = int(request.form.get('edad', -1))
            alcaldia_idx = int(request.form.get('alcaldia', -1))
            
            # Validar inputs
            if not validar_inputs(sexo, edad, alcaldia_idx):
                return render_template('perfil.html', 
                                     alcaldias=alcaldias, 
                                     error="Introducir datos válidos")
            
            # Leer datos y calcular probabilidad
            df = leer_datos_csv()
            probabilidad = calcular_probabilidad_riesgo(sexo, edad, alcaldia_idx, df)
            
            return render_template('perfil.html', 
                                 alcaldias=alcaldias, 
                                 probabilidad=probabilidad)
        
        except (ValueError, TypeError):
            return render_template('perfil.html', 
                                 alcaldias=alcaldias, 
                                 error="Introducir datos válidos")
        except Exception:
            return render_template('perfil.html', 
                                 alcaldias=alcaldias, 
                                 error="Error interno del servidor")
    
    # Método GET - mostrar formulario vacío
    return render_template('perfil.html', alcaldias=alcaldias, enumerate=enumerate)

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

# Load contacts on startup

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
@app.route('/trazabilidad/get_bot_feed', methods=['GET'])
def get_bot_feed():
    """Endpoint to get the bot's own feed."""
    if not bluesky_bot.session:
        # Attempt to authenticate if not already
        if not bluesky_bot.authenticate():
            return jsonify({'success': False, 'error': 'Bluesky authentication failed', 'username': bluesky_bot.username}), 500

    limit = request.args.get('limit', 10, type=int) # Get 10 posts by default
    feed_items = bluesky_bot.get_user_feed(limit=limit)

    if feed_items is not None:
        return jsonify({'success': True, 'feed': feed_items, 'username': bluesky_bot.username})
    else:
        # feed_items is None, meaning bluesky_bot.get_user_feed() returned None.
        # This happens if authentication within get_user_feed fails, or if the API call to getAuthorFeed fails.
        if not bluesky_bot.session or not bluesky_bot.session.get('accessJwt'):
            error_message = f"Bluesky authentication failed for user {bluesky_bot.username}. Please check credentials in .env or Bluesky service status."
        else:
            # Session exists, so authentication was successful at some point, but fetching feed failed.
            error_message = f"Failed to fetch feed for {bluesky_bot.username} from Bluesky. The account might have no posts visible via API, or there could be a temporary API issue."
        return jsonify({'success': False, 'error': error_message, 'username': bluesky_bot.username}), 500


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
