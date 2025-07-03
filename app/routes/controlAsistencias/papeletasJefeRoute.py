from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.controlAsistencias.papeletasJefeModel import PapeletaJefe
from ...utils.error_handlers import handle_response

papeletas_jefe_bp = Blueprint('papeletas_jefe', __name__)

@papeletas_jefe_bp.route('/list', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def list_papeletas_jefe():
    """
    Lista papeletas para jefe con filtros y paginación
    """
    data = request.get_json() or {}
    
    try:
        # Primero obtener el conteo total (sin paginación)
        count_data = data.copy()
        count_data.pop('inicio', None)
        count_data.pop('final', None)
        
        count_result = PapeletaJefe.contar_papeletas_jefe(count_data)
        total = count_result.get('total', 0)
        
        # Obtener los datos con paginación
        list_result = PapeletaJefe.consultar_papeletas_jefe(data)
        
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
            'message': f'Error al consultar papeletas jefe: {str(e)}'
        }), 500

@papeletas_jefe_bp.route('/aprobar', methods=['POST'])
@jwt_required()
@handle_response
def aprobar_papeleta():
    """
    Aprobar papeleta por jefe
    Campos requeridos: idPapeleta
    Campos opcionales: horaSalida, horaRetorno
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # Validar que se envíe el ID de la papeleta
    if 'idPapeleta' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idPapeleta'}), 400

    # Agregar usuario jefe a los datos
    data['idUsuario_jefe'] = current_user

    result = PapeletaJefe.aprobar_papeleta_jefe(data, current_user, request.remote_addr)
    return jsonify({
        'success': result['success'], 
        'message': result['message']
    }), 200 if result['success'] else 409

@papeletas_jefe_bp.route('/rechazar', methods=['POST'])
@jwt_required()
@handle_response
def rechazar_papeleta():
    """
    Rechazar papeleta por jefe
    Campos requeridos: idPapeleta
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # Validar que se envíe el ID de la papeleta
    if 'idPapeleta' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idPapeleta'}), 400

    # Agregar usuario jefe a los datos
    data['idUsuario_jefe'] = current_user

    result = PapeletaJefe.rechazar_papeleta_jefe(data, current_user, request.remote_addr)
    return jsonify({
        'success': result['success'], 
        'message': result['message']
    }), 200 if result['success'] else 409

@papeletas_jefe_bp.route('/modificar', methods=['PUT'])
@jwt_required()
@handle_response
def modificar_papeleta():
    """
    Modificar papeleta por jefe
    Campos requeridos: idPapeleta, idSolicitante, idTipoSalida, motivoSalida, fecha_salida, idTipoPapeleta
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = [
        'idPapeleta', 'idSolicitante', 'idTipoSalida', 
        'motivoSalida', 'fecha_salida', 'idTipoPapeleta'
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400

    result = PapeletaJefe.modificar_papeleta_jefe(data, current_user, request.remote_addr)
    return jsonify({
        'success': result['success'], 
        'message': result['message']
    }), 200 if result['success'] else 409