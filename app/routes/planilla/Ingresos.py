from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.planilla.Ingresos import Ingresos
from ...utils.error_handlers import handle_response

ingresos_bp = Blueprint('ingresos', __name__)

@ingresos_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_ingreso():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validar campos requeridos según el SP
    required_fields = [
        'idCondicionLaboral', 'codigoPDT', 'concepto', 
        'tipoCalculo', 'idTipoMonto', 'flag_ATM', 
        'monto', 'flag_apldialab'
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400
    
    result = Ingresos.create_Ingreso(data, current_user, request.remote_addr)
    return jsonify(result), 201 if result.get('success') else 409


@ingresos_bp.route('/update', methods=['PUT'])
@jwt_required()
@handle_response
def update_ingreso():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validar que venga el idConcepto
    if 'idConcepto' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idConcepto'}), 400
    
    result = Ingresos.update_Ingreso(data, current_user, request.remote_addr)
    return jsonify(result), 200 if result.get('success') else 409


@ingresos_bp.route('/delete', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_ingreso():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validar que venga el idConcepto
    if 'idConcepto' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idConcepto'}), 400
    
    result = Ingresos.delete_Ingreso(data['idConcepto'])
    return jsonify(result), 200 if result.get('success') else 409


@ingresos_bp.route('/list', methods=['POST'])
@jwt_required()
@handle_response
def list_ingresos():
    data = request.get_json()
    
    # Obtener parámetros de paginación y filtros del body
    filtros = {
        'current_page': data.get('current_page', 1),
        'per_page': data.get('per_page', 10),
        'idCondicionLaboral': data.get('idCondicionLaboral'),
        'codigoPDT': data.get('codigoPDT'),
        'codigoInterno': data.get('codigoInterno'),
        'concepto': data.get('concepto')
    }
    
    result = Ingresos.list_ingresos(filtros)
    
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