from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.controlAsistencias.papeletasSegModel import PapeletaSeg
from ...utils.error_handlers import handle_response

papeletas_seg_bp = Blueprint('papeletas_seg', __name__)

@papeletas_seg_bp.route('/list', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def list_papeletas_seg():
    data = request.get_json() or {}
    
    try:
        # Primero obtener el conteo total (sin paginación)
        count_data = data.copy()
        count_data.pop('inicio', None)
        count_data.pop('final', None)
        
        count_result = PapeletaSeg.contar_papeletas_seg(count_data)
        total = count_result.get('total', 0)
        
        # Obtener los datos con paginación
        list_result = PapeletaSeg.consultar_papeletas_seg(data)
        
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
            'message': f'Error al consultar papeletas Seguridad: {str(e)}'
        }), 500

@papeletas_seg_bp.route('/get', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def get_papeleta_seg():
    data = request.get_json()
    
    # Validar que se envíe el ID de la papeleta
    if 'idPapeleta' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idPapeleta'}), 400

    result = PapeletaSeg.obtener_papeleta_seg(data['idPapeleta'])
    
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

@papeletas_seg_bp.route('/registrar-salida', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def registrar_salida():
    data = request.get_json()
    current_user = get_jwt_identity()
    
    # Validar campos requeridos
    if 'idPapeleta' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idPapeleta'}), 400
    
    if 'estacion' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: estacion'}), 400
    
    try:
        result = PapeletaSeg.registrar_hora_salida(
            idPapeleta=data['idPapeleta'],
            idUsuario_seg=current_user,
            estacion=data['estacion']
        )
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al registrar hora de salida: {str(e)}'
        }), 500


@papeletas_seg_bp.route('/registrar-retorno', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def registrar_retorno():
    data = request.get_json()
    current_user = get_jwt_identity()
    
    # Validar campos requeridos
    if 'idPapeleta' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: idPapeleta'}), 400
    
    if 'estacion' not in data:
        return jsonify({'success': False, 'message': 'Campo requerido: estacion'}), 400
    
    try:
        result = PapeletaSeg.registrar_hora_retorno(
            idPapeleta=data['idPapeleta'],
            idUsuario_seg=current_user,
            estacion=data['estacion']
        )
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al registrar hora de retorno: {str(e)}'
        }), 500