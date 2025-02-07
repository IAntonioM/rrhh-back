from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.menu import MenuModel
from ..utils.error_handlers import handle_response
import re

menu_bp = Blueprint('menu', __name__)

def handle_sql_error(e):
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

@menu_bp.route('/update', methods=['PUT'])
@jwt_required()
@handle_response
def update_menu():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    success, message = MenuModel.update_menu(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@menu_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_menus():
    menus_list = MenuModel.get_menus_list()
    return jsonify({
        'success': True,
        'data': menus_list
    }), 200
