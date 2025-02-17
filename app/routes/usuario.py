from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.usuario import UsuarioModel
from ..utils.error_handlers import handle_response
import re

usuario_bp = Blueprint('usuario', __name__)

def handle_sql_error(e):
    """Handles SQL errors by extracting the error message."""
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@usuario_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_usuario():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = UsuarioModel.create_usuario(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@usuario_bp.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_usuario(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    data['id'] = id  # Ensure the user ID is passed for the update
    success, message = UsuarioModel.update_usuario(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@usuario_bp.route('/filtrar', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_usuarios():
    # Obtener filtros y paginación desde los parámetros de consulta
    filtros = {
        'username': request.args.get('username') or None,
        'estado': request.args.get('estado') or None,
        'rol_id': request.args.get('rol_id') or None,
    }
    
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Obtener lista de usuarios filtrados
    usuarios_list = UsuarioModel.get_usuarios_filter(filtros, current_page, per_page)
    return jsonify({
        'success': True,
        'data': usuarios_list
    }), 200

@usuario_bp.route('/<int:usuario_id>', methods=['GET'])
@jwt_required()
@handle_response
def get_usuario(usuario_id):
    usuario = UsuarioModel.get_usuario(usuario_id)
    if not usuario:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    return jsonify({
        'success': True,
        'data': usuario
    }), 200

@usuario_bp.route('/delete/<int:usuario_id>', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_usuario(usuario_id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = UsuarioModel.delete_usuario(usuario_id, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@usuario_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_usuarios_list():
    filtros = {
        'rol_id': request.args.get('rol_id') or None,
    }
    # Optionally accept query parameters to filter users (e.g., active, by role, etc.)
    usuarios = UsuarioModel.get_usuarios_list_complete(filtros)
    return jsonify({
        'success': True,
        'data': usuarios
    }), 200

@usuario_bp.route('/<int:id>/<int:estado>/estado', methods=['PATCH'])
@jwt_required()
@handle_response
def update_usuario_status(id, estado):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    # Llamamos a la función estática para cambiar el estado del usuario
    success, message = UsuarioModel.change_usuario_status(id, estado, current_user, request.remote_addr)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409
