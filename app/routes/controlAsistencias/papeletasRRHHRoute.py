from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.controlAsistencias.papeletasRRHHModel import PapeletaRRHH
from ...utils.error_handlers import handle_response

papeletas_rrhh_bp = Blueprint('papeletas_rrhh', __name__)

@papeletas_rrhh_bp.route('/list', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def list_papeletas_rrhh():
    data = request.get_json() or {}
    
    try:
        # Primero obtener el conteo total (sin paginación)
        count_data = data.copy()
        count_data.pop('inicio', None)
        count_data.pop('final', None)
        
        count_result = PapeletaRRHH.contar_papeletas_rrhh(count_data)
        total = count_result.get('total', 0)
        
        # Obtener los datos con paginación
        list_result = PapeletaRRHH.consultar_papeletas_rrhh(data)
        
        if 'data' in list_result:
            # Calcular información de paginación si se proporcionaron inicio y final
            inicio = data.get('inicio', 0)
            final = data.get('final', 0)
            
            pagination_info = {}
            if inicio > 0 and final > 0:
                per_page = final - inicio + 1
                current_page = ((inicio - 1) // per_page) + 1 if per_page > 0 else 1
                total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1
                
                pagination_info = {
                    'current_page': current_page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages,
                    'inicio': inicio,
                    'final': final
                }
            else:
                pagination_info = {
                    'total': total
                }
            
            return jsonify({
                'success': True,
                'data': list_result['data'],
                'pagination': pagination_info
            }), 200
        else:
            return jsonify({
                'success': False, 
                'message': 'No se pudieron obtener los datos'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error al consultar papeletas RRHH: {str(e)}'
        }), 500

@papeletas_rrhh_bp.route('/get', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def get_papeleta_rrhh():
    data = request.get_json()
    
    # Validar que se envíe el ID de la papeleta
    if 'idPapeleta' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idPapeleta'}), 400

    result = PapeletaRRHH.obtener_papeleta_rrhh(data['idPapeleta'])
    
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

@papeletas_rrhh_bp.route('/aprobar', methods=['POST'])
@jwt_required()
@handle_response
def aprobar_papeleta():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # Validar que se envíe el ID de la papeleta
    if 'idPapeleta' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idPapeleta'}), 400

    result = PapeletaRRHH.aprobar_papeleta_rrhh(data, current_user, request.remote_addr)
    return jsonify({
        'success': result['success'], 
        'message': result['message']
    }), 200 if result['success'] else 409

@papeletas_rrhh_bp.route('/rechazar', methods=['POST'])
@jwt_required()
@handle_response
def rechazar_papeleta():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # Validar que se envíe el ID de la papeleta
    if 'idPapeleta' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idPapeleta'}), 400

    result = PapeletaRRHH.rechazar_papeleta_rrhh(data, current_user, request.remote_addr)
    return jsonify({
        'success': result['success'], 
        'message': result['message']
    }), 200 if result['success'] else 409

@papeletas_rrhh_bp.route('/modificar', methods=['PUT'])
@jwt_required()
@handle_response
def modificar_papeleta():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # Validar que se envíe el ID de la papeleta
    if 'idPapeleta' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idPapeleta'}), 400

    result = PapeletaRRHH.modificar_papeleta_rrhh(data, current_user, request.remote_addr)
    return jsonify({
        'success': result['success'], 
        'message': result['message']
    }), 200 if result['success'] else 409

@papeletas_rrhh_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_papeleta_rrhh():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # Validar campos requeridos para crear papeleta desde RRHH
    required_fields = [
        'idSede', 'idArea', 'idSolicitante', 
        'idTipoSalida', 'motivoSalida', 'fecha_salida', 
        'idTipoPapeleta'
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400

    result = PapeletaRRHH.crear_papeleta_rrhh(data, current_user, request.remote_addr)
    return jsonify({
        'success': result['success'], 
        'message': result['message']
    }), 201 if result['success'] else 409
@papeletas_rrhh_bp.route('/delete', methods=['DELETE'])
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

    result = PapeletaRRHH.eliminar_papeleta(data, current_user, request.remote_addr)
    
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