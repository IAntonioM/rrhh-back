from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.general.estado_civil import EstadoCivilModel
from ...utils.error_handlers import handle_response
import re

estado_civil_bp = Blueprint('estado_civil', __name__)

def handle_sql_error(e):
    """Handles SQL errors by extracting the error message."""
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@estado_civil_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_estado_civil():
    """Crea un nuevo estado civil."""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = EstadoCivilModel.create_estado_civil(data)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@estado_civil_bp.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_estado_civil(id):
    """Actualiza un estado civil existente."""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    data['idEstadoCivil'] = id  # Aseguramos que el id sea el correcto para la actualización
    success, message = EstadoCivilModel.update_estado_civil(data)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@estado_civil_bp.route('', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_estado_civiles():
    """Obtiene la lista de estados civiles con filtros y paginación."""
    filtros = {
        'estadoCivil': request.args.get('estadoCivil') or None,
        'flag_estado': request.args.get('flag_estado') or None,
    }
    
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Obtener lista de estados civiles filtrados
    estado_civiles_list = EstadoCivilModel.get_estado_civiles_filter(filtros, current_page, per_page)
    return jsonify({
        'success': True,
        'data': estado_civiles_list
    }), 200

@estado_civil_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@handle_response
def get_estado_civil(id):
    """Obtiene un estado civil por su ID."""
    estado_civil = EstadoCivilModel.get_estado_civil(id)
    if not estado_civil:
        return jsonify({'success': False, 'message': 'Estado civil no encontrado'}), 404
    return jsonify({
        'success': True,
        'data': estado_civil
    }), 200

@estado_civil_bp.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_estado_civil(id):
    """Elimina un estado civil."""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = EstadoCivilModel.delete_estado_civil(id)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@estado_civil_bp.route('/<int:id>/<string:estado>/estado', methods=['PATCH'])
@jwt_required()
@handle_response
def update_estado_civil_status(id, estado):
    """Cambia el estado (activo/inactivo) de un estado civil."""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    # Llamamos a la función estática para cambiar el estado
    success, message = EstadoCivilModel.change_estado_civil_status(id, estado)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409
