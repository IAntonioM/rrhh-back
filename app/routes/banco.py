from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.banco import BancoModel
from ..utils.error_handlers import handle_response
import re

banco_bp = Blueprint('banco', __name__)

def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@banco_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_banco():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = BancoModel.create_banco(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@banco_bp.route('/update', methods=['PUT'])
@jwt_required()
@handle_response
def update_banco():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    success, message = BancoModel.update_banco(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@banco_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_bancos():
    filtros = {
        'flag_estado': request.args.get('flag_estado') or None
    }
    bancos_list = BancoModel.get_bancos_list(filtros)
    return jsonify({
        'success': True,
        'data': bancos_list
    }), 200
