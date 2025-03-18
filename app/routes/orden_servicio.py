from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.orden_servicio import OrdenServicio
from ..utils.error_handlers import handle_response

orden_servicio_bp = Blueprint('orden_servicio', __name__)

@orden_servicio_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_orden_servicio():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    required_fields = [
        'id_empleado', 'id_cargo', 'id_area', 
        'descripcion', 'fecha_inicio', 'fecha_termino', 
        'monto'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400

    result = OrdenServicio.create_orden_servicio(data, current_user, request.remote_addr)
    return jsonify(result), 201 if result.get('success', False) else 409

@orden_servicio_bp.route('/update/<uuid:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_orden_servicio(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    data['id'] = id
    result = OrdenServicio.update_orden_servicio(data, current_user, request.remote_addr)
    return jsonify(result), 200 if result.get('success', False) else 409

@orden_servicio_bp.route('/delete/<uuid:id>', methods=['PUT'])
@jwt_required()
@handle_response
def delete_orden_servicio(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    result = OrdenServicio.delete_orden_servicio(id, current_user, request.remote_addr)
    return jsonify(result), 200 if result.get('success', False) else 409

@orden_servicio_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_orden_servicio():
    # Solo permitir los filtros válidos
    valid_filters = ['id', 'id_empleado', 'id_cargo', 'id_area']
    filtros = {k: v for k, v in request.args.items() if k in valid_filters}
    
    # Convertir el ID a UUID si está presente
    if 'id' in filtros:
        try:
            from uuid import UUID
            filtros['id'] = UUID(filtros['id'])
        except ValueError:
            return jsonify({'success': False, 'message': 'ID inválido'}), 400
    
    # Convertir IDs numéricos a enteros si están presentes
    for key in ['id_empleado', 'id_cargo', 'id_area']:
        if key in filtros:
            try:
                filtros[key] = int(filtros[key])
            except ValueError:
                return jsonify({'success': False, 'message': f'{key} inválido'}), 400
    
    result = OrdenServicio.get_orden_servicio(filtros)
    
    if isinstance(result, dict) and 'data' in result:
        return jsonify({
            'success': True,
            'data': result['data']
        }), 200
    else:
        return jsonify({'success': False, 'message': 'Error al obtener datos'}), 409