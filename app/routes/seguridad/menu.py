from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.seguridad.menu import MenuModel
from ...utils.error_handlers import handle_response
import re

menu_bp = Blueprint('menu', __name__)

def handle_sql_error(e):
    """Handles SQL errors by extracting the error message."""
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@menu_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_menu():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = MenuModel.create_menu(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@menu_bp.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_menu(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    success, message = MenuModel.update_menu(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@menu_bp.route('/filtrar', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_menus():
    # Obtener filtros y paginación desde los parámetros de consulta
    filtros = {
        'nombre': request.args.get('nombre') or None,
    }
    
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Obtener lista de menús filtrados
    menus_list = MenuModel.get_menus_filter(filtros, current_page, per_page)
    return jsonify({
        'success': True,
        'data': menus_list
    }), 200


@menu_bp.route('/<int:menu_id>', methods=['GET'])
@jwt_required()
@handle_response
def get_menu(menu_id):
    menu = MenuModel.get_menu(menu_id)
    if not menu:
        return jsonify({'success': False, 'message': 'Menu no encontrado'}), 404
    return jsonify({
        'success': True,
        'data': menu
    }), 200

@menu_bp.route('/delete/<int:menu_id>', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_menu(menu_id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = MenuModel.delete_menu(menu_id, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409


@menu_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_menus_list():
    filtros = {
        'padre_id': request.args.get('padre_id') or None,
    }
    # Optionally accept query parameters to filter menus (e.g., active, by parent_id, etc.)
    menus = MenuModel.get_menus_list_complete(filtros)
    return jsonify({
        'success': True,
        'data': menus
    }), 200
    
@menu_bp.route('/<int:id>/<int:estado>/estado', methods=['PATCH'])
@jwt_required()
@handle_response
def update_menu_status(id, estado):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    # Llamamos a la función estática para cambiar el estado del menú
    success, message = MenuModel.change_menu_status(id, estado, current_user, request.remote_addr)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409
