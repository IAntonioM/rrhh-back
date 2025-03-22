from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.general.emp_concepto import EmpConceptoModel
from ...utils.error_handlers import handle_response
import re

emp_concepto_bp = Blueprint('emp_concepto', __name__)

def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@emp_concepto_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_emp_concepto():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = EmpConceptoModel.create_emp_concepto(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@emp_concepto_bp.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_emp_concepto(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    # Obtenemos los datos del cuerpo de la solicitud
    data = request.get_json()
    
    # Agregar el id de la URL al diccionario de datos
    data['idEmpConcepto'] = id
    
    # Llamamos al método que actualiza el concepto
    success, message = EmpConceptoModel.update_emp_concepto(data, current_user, request.remote_addr)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@emp_concepto_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_emp_conceptos():
    emp_conceptos_list = EmpConceptoModel.get_emp_conceptos_list()
    return jsonify({
        'success': True,
        'data': emp_conceptos_list
    }), 200

@emp_concepto_bp.route('/list_filtered', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_filtered_emp_conceptos():
    # Obtener los parámetros de la query string
    idEmpleado = request.args.get('idEmpleado', default=None, type=str)
    tipo = request.args.get('tipo', default=None, type=str)

    # Llamar al método de la clase para obtener los conceptos filtrados
    emp_conceptos_list = EmpConceptoModel.consult_emp_concepto_tipo_cod(idEmpleado=idEmpleado, tipo=tipo)

    return jsonify({
        'success': True,
        'data': emp_conceptos_list
    }), 200

@emp_concepto_bp.route('/<int:idEmpConcepto>/<int:idNuevoEstado>/estado', methods=['PATCH'])
@jwt_required()
@handle_response  # Si tienes un decorador personalizado para manejar la respuesta
def update_estado_emp_concepto(idEmpConcepto, idNuevoEstado):
    current_user = get_jwt_identity()  # Obtener el usuario autenticado a través del JWT
    
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    # Llamar al método para actualizar el estado del EmpConcepto
    success, message = EmpConceptoModel.update_estado_emp_concepto(
        idEmpConcepto, 
        idNuevoEstado, 
        current_user, 
        request.remote_addr
    )

    # Devolver la respuesta JSON
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 400