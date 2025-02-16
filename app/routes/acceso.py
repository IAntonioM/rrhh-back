from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.acceso import AccesoModel
from ..utils.error_handlers import handle_response
import re

acceso_bp = Blueprint('acceso', __name__)

def handle_sql_error(e):
    """Handles SQL errors by extracting the error message."""
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@acceso_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_acceso():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = AccesoModel.create_acceso(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@acceso_bp.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_acceso(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    success, message = AccesoModel.update_acceso(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@acceso_bp.route('/filtrar', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_accesos():
    # Obtener filtros y paginación desde los parámetros de consulta
    filtros = {
        'nombre': request.args.get('nombre') or None,
        'objeto_id': request.args.get('objeto_id') or None,
        'tipo': request.args.get('tipo') or None,
        'estado': request.args.get('estado') or None,
    }
    
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Obtener lista de accesos filtrados
    accesos_list = AccesoModel.get_accesos_filter(filtros, current_page, per_page)
    return jsonify({
        'success': True,
        'data': accesos_list
    }), 200

@acceso_bp.route('/<int:acceso_id>', methods=['GET'])
@jwt_required()
@handle_response
def get_acceso(acceso_id):
    acceso = AccesoModel.get_acceso(acceso_id)
    if not acceso:
        return jsonify({'success': False, 'message': 'Acceso no encontrado'}), 404
    return jsonify({
        'success': True,
        'data': acceso
    }), 200

@acceso_bp.route('/delete/<int:acceso_id>', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_acceso(acceso_id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = AccesoModel.delete_acceso(acceso_id, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@acceso_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_accesos_list():
    # Optionally accept query parameters to filter accesos (e.g., active, by tipo, etc.)
    accesos = AccesoModel.get_accesos_list_complete()
    return jsonify({
        'success': True,
        'data': accesos
    }), 200

@acceso_bp.route('/<int:id>/<int:estado>/estado', methods=['PATCH'])
@jwt_required()
@handle_response
def update_acceso_status(id, estado):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    # Llamamos a la función estática para cambiar el estado del acceso
    success, message = AccesoModel.change_acceso_status(id, estado, current_user, request.remote_addr)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409
