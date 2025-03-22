from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.general.cargo import CargoModel  # Importa tu modelo CargoModel
from ...utils.error_handlers import handle_response
import re

cargo_bp = Blueprint('cargo', __name__)

def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@cargo_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_cargo():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = CargoModel.create_cargo(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@cargo_bp.route('/update', methods=['PUT'])
@jwt_required()
@handle_response
def update_cargo():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    success, message = CargoModel.update_cargo(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@cargo_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_cargos():

    cargos_list = CargoModel.get_cargos_list()
    return jsonify({
        'success': True,
        'data': cargos_list
    }), 200
