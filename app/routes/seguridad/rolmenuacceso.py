from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.seguridad.rol_menu_acceso import RolMenuAccesoModel
from ...utils.error_handlers import handle_response
from ...models.seguridad.usuario import UsuarioModel
import re

rol_menu_acceso_bp = Blueprint('rol_menu_acceso', __name__)

def handle_sql_error(e):
    """Handles SQL errors by extracting the error message."""
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@rol_menu_acceso_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_rol_menu_acceso():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = RolMenuAccesoModel.save_rol_menu_acceso(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@rol_menu_acceso_bp.route('/consultar', methods=['GET'])
@jwt_required()
@handle_response
def consultar_rol_menu_acceso():
    rol_id = request.args.get('rol_id')
    menu_id = request.args.get('menu_id')
    acceso_id = request.args.get('acceso_id')

    if not rol_id:
        return jsonify({'success': False, 'message': 'Parámetros faltantes (rol_id)'}), 400

    rol_id = int(rol_id)
    menu_id = int(menu_id) if menu_id else None
    acceso_id = int(acceso_id) if acceso_id else None

    data = RolMenuAccesoModel.get_rol_menu_acceso(rol_id, menu_id, acceso_id)

    return jsonify({
        'success': True,
        'data': data
    }), 200

@rol_menu_acceso_bp.route('/consultarUserCurrent', methods=['GET'])
@jwt_required()
@handle_response
def consultar_rol_menu_acceso_user_current():
    # Obtener el usuario autenticado desde el token JWT
    menu_id = request.args.get('menu_id')
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    # Consultar el rol del usuario en la base de datos
    usuario = UsuarioModel.get_by_username(current_user)
    if not usuario:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    rol_id = usuario['rol_id']  # Obtener el rol_id del usuario

    # Consultar los accesos del rol
    data = RolMenuAccesoModel.get_rol_menu_acceso(rol_id,menu_id)

    return jsonify({
        'success': True,
        'data': data
    }), 200
