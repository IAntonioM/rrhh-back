from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.emp_concepto import EmpConceptoModel
from ..utils.error_handlers import handle_response
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

@emp_concepto_bp.route('/update', methods=['PUT'])
@jwt_required()
@handle_response
def update_emp_concepto():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
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
    codEmpleado = request.args.get('codEmpleado', default=None, type=str)
    tipo = request.args.get('tipo', default=None, type=str)

    # Llamar al método de la clase para obtener los conceptos filtrados
    emp_conceptos_list = EmpConceptoModel.consult_emp_concepto_tipo_cod(codEmpleado=codEmpleado, tipo=tipo)

    return jsonify({
        'success': True,
        'data': emp_conceptos_list
    }), 200

