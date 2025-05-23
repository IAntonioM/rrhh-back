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
        'idCondicionLaboral', 'codigoPDT', 'codigoInterno', 
        'concepto', 'tipoCalculo', 'idTipoMonto', 
        'flag_ATM', 'monto', 'flag_apldialab'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400

    success, message = Ingresos.create_Ingreso(data, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 201 if success else 409

@ingresos_bp.route('/update/<int:idConcepto>', methods=['PUT'])
@jwt_required()
@handle_response
def update_ingreso(idConcepto):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    data['idConcepto'] = idConcepto
    success, message = Ingresos.update_Ingreso(data, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 200 if success else 409

@ingresos_bp.route('/status/<int:idConcepto>', methods=['PUT'])
@jwt_required()
@handle_response
def change_status_ingreso(idConcepto):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = Ingresos.delete_Ingreso(idConcepto)  # Internamente hace el update de flag_estado
    return jsonify({'success': success, 'message': message}), 200 if success else 409

@ingresos_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def list_Egresos():
    # Obtener parámetros de paginación
    page = request.args.get('current_page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Solo permitir los filtros válidos
    valid_filters = ['idCondicionLaboral', 'codigoPDT', 'codigoInterno', 'concepto']
    filtros = {k: v for k, v in request.args.items() if k in valid_filters}
    
    # Agregar parámetros de paginación a los filtros
    filtros['current_page'] = page
    filtros['per_page'] = per_page
    
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