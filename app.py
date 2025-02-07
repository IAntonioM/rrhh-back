from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS  # Importa CORS para habilitar solicitudes de diferentes orígenes
from app.models.init_db import init_db
from app.routes.periodos import periodos_bp
from app.routes.auth import auth_bp
from app.routes.empleado import empleado_bp
from app.routes.condicion_laboral import condicion_laboral_bp
from app.routes.centro_costo import centro_costo_bp
from app.routes.cargo import cargo_bp
from app.routes.ubicacion import ubicacion_bp
from app.routes.menu import menu_bp
from datetime import timedelta

def create_app():
    app = Flask(__name__)

    # Habilitar CORS para permitir solicitudes desde cualquier origen
    CORS(app)

    app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Cambiar por una clave segura
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
    jwt = JWTManager(app)

    # Registrar los Blueprints para las rutas
    app.register_blueprint(periodos_bp, url_prefix='/api/periodos')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(empleado_bp, url_prefix='/api/empleado')
    app.register_blueprint(condicion_laboral_bp, url_prefix='/api/condicion_laboral')
    app.register_blueprint(centro_costo_bp, url_prefix='/api/centro_costo')
    app.register_blueprint(cargo_bp, url_prefix='/api/cargo')
    app.register_blueprint(menu_bp, url_prefix='/api/menu')
    app.register_blueprint(ubicacion_bp, url_prefix='/api/ubicacion')

    return app

if __name__ == '__main__':
    # Inicializa la base de datos (si es necesario)
    init_db()

    # Crea y corre la aplicación
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
