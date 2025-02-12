from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.Egresos import Egresos
from ..utils.error_handlers import handle_response

egresos = Blueprint('egresos', __name__)

@egresos.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_egreso():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    required_fields = [
        'idCondicionLaboral', 'codigoPDT', 'codigoInterno', 
        'concepto', 'tipoCalculo', 'idTipoMonto', 
        'flag_ATM', 'monto', 'flag_apldialab'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400

    success, message = Egresos.create_egreso(data, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 201 if success else 409

@egresos.route('/update/<int:idConcepto>', methods=['PUT'])
@jwt_required()
@handle_response
def update_egreso(idConcepto):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    data['idConcepto'] = idConcepto
    success, message = Egresos.update_egreso(data, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 200 if success else 409

@egresos.route('/status/<int:idConcepto>', methods=['PUT'])
@jwt_required()
@handle_response
def change_status_egreso(idConcepto):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = Egresos.delete_egreso(idConcepto)
    return jsonify({'success': success, 'message': message}), 200 if success else 409

@egresos.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def list_egresos():
    # Obtener parámetros de paginación
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Solo permitir los filtros válidos
    valid_filters = ['codigoPDT', 'codigoInterno', 'concepto']
    filtros = {k: v for k, v in request.args.items() if k in valid_filters}
    
    # Agregar parámetros de paginación a los filtros
    filtros['current_page'] = page
    filtros['per_page'] = per_page
    
    result = Egresos.list_egresos(filtros)
    
    if isinstance(result, dict):
        return jsonify({
            'success': True,
            'data': result['data'],
            'pagination': result['pagination']
        }), 200
    else:
        success, message = result
        return jsonify({'success': success, 'message': message}), 409