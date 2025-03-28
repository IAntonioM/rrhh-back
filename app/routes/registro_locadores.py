from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.registro_locadores import RegistroLocadoresModel
from ..utils.error_handlers import handle_response
import re

registro_locadores_bp = Blueprint('registro_locadores', __name__)

def handle_sql_error(e):
    """Maneja los errores de SQL extrayendo el mensaje de error."""
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

def validate_locador_data(data):
    """Validación de datos de locador antes de procesar"""
    errors = []

    # Validar datos personales
    if 'id_datos_personales' not in data or not data['id_datos_personales']:
        errors.append('Debe seleccionar un empleado')

    # Validar área
    if 'idCentroCosto' not in data or not data['idCentroCosto']:
        errors.append('Debe seleccionar un área')

    # Validar cargo
    if 'id_cargo' not in data or not data['id_cargo']:
        errors.append('Debe seleccionar un cargo')

    # Validar fecha
    if 'fecha' not in data or not data['fecha']:
        errors.append('Debe seleccionar una fecha')

    # Validar monto (si aplica)
    if 'monto' in data:
        try:
            monto = float(data['monto'])
            if monto <= 0:
                errors.append('El monto debe ser un valor positivo')
        except (ValueError, TypeError):
            errors.append('El monto debe ser un número válido')

    return errors

@registro_locadores_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_registro_locadores():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # Validar datos antes de procesar
    validation_errors = validate_locador_data(data)
    if validation_errors:
        return jsonify({
            'success': False,
            'message': 'Error de validación',
            'errors': validation_errors
        }), 400

    success, message = RegistroLocadoresModel.register_locador(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@registro_locadores_bp.route('/update/<uuid:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_registro_locadores(id):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    data['id'] = id  # Incluimos el ID en los datos para la actualización
    success, message = RegistroLocadoresModel.update_locador(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@registro_locadores_bp.route('', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_registros_locadores():
    # Obtener filtros y paginación desde los parámetros de consulta
    filtros = {
        'id_datos_personales': request.args.get('id_datos_personales'),
        'idCentroCosto': request.args.get('idCentroCosto'),
        'id_cargo': request.args.get('id_cargo'),
        'tipo': request.args.get('tipo'),
        'estado': request.args.get('estado'),
        'fecha': request.args.get('fecha'),
        'anio': request.args.get('anio'),
        'mes': request.args.get('mes'),
    }
    
    # Eliminar filtros con valor None
    filtros = {k: v for k, v in filtros.items() if v is not None}
    
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Obtener lista de registros locadores con detalles personales
    resultado = RegistroLocadoresModel.get_locadores_with_personal_details(
        filtros, current_page, per_page
    )
    
    # Manejar diferentes tipos de respuesta
    if not resultado.get('success', False):
        return jsonify({
            'success': False,
            'message': resultado.get('message', 'Error al obtener registros')
        }), 400
    
    return jsonify({
        'success': True,
        'data': resultado.get('data', []),
        'pagination': resultado.get('pagination', {})
    }), 200

