from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.planilla.aportaciones import Aportaciones
from ...utils.error_handlers import handle_response

aportaciones_bp = Blueprint('aportaciones', __name__)

@aportaciones_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_aportacion():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    required_fields = [
        'idCondicionLaboral', 'codigoPDT',    
        'concepto', 'tipoCalculo', 'idTipoMonto', 
        'flag_ATM', 'monto', 'flag_apldialab'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400

    success, message = Aportaciones.create_aportacion(data, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 201 if success else 409

@aportaciones_bp.route('/update/<int:idConcepto>', methods=['PUT'])
@jwt_required()
@handle_response
def update_aportacion(idConcepto):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    data['idConcepto'] = idConcepto
    success, message = Aportaciones.update_aportacion(data, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 200 if success else 409

@aportaciones_bp.route('/status/<int:idConcepto>', methods=['PUT'])
@jwt_required()
@handle_response
def change_status_aportacion(idConcepto):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = Aportaciones.delete_aportacion(idConcepto)
    return jsonify({'success': success, 'message': message}), 200 if success else 409

@aportaciones_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def list_aportacions():
    # Obtener parámetros de paginación
    page = request.args.get('current_page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Solo permitir los filtros válidos
    valid_filters = ['codigoPDT', 'codigoInterno', 'concepto']
    filtros = {k: v for k, v in request.args.items() if k in valid_filters}
    
    # Agregar parámetros de paginación a los filtros
    filtros['current_page'] = page
    filtros['per_page'] = per_page
    
    result = Aportaciones.list_aportacions(filtros)
    
    if isinstance(result, dict):
        return jsonify({
            'success': True,
            'data': result['data'],
            'pagination': result['pagination']
        }), 200
    else:
        success, message = result
        return jsonify({'success': success, 'message': message}), 409
    
@aportaciones_bp.route('/totallist', methods=['GET'])
@jwt_required()
@handle_response()
def list_Total_aportacions():
    result = Aportaciones.list_total_aportacions()
    
    if isinstance(result, dict):
        return jsonify({
            'success': True,
            'data': result['data'],
        }), 200
    else:
        success, message = result
        return jsonify({'success': success, 'message': message}), 409