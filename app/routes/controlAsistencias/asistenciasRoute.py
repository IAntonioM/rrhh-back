from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.controlAsistencias.asistenciasModel import Asistencia
from ...utils.error_handlers import handle_response

asistencias_bp = Blueprint('asistencias', __name__)

@asistencias_bp.route('/asistencias-por-empleado', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def consulta_asistencias_por_empleado():
    """
    Consulta asistencias por empleado
    Campos: idEmpleado (requerido), nombreEmpleado, idArea, idcondicion, dni, fecha_desde, fecha_hasta
    """
    data = request.get_json() or {}
    
    try:
        result = Asistencia.consulta_asistencias_por_empleado(data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data']
            }), 200
        else:
            return jsonify({
                'success': False, 
                'message': result.get('message', 'Error en la consulta')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error al consultar asistencias por empleado: {str(e)}'
        }), 500

@asistencias_bp.route('/asistencias-detalladas-por-empleado', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def consulta_asistencias_detalladas_por_empleado():
    """
    Consulta asistencias detalladas por empleado
    Campos: idEmpleado (requerido), nombreEmpleado, idArea, idcondicion, dni, fecha_desde, fecha_hasta
    """
    data = request.get_json() or {}
    
    try:
        result = Asistencia.consulta_asistencias_detalladas_por_empleado(data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data']
            }), 200
        else:
            return jsonify({
                'success': False, 
                'message': result.get('message', 'Error en la consulta')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error al consultar asistencias detalladas por empleado: {str(e)}'
        }), 500

@asistencias_bp.route('/empleados-list', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def consulta_empleados():
    """
    Consulta empleados con filtros
    Campos opcionales: idArea, idcondicion, dni, nombreEmpleado
    """
    data = request.get_json() or {}
    
    try:
        result = Asistencia.consulta_empleados(data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data']
            }), 200
        else:
            return jsonify({
                'success': False, 
                'message': result.get('message', 'Error en la consulta')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error al consultar empleados: {str(e)}'
        }), 500