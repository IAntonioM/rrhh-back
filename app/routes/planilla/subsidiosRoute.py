from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.planilla.subsidiosModel import Subsidio
from ...utils.error_handlers import handle_response

subsidio_bp = Blueprint('subsidio', __name__)

@subsidio_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_subsidio():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['concepto', 'subsidiar', 'permitir']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400
    
    result = Subsidio.create_subsidio(data, current_user, request.remote_addr)
    return jsonify(result), 201 if result['success'] else 409

@subsidio_bp.route('/update', methods=['PUT'])
@jwt_required()
@handle_response
def update_subsidio():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validar idSubsidio
    if 'idSubsidio' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idSubsidio'}), 400
    
    result = Subsidio.update_subsidio(data, current_user, request.remote_addr)
    return jsonify(result), 200 if result['success'] else 409

@subsidio_bp.route('/delete', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_subsidio():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validar idSubsidio
    if 'idSubsidio' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idSubsidio'}), 400
    
    result = Subsidio.delete_subsidio(data['idSubsidio'], current_user, request.remote_addr)
    return jsonify(result), 200 if result['success'] else 409

@subsidio_bp.route('/get', methods=['POST'])
@jwt_required()
@handle_response
def get_subsidio():
    data = request.get_json()
    
    # Validar idSubsidio
    if 'idSubsidio' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idSubsidio'}), 400
    
    result = Subsidio.get_subsidio(data['idSubsidio'])
    return jsonify(result), 200 if result['success'] else 404

@subsidio_bp.route('/list', methods=['POST'])
@jwt_required()
@handle_response
def list_subsidios():
    result = Subsidio.list_subsidios()
    return jsonify(result), 200 if result['success'] else 500

@subsidio_bp.route('/count', methods=['POST'])
@jwt_required()
@handle_response
def count_subsidios():
    result = Subsidio.count_subsidios()
    return jsonify(result), 200 if result['success'] else 500