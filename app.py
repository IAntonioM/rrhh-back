from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.models.init_db import init_db
from app.routes import register_blueprints
from datetime import timedelta
from dotenv import load_dotenv
import os
import pytz

def create_app():
    app = Flask(__name__)
    load_dotenv()
    
    # Habilitar CORS
    CORS(app)
    
    # Obtener la zona horaria desde .env
    APP_TIMEZONE = os.getenv('APP_TIMEZONE', 'UTC')
    timezone = pytz.timezone(APP_TIMEZONE)
    
    # Configuración de JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 120)))
    jwt = JWTManager(app)
    
    # Manejador de error personalizado para el token expirado
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Tu sesión ha expirado. Por favor, vuelve a iniciar sesión.'
        }), 401
    
    # Registrar los Blueprints desde el módulo de rutas
    register_blueprints(app)
    
    return app

if __name__ == '__main__':
    init_db()  # Inicializa la base de datos
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
