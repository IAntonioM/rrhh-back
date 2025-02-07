from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.centro_costo import CentroCostoModel
from ..utils.error_handlers import handle_response
import re

centro_costo_bp = Blueprint('centro_costo', __name__)

def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@centro_costo_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_centro_costo():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = CentroCostoModel.create_centro_costo(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@centro_costo_bp.route('/update', methods=['PUT'])
@jwt_required()
@handle_response
def update_centro_costo():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    success, message = CentroCostoModel.update_centro_costo(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@centro_costo_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_centros_costo():

    centros_costo_list = CentroCostoModel.get_centros_costo_list()
    return jsonify({
        'success': True,
        'data': centros_costo_list
    }), 200
