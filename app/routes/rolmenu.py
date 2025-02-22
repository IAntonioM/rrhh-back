from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.rol_menu import RolMenuModel
from ..utils.error_handlers import handle_response
from ..models.usuario import UsuarioModel
import re

rol_menu_bp = Blueprint('rol_menu', __name__)

def handle_sql_error(e):
    """Handles SQL errors by extracting the error message."""
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@rol_menu_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_rol_menu():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = RolMenuModel.save_rol_menu(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@rol_menu_bp.route('/consultar', methods=['GET'])
@jwt_required()
@handle_response
def consultar_rol_menu():
    rol_id = request.args.get('rol_id')
    if not rol_id :
        return jsonify({'success': False, 'message': 'Parámetros faltantes (rol_id)'}), 400

    rol_id = int(rol_id)

    data = RolMenuModel.get_rol_menu(rol_id)

    return jsonify({
        'success': True,
        'data': data
    }), 200
    
@rol_menu_bp.route('/consultarUserCurrent', methods=['GET'])
@jwt_required()
@handle_response
def consultar_rol_menu_user_current():
    # Obtener el usuario autenticado desde el token JWT
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404


    print(current_user)
    # Consultar el rol del usuario en la base de datos
    usuario = UsuarioModel.get_by_username(current_user)
    print(usuario)
    if not usuario:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    rol_id = usuario['rol_id']  # Obtener el rol_id del usuario

    print(usuario)
    # Consultar el menú del rol
    data = RolMenuModel.get_rol_menu(rol_id)

    return jsonify({
        'success': True,
        'data': data
    }), 200

