from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.terceros.registro_locador import RegistroLocadorModel
from ...utils.error_handlers import handle_response
from ...request.terceros.UpdateContratoRequest1 import UpdateContratoRequest1
from ...request.terceros.UpdateContratoRequest2 import UpdateContratoRequest2
from ...request.terceros.UpdateContratoRequest3 import UpdateContratoRequest3
from ...request.terceros.createContratoRequest import CreateContratoRequest

locador_contrato_bp = Blueprint('locador_contrato', __name__)

@locador_contrato_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_contrato():
    """Crear un nuevo contrato de locador."""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # Campos requeridos según el SP
    valid_data, error_message = CreateContratoRequest.validate(data)
    if not valid_data:
        return jsonify({'success': False, 'message': error_message}), 409


    success, message = RegistroLocadorModel.create(data, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 201 if success else 409


@locador_contrato_bp.route('/update/<uuid:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_contrato(id):
    """Actualizar un contrato de locador."""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    criterio = data.get('criterio', None)
    print("criterio")
    print(criterio)
    if criterio == 1 :
        print('criterio 1')
        valid_data, error_message = UpdateContratoRequest1.validate(data)
        if not valid_data:
            return jsonify({'success': False, 'message': error_message}), 409
    elif criterio == 2:
        print('criterio 2')
        valid_data, error_message = UpdateContratoRequest2.validate(data)
        if not valid_data:
            return jsonify({'success': False, 'message': error_message}), 409
    elif criterio == 3:
        print('criterio 3')
        valid_data, error_message = UpdateContratoRequest3.validate(data)
        if not valid_data:
            return jsonify({'success': False, 'message': error_message}), 409
    else:
        # Si el valor de 'criterio' es inválido o no está contemplado, puedes manejarlo de una manera específica
        return jsonify({'success': False, 'message': 'Criterio no válido'}), 400
    
    data['id'] = str(id)  # Convertir UUID a string

    success, message = RegistroLocadorModel.update(data, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 200 if success else 409


@locador_contrato_bp.route('/status/<uuid:id>/<int:estado>', methods=['PATCH'])
@jwt_required()
@handle_response
def change_status_contrato(id, estado):
    """Actualizar el estado de un contrato de locador (activo/inactivo)."""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = RegistroLocadorModel.change_status(id, estado, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 200 if success else 409


@locador_contrato_bp.route('/delete/<uuid:id>', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_contrato(id):
    """Eliminar (desactivar) un contrato de locador."""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = RegistroLocadorModel.delete(id, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 200 if success else 409


@locador_contrato_bp.route('/filtrar', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def list_contratos():
    """Listar contratos de locadores con filtros y paginación."""
    
    # Filtros permitidos
    filtros = {
        'id': request.args.get('id') or None,
        'id_datos_personales': request.args.get('id_datos_personales') or None,
        'idCentroCosto': request.args.get('idCentroCosto') or None,
        'id_cargo': request.args.get('id_cargo') or None,
        'nro_orden_servicio': request.args.get('nro_orden_servicio') or None,
        'estado': request.args.get('estado') or None,
        'estado_recepcion': request.args.get('estado_recepcion') or None,
        'mes': request.args.get('mes') or None ,
        'anio': request.args.get('anio') or None 
    }
    
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    result = RegistroLocadorModel.filter(filtros, current_page, per_page)
    
    # Verificar si result es un error
    if isinstance(result, dict) and 'success' in result and not result['success']:
        return jsonify(result), 500
    
    return jsonify({
        'success': True,
        'data': result
    }), 200 
    
@locador_contrato_bp.route('/<string:id_list>/<int:idNuevoEstado>/estado', methods=['PATCH'])
@jwt_required()
@handle_response
def change_recepcion_estado(id_list, idNuevoEstado):
    """Actualiza el estado de múltiples empleados"""
    current_user = get_jwt_identity()
    
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    if not id_list or not idNuevoEstado:
        return jsonify({'success': False, 'message': 'Lista de IDs y estado nuevo son requeridos'}), 400
    
    # Llamar al modelo para actualizar los estados
    success, message = RegistroLocadorModel.change_status_recepcion_list(id_list, idNuevoEstado, current_user, request.remote_addr)
    
    return jsonify({'success': success, 'message': message}), 200 if success else 409
