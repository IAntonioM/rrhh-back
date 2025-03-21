from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.ordenServicio import OrdenServicioModel
from ..utils.error_handlers import handle_response
from ..request.CreateOrdenServicioRequest import CreateOrdenServicioRequest

orden_servicio_bpv2 = Blueprint('orden_servicio_bpv2', __name__)

# Route to create a new order service
@orden_servicio_bpv2.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_orden_servicio():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    valid_data, error_message = CreateOrdenServicioRequest.validate(data)
    if not valid_data:
        return jsonify({'success': False, 'message': error_message}), 409
    success, message = OrdenServicioModel.create_orden_servicio(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

# Route to update an existing order service
@orden_servicio_bpv2.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_orden_servicio(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()  # Get the updated data from the request body
    success, message = OrdenServicioModel.update_orden_servicio(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

# Route to list all order services with optional filters and pagination
@orden_servicio_bpv2.route('', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_ordenes_servicio():
    filtros = {
        'num_servicio': request.args.get('num_servicio') or None,
        'fecha_orden': request.args.get('fecha_orden') or None,
        'id_datos_personales': request.args.get('id_datos_personales') or None,
        'id_estado_servicio': request.args.get('id_estado_servicio') or None,
        'estado': request.args.get('estado') or None,
        # Añadir filtros existentes adicionales
        'id_tipo_presupuesto': request.args.get('id_tipo_presupuesto') or None,
        'id_proceso_seleccion': request.args.get('id_proceso_seleccion') or None,
        'concepto': request.args.get('concepto') or None,
        # Nuevos filtros
        'mes': request.args.get('mes') or None,
        'dia': request.args.get('dia') or None,
        'anio': request.args.get('anio') or None,
        'dni': request.args.get('dni') or None,
        'nombres': request.args.get('nombres') or None,
    }
    
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    ordenes_servicio_list = OrdenServicioModel.get_ordenes_servicio_filter(filtros, current_page, per_page)
    return jsonify({
        'success': True,
        'data': ordenes_servicio_list
    }), 200

# Route to get a single order service by its ID
@orden_servicio_bpv2.route('/<int:id>', methods=['GET'])
@jwt_required()
@handle_response
def get_orden_servicio(id):
    orden_servicio = OrdenServicioModel.get_orden_servicio(id)
    if not orden_servicio:
        return jsonify({'success': False, 'message': 'Orden de servicio no encontrada'}), 404
    return jsonify({
        'success': True,
        'data': orden_servicio
    }), 200

# Route to delete an order service by its ID
@orden_servicio_bpv2.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_orden_servicio(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = OrdenServicioModel.delete_orden_servicio(id, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409
