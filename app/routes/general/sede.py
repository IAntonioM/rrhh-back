from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.general.sede import SedeModel
from ...utils.error_handlers import handle_response
import re

sede_bp = Blueprint('sede', __name__)

def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@sede_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_sede():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = SedeModel.create_sede(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@sede_bp.route('/update', methods=['PUT'])
@jwt_required()
@handle_response
def update_sede():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = SedeModel.update_sede(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@sede_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_sedes():
    filtros = {
        'flag_estado': request.args.get('flag_estado') or None
    }
    sedes_list = SedeModel.get_sedes_list(filtros)
    return jsonify({
        'success': True,
        'data': sedes_list
    }), 200
