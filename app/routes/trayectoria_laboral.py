from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.trayectoria_laboral import TrayectoriaLaboralModel
from ..utils.error_handlers import handle_response
import re

trayectoria_laboral_bp = Blueprint('trayectoria_laboral', __name__)

def handle_sql_error(e):
    """Handles SQL errors by extracting the error message."""
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@trayectoria_laboral_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_trayectoria_laboral():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = TrayectoriaLaboralModel.create_trayectoria_laboral(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@trayectoria_laboral_bp.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_trayectoria_laboral(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    success, message = TrayectoriaLaboralModel.update_trayectoria_laboral(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@trayectoria_laboral_bp.route('', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_trayectorias_laborales():
    # Obtener filtros y paginación desde los parámetros de consulta
    filtros = {
        'idEmpleado': request.args.get('idEmpleado') or None,
        'entidad': request.args.get('entidad') or None,
        'puesto': request.args.get('puesto') or None,
        'estado': request.args.get('estado') or None,
    }
    
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Obtener lista de trayectorias laborales filtradas
    trayectorias_laborales_list = TrayectoriaLaboralModel.get_trayectorias_laborales_filter(filtros, current_page, per_page)
    return jsonify({
        'success': True,
        'data': trayectorias_laborales_list
    }), 200

@trayectoria_laboral_bp.route('/<int:trayectoria_id>', methods=['GET'])
@jwt_required()
@handle_response
def get_trayectoria_laboral(trayectoria_id):
    trayectoria = TrayectoriaLaboralModel.get_trayectoria_laboral(trayectoria_id)
    if not trayectoria:
        return jsonify({'success': False, 'message': 'Trayectoria laboral no encontrada'}), 404
    return jsonify({
        'success': True,
        'data': trayectoria
    }), 200

@trayectoria_laboral_bp.route('/delete/<int:trayectoria_id>', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_trayectoria_laboral(trayectoria_id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = TrayectoriaLaboralModel.delete_trayectoria_laboral(trayectoria_id, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@trayectoria_laboral_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_trayectorias_laborales_list():
    # Optionally accept query parameters to filter trayectoria laborales (e.g., active, by idEmpleado, etc.)
    trayectorias = TrayectoriaLaboralModel.get_trayectorias_laborales_list_complete()
    return jsonify({
        'success': True,
        'data': trayectorias
    }), 200

@trayectoria_laboral_bp.route('/<int:id>/<int:estado>/estado', methods=['PATCH'])
@jwt_required()
@handle_response
def update_trayectoria_laboral_status(id, estado):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    # Llamamos a la función estática para cambiar el estado de la trayectoria laboral
    success, message = TrayectoriaLaboralModel.change_trayectoria_laboral_status(id, estado, current_user, request.remote_addr)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409


@trayectoria_laboral_bp.route('/menu', methods=['GET'])
@jwt_required()  # Si estás usando JWT para proteger la ruta
def get_trayectorias_laborales_por_menu():
    filtros = {
        'menu_id': request.args.get('menu_id') or None,
    }
    trayectorias_laborales_list = TrayectoriaLaboralModel.get_trayectorias_laborales_por_menu(filtros)
    return jsonify({
        'success': True,
        'data': trayectorias_laborales_list
    }), 200
