from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.terceros.control_contrato import ControlContratoModel
from ...utils.error_handlers import handle_response
# from ...request.locadores.CreateControlContratoRequest import CreateControlContratoRequest

control_contrato_bp = Blueprint('control_contrato_bp', __name__)

# Ruta para crear un nuevo contrato de control
@control_contrato_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_control_contrato():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # valid_data, error_message = CreateControlContratoRequest.validate(data)
    # if not valid_data:
    #     return jsonify({'success': False, 'message': error_message}), 409

    success, message = ControlContratoModel.create(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

# Ruta para actualizar un contrato de control existente
@control_contrato_bp.route('/update/<uuid:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_control_contrato(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()  # Obtener los datos actualizados desde el cuerpo de la solicitud
    data['id'] = id  # Asegurarse de incluir el ID del contrato en los datos
    success, message = ControlContratoModel.update(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

# Ruta para listar todos los contratos de control con filtros opcionales y paginación
@control_contrato_bp.route('', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_control_contratos():
    filtros = {
        'id_contrato': request.args.get('id_contrato') or None,
        'estado': request.args.get('estado') or None,
        'estado_pago': request.args.get('estado_pago') or None,
        'mes': request.args.get('mes') or None,
        'anio': request.args.get('anio') or None,
        # Nuevos filtros adicionales
        'motivo_reemplazo': request.args.get('motivo_reemplazo') or None,
    }
    
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    contratos_list = ControlContratoModel.filter(filtros, current_page, per_page)
    return jsonify({
        'success': True,
        'data': contratos_list
    }), 200

# Ruta para cambiar el estado de un contrato de control
@control_contrato_bp.route('/change_status/<uuid:id>', methods=['PATCH'])
@jwt_required()
@handle_response
def change_status_control_contrato(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    estado = data.get('estado')
    if not estado:
        return jsonify({'success': False, 'message': 'Estado no proporcionado'}), 400

    success, message = ControlContratoModel.change_status(id, estado, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

# Ruta para eliminar un contrato de control
@control_contrato_bp.route('/delete/<uuid:id>', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_control_contrato(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = ControlContratoModel.delete(id, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409



# Ruta para listar los pagos con columnas dinámicas según el rango de fechas
@control_contrato_bp.route('/pagos', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def listar_pagos():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    # Obtener los parámetros de la consulta
    filtros = {
        'FechaInicio': request.args.get('FechaInicio') or None,
        'FechaFin': request.args.get('FechaFin') or None,
        'anio': request.args.get('anio') or None,
    }

    pagos_list = ControlContratoModel.filter_control_contrato(filtros)

    # Crear un formato dinámico de respuesta con los meses como columnas
    return jsonify({
            'success': True,
            'data': pagos_list
        }), 200