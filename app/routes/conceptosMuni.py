from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.conceptosMuni import ConceptosMuniModel
from ..utils.error_handlers import handle_response

conceptos_muni_bp = Blueprint('conceptos_muni', __name__)

@conceptos_muni_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_concepto_muni():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = ConceptosMuniModel.create_concepto_muni(data, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 201 if success else 409

@conceptos_muni_bp.route('/update', methods=['PUT'])
@jwt_required()
@handle_response
def update_concepto_muni():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    success, message = ConceptosMuniModel.update_concepto_muni(data, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 200 if success else 409

@conceptos_muni_bp.route('/filter', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_conceptos_muni():
    conceptos_muni_list = ConceptosMuniModel.get_conceptos_muni_list()
    return jsonify({'success': True, 'data': conceptos_muni_list}), 200

@conceptos_muni_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_conceptos_muni_active():
    conceptos_muni_active = ConceptosMuniModel.get_conceptos_muni_active()
    return jsonify({'success': True, 'data': conceptos_muni_active}), 200

@conceptos_muni_bp.route('/filter-tipo-condi', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_conceptos_muni_tip_cond():
    # Extract query parameters
    id_empleado = request.args.get('idEmpleado', type=int)  # Get the idEmpleado from query parameters
    tipo = request.args.get('tipo', default=None, type=str)  # Optional parameter for tipo

    if not id_empleado:
        return jsonify({'success': False, 'message': 'idEmpleado is required'}), 400

    # Call the stored procedure
    conceptos_muni_active = ConceptosMuniModel.get_conceptos_muni_by_employee(id_empleado, tipo)
    
    if conceptos_muni_active is False:
        return jsonify({'success': False, 'message': 'Error retrieving data from database'}), 500

    return jsonify({'success': True, 'data': conceptos_muni_active}), 200
