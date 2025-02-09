from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.empleado import EmpleadoModel  # Modelo Empleado
from ..utils.error_handlers import handle_response
import re

empleado_bp = Blueprint('empleado', __name__)

# Handler para errores SQL
def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@empleado_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_empleado():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
    data = request.get_json()
    success, message = EmpleadoModel.create_empleado(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@empleado_bp.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_datos(id):
    current_user = get_jwt_identity()
    
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()

    # Validar que el 'updateType' esté presente en los datos
    updateTipo = data.get('updateTipo', None)

    if not updateTipo:
        return jsonify({
            'success': False,
            'message': 'El tipo de actualización (updateType) es obligatorio'
        }), 400

    # Validar que el idEmpleado esté presente en los datos
    if not data.get('idEmpleado'):
        return jsonify({
            'success': False,
            'message': 'El ID del empleado es obligatorio'
        }), 400

    if updateTipo == 'dp':
        # Llamar al método para actualizar los datos personales
        success, message = EmpleadoModel.update_datosPersonales(data, current_user, request.remote_addr)
    elif updateTipo == 'e':
        # Llamar al método para actualizar los datos generales del empleado
        success, message = EmpleadoModel.update_empleado(data, current_user, request.remote_addr)
    else:
        return jsonify({
            'success': False,
            'message': 'Tipo de actualización no válido. Usa "dp" para datos personales o "e" para datos generales.'
        }), 400
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 400


@empleado_bp.route('/update-e/<int:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_empleado(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
    data = request.get_json()
    
    # Validar que el idEmpleado esté presente en los datos
    if not data.get('idEmpleado'):
        return jsonify({
            'success': False,
            'message': 'El ID del empleado es obligatorio'
        }), 400
    
    # Llamar al método para actualizar el empleado
    success, message = EmpleadoModel.update_empleado(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 400

@empleado_bp.route('/filtrar', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_empleados():
    # Obtener filtros y paginación desde los parámetros de consulta
    filtros = {
        'estado': request.args.get('estado') or None,  # Si está vacío, reemplazamos con None
        'cargo': request.args.get('cargo') or None,
        'condicionLaboral': request.args.get('condicionLaboral') or None,
        'nombreApellido': request.args.get('nombreApellido') or None,
        'centroCosto': request.args.get('centroCosto') or None
    }
    
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    empleados_list = EmpleadoModel.get_empleados_filtrar(filtros, current_page, per_page)
    return jsonify({
        'success': True,
        'data': empleados_list
    }), 200

@empleado_bp.route('/datosLaborales', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_datos_empleado():
    # Obtener el filtro de idDatosPersonales desde los parámetros de consulta
    idDatosPersonales = request.args.get('idDatosPersonales')  # Filtro por idDatosPersonales

    if not idDatosPersonales:
        return jsonify({
            'success': False,
            'message': 'El parámetro idDatosPersonales es obligatorio'
        }), 400
    
    # Consultar los datos del empleado usando el idDatosPersonales
    filtros = {
        'idDatosPersonales': idDatosPersonales  # Usamos el filtro para idDatosPersonales
    }
    
    empleados_list = EmpleadoModel.get_empleados_datosLaborales(filtros)
    
    if not empleados_list:
        return jsonify({
            'success': False,
            'message': 'No se encontraron empleados con el idDatosPersonales proporcionado'
        }), 404

    return jsonify({
        'success': True,
        'data': empleados_list
    }), 200
