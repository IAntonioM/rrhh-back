from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.tercerosv2.emp_horario import EmpHorario
from ...utils.error_handlers import handle_response

emp_horario_bp = Blueprint('emp_horario', __name__)

@emp_horario_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_horario():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['idHorario', 'idEmpleado', 'idTipoHorario', 'fechaDesde']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400
    
    # Validar que si es tipo Variable (V), debe incluir fechaHasta
    if data['idTipoHorario'] == 'V' and ('fechaHasta' not in data or not data['fechaHasta']):
        return jsonify({'success': False, 'message': 'Campo requerido para horario variable: fechaHasta'}), 400
    
    result = EmpHorario.create_horario(data, current_user, request.remote_addr)
    
    if True:
        return jsonify(result), 201
    else:
        return jsonify(result), 409

@emp_horario_bp.route('/update', methods=['POST'])
@jwt_required()
@handle_response
def update_horario():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()

    # Validar campos requeridos
    required_fields = ['idHorario', 'idEmpleado', 'idTipoHorario', 'fechaDesde','idEmpHorario']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400
    
    # Validar que si es tipo Variable (V), debe incluir fechaHasta
    if data['idTipoHorario'] == 'V' and ('fechaHasta' not in data or not data['fechaHasta']):
        return jsonify({'success': False, 'message': 'Campo requerido para horario variable: fechaHasta'}), 400
    
    result = EmpHorario.update_horario(data, current_user, request.remote_addr)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 409

@emp_horario_bp.route('/delete/<int:idEmpHorario>', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_horario(idEmpHorario):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    result = EmpHorario.delete_horario(idEmpHorario)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 409

@emp_horario_bp.route('/get', methods=['GET'])
@jwt_required()
@handle_response
def get_horario():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    idEmpleado = request.args.get('idEmpleado')
    result = EmpHorario.get_horario(idEmpleado)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 404

@emp_horario_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def list_horarios():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    # Obtener parámetros de paginación
    page = request.args.get('current_page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Obtener filtro de empleado (único filtro válido según el SP)
    idEmpleado = request.args.get('idEmpleado', type=int)
    
    filtros = {
        'current_page': page,
        'per_page': per_page
    }
    
    # Solo agregar idEmpleado si se proporciona
    if idEmpleado:
        filtros['idEmpleado'] = idEmpleado
    
    result = EmpHorario.list_horarios(filtros)
    
    return jsonify({
        'success': True,
        'data': result['data'],
        'pagination': result['pagination']
    }), 200