from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.general.registro_tiempo import TiempoProcesamiento
from ...utils.error_handlers import handle_response
from datetime import datetime
import re

tiempo_procesamiento_bp = Blueprint('tiempo_procesamiento', __name__)

def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@tiempo_procesamiento_bp.route('/guardar', methods=['POST'])
@jwt_required()
@handle_response
def guardar_tiempo_procesamiento():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # Validar campos requeridos
    if not data.get('tiempo_modal') or not data.get('tipo'):
        return jsonify({
            'success': False,
            'message': 'Faltan campos requeridos: tiempo_modal, tipo'
        }), 400
    
    # Convertir tiempo_modal a datetime si viene como string
    tiempo_modal = data.get('tiempo_modal')
    if isinstance(tiempo_modal, str):
        try:
            tiempo_modal = datetime.fromisoformat(tiempo_modal.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Formato de fecha inválido para tiempo_modal'
            }), 400
    
    success, message = TiempoProcesamiento.guardar_tiempo_procesamiento(
        tiempo_modal=tiempo_modal,
        tipo=data['tipo']
    )
    
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@tiempo_procesamiento_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_registros_procesamiento():
    # Obtener filtros opcionales de query params
    filtros = {
        'tipo': request.args.get('tipo')
    }
    
    registros = TiempoProcesamiento.get_registros_procesamiento(filtros)
    
    return jsonify({
        'success': True,
        'data': registros
    }), 200