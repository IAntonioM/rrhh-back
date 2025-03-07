from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.vinculo_familiar import VinculoFamiliarModel
from ..utils.error_handlers import handle_response
import re

vinculo_familiar_bp = Blueprint('vinculo_familiar', __name__)

def handle_sql_error(e):
    """Handles SQL errors by extracting the error message."""
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@vinculo_familiar_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_vinculo_familiar():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = VinculoFamiliarModel.create_vinculo_familiar(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@vinculo_familiar_bp.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_vinculo_familiar(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    success, message = VinculoFamiliarModel.update_vinculo_familiar(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@vinculo_familiar_bp.route('', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_vinculos_familiares():
    # Obtener filtros y paginación desde los parámetros de consulta
    filtros = {
        'vinculo': request.args.get('vinculo') or None,
        'estado': request.args.get('estado') or None,
    }
    
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Obtener lista de vínculos familiares filtrados
    vinculos_familiares_list = VinculoFamiliarModel.get_vinculos_familiares_filter(filtros, current_page, per_page)
    return jsonify({
        'success': True,
        'data': vinculos_familiares_list
    }), 200

@vinculo_familiar_bp.route('/<int:vinculo_id>', methods=['GET'])
@jwt_required()
@handle_response
def get_vinculo_familiar(vinculo_id):
    vinculo = VinculoFamiliarModel.get_vinculo_familiar(vinculo_id)
    if not vinculo:
        return jsonify({'success': False, 'message': 'Vinculo familiar no encontrado'}), 404
    return jsonify({
        'success': True,
        'data': vinculo
    }), 200

@vinculo_familiar_bp.route('/delete/<int:vinculo_id>', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_vinculo_familiar(vinculo_id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = VinculoFamiliarModel.delete_vinculo_familiar(vinculo_id, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@vinculo_familiar_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_vinculos_familiares_list():
    # Optionally accept query parameters to filter vinculos familiares (e.g., active, by vinculo, etc.)
    vinculos = VinculoFamiliarModel.get_vinculos_familiares_list_complete()
    return jsonify({
        'success': True,
        'data': vinculos
    }), 200

@vinculo_familiar_bp.route('/<int:id>/<int:estado>/estado', methods=['PATCH'])
@jwt_required()
@handle_response
def update_vinculo_familiar_status(id, estado):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    # Llamamos a la función estática para cambiar el estado del vínculo familiar
    success, message = VinculoFamiliarModel.change_vinculo_familiar_status(id, estado, current_user, request.remote_addr)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409
