from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.general.configuracion import ConfiguracionesModel
from ...utils.error_handlers import handle_response
import re

configuraciones_bp = Blueprint('configuraciones', __name__)

# Route to create a new configuration
@configuraciones_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_configuracion():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()  # Get the data sent in the request body
    success, message = ConfiguracionesModel.create_configuracion(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

# Route to update an existing configuration
@configuraciones_bp.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_configuracion(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()  # Get the updated data from the request body
    success, message = ConfiguracionesModel.update_configuracion(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

# Route to list all configurations with optional filters and pagination
@configuraciones_bp.route('', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_configuraciones():
    filtros = {
        'configuracion_id': request.args.get('configuracion_id') or None,
        'clave': request.args.get('clave') or None,
        'valor': request.args.get('valor') or None,
        'estado': request.args.get('estado') or None,
    }
    
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    configuraciones_list = ConfiguracionesModel.get_configuraciones_filter(filtros, current_page, per_page)
    return jsonify({
        'success': True,
        'data': configuraciones_list
    }), 200

# Route to get a single configuration by its ID
@configuraciones_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@handle_response
def get_configuracion(id):
    configuracion = ConfiguracionesModel.get_configuracion(id)
    if not configuracion:
        return jsonify({'success': False, 'message': 'Configuración no encontrada'}), 404
    return jsonify({
        'success': True,
        'data': configuracion
    }), 200

# Route to delete a configuration by its ID
@configuraciones_bp.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_configuracion(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = ConfiguracionesModel.delete_configuracion(id, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409
