from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.composicion_familiar import ComposicionFamiliarModel
from ..utils.error_handlers import handle_response
import re

composicion_familiar_bp = Blueprint('composicion_familiar', __name__)

def handle_sql_error(e):
    """Handles SQL errors by extracting the error message."""
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@composicion_familiar_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_composicion_familiar():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = ComposicionFamiliarModel.create_composicion_familiar(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@composicion_familiar_bp.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_composicion_familiar(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    success, message = ComposicionFamiliarModel.update_composicion_familiar(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@composicion_familiar_bp.route('', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_composiciones_familiares():
    # Obtener filtros y paginación desde los parámetros de consulta
    filtros = {
        'idEmpleado': request.args.get('idEmpleado') or None,
        'apellido_paterno': request.args.get('apellido_paterno') or None,
        'apellido_materno': request.args.get('apellido_materno') or None,
        'nombres': request.args.get('nombres') or None,
        'estado': request.args.get('estado') or None,
    }
    
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Obtener lista de composiciones familiares filtradas
    composiciones_familiares_list = ComposicionFamiliarModel.get_composiciones_familiares_filter(filtros, current_page, per_page)
    return jsonify({
        'success': True,
        'data': composiciones_familiares_list
    }), 200

@composicion_familiar_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@handle_response
def get_composicion_familiar(id):
    composicion_familiar = ComposicionFamiliarModel.get_composicion_familiar(id)
    if not composicion_familiar:
        return jsonify({'success': False, 'message': 'Composición familiar no encontrada'}), 404
    return jsonify({
        'success': True,
        'data': composicion_familiar
    }), 200

@composicion_familiar_bp.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_composicion_familiar(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = ComposicionFamiliarModel.delete_composicion_familiar(id, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@composicion_familiar_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_composiciones_familiares_list():
    # Obtener lista completa de composiciones familiares
    composiciones_familiares = ComposicionFamiliarModel.get_composiciones_familiares_list_complete()
    return jsonify({
        'success': True,
        'data': composiciones_familiares
    }), 200

@composicion_familiar_bp.route('/<int:id>/<int:estado>/estado', methods=['PATCH'])
@jwt_required()
@handle_response
def update_composicion_familiar_status(id, estado):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    # Llamamos a la función estática para cambiar el estado de la composición familiar
    success, message = ComposicionFamiliarModel.change_composicion_familiar_status(id, estado, current_user, request.remote_addr)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@composicion_familiar_bp.route('/menu', methods=['GET'])
@jwt_required()  # Si estás usando JWT para proteger la ruta
def get_composiciones_familiares_por_menu():
    filtros = {
        'menu_id': request.args.get('menu_id') or None,
    }
    composiciones_familiares_list = ComposicionFamiliarModel.get_composiciones_familiares_por_menu(filtros)
    return jsonify({
        'success': True,
        'data': composiciones_familiares_list
    }), 200
