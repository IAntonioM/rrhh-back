from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.controlAsistencias.papeletasModel import Papeleta
from ...utils.error_handlers import handle_response

papeletas_bp = Blueprint('papeletas', __name__)

@papeletas_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_papeleta():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    required_fields = [
        'idSede', 'idArea', 'idSolicitante', 
        'idTipoSalida', 'motivoSalida', 'fecha_salida', 
        'idTipoPapeleta'
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400

    result = Papeleta.crear_papeleta(data, current_user, request.remote_addr)
    return jsonify({
        'success': result['success'], 
        'message': result['message']
    }), 201 if result['success'] else 409

@papeletas_bp.route('/update', methods=['PUT'])
@jwt_required()
@handle_response
def update_papeleta():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # Validar que se envíe el ID de la papeleta
    if 'idPapeleta' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idPapeleta'}), 400

    result = Papeleta.editar_papeleta(data, current_user, request.remote_addr)
    return jsonify({
        'success': result['success'], 
        'message': result['message']
    }), 200 if result['success'] else 409

@papeletas_bp.route('/get', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def get_papeleta():
    data = request.get_json()
    
    # Validar que se envíe el ID de la papeleta
    if 'idPapeleta' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idPapeleta'}), 400

    result = Papeleta.obtener_papeleta(data)
    
    if result.get('data'):
        return jsonify({
            'success': True,
            'data': result['data']
        }), 200
    else:
        return jsonify({
            'success': False, 
            'message': 'Papeleta no encontrada'
        }), 404

@papeletas_bp.route('/list', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def list_papeletas():
    data = request.get_json() or {}
    
    try:
        # Primero obtener el conteo total (sin paginación)
        count_data = data.copy()
        count_data.pop('current_page', None)
        count_data.pop('per_page', None)
        
        count_result = Papeleta.contar_papeletas(count_data)
        total = count_result.get('total', 0)
        
        # Obtener los datos con paginación
        list_result = Papeleta.consultar_papeletas(data)
        
        if 'data' in list_result:
            # Calcular información de paginación
            current_page = data.get('current_page', 1)
            per_page = data.get('per_page', 10)
            total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1
            
            return jsonify({
                'success': True,
                'data': list_result['data'],
                'pagination': {
                    'current_page': current_page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages
                }
            }), 200
        else:
            return jsonify({
                'success': False, 
                'message': 'No se pudieron obtener los datos'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error al consultar papeletas: {str(e)}'
        }), 500

@papeletas_bp.route('/totallist', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def list_total_papeletas():
    data = request.get_json() or {}
    
    try:
        # Usar consultar_papeletas sin parámetros de paginación para obtener todos los registros
        data_without_pagination = data.copy()
        data_without_pagination.pop('current_page', None)
        data_without_pagination.pop('per_page', None)
        data_without_pagination.pop('inicio', None)
        data_without_pagination.pop('final', None)
        
        result = Papeleta.consultar_papeletas(data_without_pagination)
        
        if 'data' in result:
            return jsonify({
                'success': True,
                'data': result['data']
            }), 200
        else:
            return jsonify({
                'success': False, 
                'message': 'No se pudieron obtener los datos'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error al consultar papeletas: {str(e)}'
        }), 500

@papeletas_bp.route('/registrar-salida', methods=['POST'])
@jwt_required()
@handle_response
def registrar_hora_salida():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # Validar que se envíe el ID de la papeleta
    if 'idPapeleta' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idPapeleta'}), 400

    result = Papeleta.registrar_hora_salida(data, current_user, request.remote_addr)
    return jsonify({
        'success': result['success'], 
        'message': result['message']
    }), 200 if result['success'] else 409

@papeletas_bp.route('/registrar-retorno', methods=['POST'])
@jwt_required()
@handle_response
def registrar_hora_retorno():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # Validar que se envíe el ID de la papeleta
    if 'idPapeleta' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idPapeleta'}), 400

    result = Papeleta.registrar_hora_retorno(data, current_user, request.remote_addr)
    return jsonify({
        'success': result['success'], 
        'message': result['message']
    }), 200 if result['success'] else 409

@papeletas_bp.route('/historial-aprobaciones', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def historial_aprobaciones():
    data = request.get_json()
    
    # Validar que se envíe el ID de la papeleta
    if 'idPapeleta' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idPapeleta'}), 400

    result = Papeleta.historial_aprobaciones(data)
    
    if 'data' in result:
        return jsonify({
            'success': True,
            'data': result['data']
        }), 200
    else:
        return jsonify({
            'success': False, 
            'message': 'Error al obtener historial'
        }), 409
@papeletas_bp.route('/delete', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_papeleta():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # Validar que se envíe el ID de la papeleta
    if 'idPapeleta' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idPapeleta'}), 400

    result = Papeleta.eliminar_papeleta(data, current_user, request.remote_addr)
    
    # Verificar que result no sea None
    if result is None:
        return jsonify({
            'success': False, 
            'message': 'Error interno del servidor'
        }), 500
    
    return jsonify({
        'success': result.get('success', False), 
        'message': result.get('message', 'Error desconocido')
    }), 200 if result.get('success', False) else 409