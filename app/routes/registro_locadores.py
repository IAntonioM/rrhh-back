from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.registro_locadores import RegistroLocadoresModel
from ..utils.error_handlers import handle_response
import re

registro_locadores_bp = Blueprint('registro_locadores', __name__)

def handle_sql_error(e):
    """Maneja los errores de SQL extrayendo el mensaje de error."""
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@registro_locadores_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_registro_locadores():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = RegistroLocadoresModel.register_locador(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@registro_locadores_bp.route('/update/<uuid:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_registro_locadores(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    data['id'] = id  # Incluimos el ID en los datos para la actualización
    success, message = RegistroLocadoresModel.update_locador(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@registro_locadores_bp.route('', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_registros_locadores():
    # Obtener filtros y paginación desde los parámetros de consulta
    filtros = {
        'id_datos_personales': request.args.get('id_datos_personales') or None,
        'id_area': request.args.get('id_area') or None,
        'id_cargo': request.args.get('id_cargo') or None,
        'tipo': request.args.get('tipo') or None,
        'estado': request.args.get('estado') or None,
        'fecha': request.args.get('fecha') or None,
        'anio': request.args.get('anio') or None,
        'mes': request.args.get('mes') or None,
    }
    
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Obtener lista de registros locadores filtrados
    registros_locadores_list = RegistroLocadoresModel.get_locadores_by_filter(filtros, current_page, per_page)
    return jsonify({
        'success': True,
        'data': registros_locadores_list
    }), 200
