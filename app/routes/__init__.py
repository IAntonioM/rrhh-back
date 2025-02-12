from flask import Blueprint

from app.routes.periodos import periodos_bp
from app.routes.auth import auth_bp
from app.routes.empleado import empleado_bp
from app.routes.condicion_laboral import condicion_laboral_bp
from app.routes.centro_costo import centro_costo_bp
from app.routes.cargo import cargo_bp
from app.routes.ubicacion import ubicacion_bp
from app.routes.menu import menu_bp
from app.routes.conceptosMuni import conceptos_muni_bp
from app.routes.emp_concepto import emp_concepto_bp
from app.routes.banco import banco_bp
from app.routes.sede import sede_bp
from app.routes.regimenPensionarioSUNAT import regimen_pensionario_bp
from app.routes.Egresos import egresos
from app.routes.Ingresos import ingresos

# Función para registrar todas las rutas
def register_blueprints(app):
    app.register_blueprint(periodos_bp, url_prefix='/api/periodos')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(empleado_bp, url_prefix='/api/empleado')
    app.register_blueprint(condicion_laboral_bp, url_prefix='/api/condicion_laboral')
    app.register_blueprint(centro_costo_bp, url_prefix='/api/centro_costo')
    app.register_blueprint(cargo_bp, url_prefix='/api/cargo')
    app.register_blueprint(menu_bp, url_prefix='/api/menu')
    app.register_blueprint(ubicacion_bp, url_prefix='/api/ubicacion')
    app.register_blueprint(conceptos_muni_bp, url_prefix='/api/conceptosMuni')
    app.register_blueprint(emp_concepto_bp, url_prefix='/api/emp_concepto')
    app.register_blueprint(banco_bp, url_prefix='/api/banco')
    app.register_blueprint(sede_bp, url_prefix='/api/sede')
    app.register_blueprint(regimen_pensionario_bp, url_prefix='/api/regimen_pensionario_sunat')
    app.register_blueprint(egresos, url_prefix='/api/egresos')
    app.register_blueprint(ingresos, url_prefix='/api/ingresos')
