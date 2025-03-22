from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.planilla.condicion_laboral import CondicionLaboralModel
from ...utils.error_handlers import handle_response
import re

condicion_laboral_bp = Blueprint('condicion_laboral', __name__)

def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@condicion_laboral_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_condicion_laboral():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = CondicionLaboralModel.create_condicion_laboral(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@condicion_laboral_bp.route('/update', methods=['PUT'])
@jwt_required()
@handle_response
def update_condicion_laboral():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    success, message = CondicionLaboralModel.update_condicion_laboral(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@condicion_laboral_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_condiciones_laborales():

    condiciones_list = CondicionLaboralModel.get_condiciones_laborales_list()
    return jsonify({
        'success': True,
        'data': condiciones_list
    }), 200
