from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.planilla.periodoModel import Periodo
from ...utils.error_handlers import handle_response

periodo_bp = Blueprint('periodo', __name__)

@periodo_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_periodo():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['anio', 'mes']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400
    
    success, message = Periodo.create_periodo(data, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 201 if success else 409

@periodo_bp.route('/update', methods=['PUT'])
@jwt_required()
@handle_response
def update_periodo():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validar campos requeridos
    if 'id' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: id'}), 400
    
    success, message = Periodo.update_periodo(data, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 200 if success else 409

@periodo_bp.route('/list', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def list_periodos():
    data = request.get_json() or {}
    
    # Obtener parámetros de paginación y filtros del body
    page = data.get('current_page', 1)
    per_page = data.get('per_page', 10)
    
    # Filtros válidos
    valid_filters = ['anio']
    filtros = {k: v for k, v in data.items() if k in valid_filters}
    
    # Agregar parámetros de paginación
    filtros['current_page'] = page
    filtros['per_page'] = per_page
    
    result = Periodo.list_periodos(filtros)
    
    if not result.get('success', False):
        return jsonify({
            'success': False,
            'message': result.get('message', 'Error al obtener los datos')
        }), 500
    
    return jsonify({
        'success': True,
        'data': result.get('data', []),
        'pagination': result.get('pagination', {})
    }), 200

@periodo_bp.route('/status', methods=['PUT'])
@jwt_required()
@handle_response
def change_status_periodo():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validar campos requeridos
    if 'id' not in data or 'idEstado' not in data:
        return jsonify({'success': False, 'message': 'Campos requeridos: id, idEstado'}), 400
    
    success, message = Periodo.change_status_periodo(data['id'], data['idEstado'])
    return jsonify({'success': success, 'message': message}), 200 if success else 409