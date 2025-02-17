from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.rol import RolModel
from ..utils.error_handlers import handle_response
import re

rol_bp = Blueprint('rol', __name__)

def handle_sql_error(e):
    """Handles SQL errors by extracting the error message."""
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@rol_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_rol():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = RolModel.create_rol(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@rol_bp.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_rol(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    success, message = RolModel.update_rol(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@rol_bp.route('/filtrar', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_roles():
    # Obtener filtros y paginación desde los parámetros de consulta
    filtros = {
        'nombre': request.args.get('nombre') or None,
        'estado': request.args.get('estado') or None,
    }
    
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Obtener lista de roles filtrados
    roles_list = RolModel.get_roles_filter(filtros, current_page, per_page)
    return jsonify({
        'success': True,
        'data': roles_list
    }), 200

@rol_bp.route('/<int:rol_id>', methods=['GET'])
@jwt_required()
@handle_response
def get_rol(rol_id):
    rol = RolModel.get_rol(rol_id)
    if not rol:
        return jsonify({'success': False, 'message': 'Rol no encontrado'}), 404
    return jsonify({
        'success': True,
        'data': rol
    }), 200

@rol_bp.route('/delete/<int:rol_id>', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_rol(rol_id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = RolModel.delete_rol(rol_id, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@rol_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_roles_list():
    # Opción de obtener todos los roles (sin filtros)
    roles = RolModel.get_roles_list_complete()
    return jsonify({
        'success': True,
        'data': roles
    }), 200

@rol_bp.route('/<int:id>/<int:estado>/estado', methods=['PATCH'])
@jwt_required()
@handle_response
def update_rol_status(id, estado):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    # Llamamos a la función estática para cambiar el estado del rol
    success, message = RolModel.change_rol_status(id, estado, current_user, request.remote_addr)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409
