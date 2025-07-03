from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.controlAsistencias.asistenciasModel import Asistencia
from ...utils.error_handlers import handle_response

asistencias_bp = Blueprint('asistencias', __name__)

@asistencias_bp.route('/consulta-simple', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def consulta_simple():
    """
    Consulta simple de asistencias
    """
    data = request.get_json() or {}
    
    try:
        result = Asistencia.consulta_simple(data)
        
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
            'message': f'Error al realizar consulta simple: {str(e)}'
        }), 500

@asistencias_bp.route('/empleados', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def consulta_asistencia_empleados():
    """
    Consulta asistencia por empleados
    Campos opcionales: fechaInicio, fechaFin, idArea, dni, apellidos, nombres, idcondicion, dataxmlEmpleados
    """
    data = request.get_json() or {}
    
    try:
        result = Asistencia.consulta_asistencia_empleados(data)
        
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
            'message': f'Error al consultar asistencia de empleados: {str(e)}'
        }), 500

@asistencias_bp.route('/empleados-detalle', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def consulta_asistencia_empleados_detalle():
    """
    Consulta asistencia por empleados con detalle completo
    Campos opcionales: fechaInicio, fechaFin, idArea, dni, apellidos, nombres, idcondicion, dataxmlEmpleados
    """
    data = request.get_json() or {}
    
    try:
        result = Asistencia.consulta_asistencia_empleados_detalle(data)
        
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
            'message': f'Error al consultar detalle de asistencia: {str(e)}'
        }), 500

@asistencias_bp.route('/faltas-dia', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def consulta_faltas_del_dia():
    """
    Consulta faltas del día actual
    """
    data = request.get_json() or {}
    
    try:
        result = Asistencia.consulta_faltas_del_dia(data)
        
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
            'message': f'Error al consultar faltas del día: {str(e)}'
        }), 500

@asistencias_bp.route('/tardanzas-dia', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def consulta_tardanzas_del_dia():
    """
    Consulta tardanzas del día actual
    """
    data = request.get_json() or {}
    
    try:
        result = Asistencia.consulta_tardanzas_del_dia(data)
        
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
            'message': f'Error al consultar tardanzas del día: {str(e)}'
        }), 500

@asistencias_bp.route('/consolidado', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def consulta_asistencia_consolidado():
    """
    Consulta asistencia consolidada
    Campos opcionales: fechaInicio, fechaFin, idArea, dni, apellidos, nombres, idcondicion, dataxmlEmpleados
    """
    data = request.get_json() or {}
    
    try:
        result = Asistencia.consulta_asistencia_consolidado(data)
        
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
            'message': f'Error al consultar asistencia consolidada: {str(e)}'
        }), 500

@asistencias_bp.route('/empleados-list', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def consulta_empleados():
    """
    Consulta empleados con filtros
    Campos opcionales: idArea, idcondicion, dni, apellidos, nombres
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

@asistencias_bp.route('/empleados-count', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def conteo_empleados():
    """
    Conteo de empleados activos
    """
    data = request.get_json() or {}
    
    try:
        result = Asistencia.conteo_empleados(data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'total': result['total']
            }), 200
        else:
            return jsonify({
                'success': False, 
                'message': result.get('message', 'Error en la consulta')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error al contar empleados: {str(e)}'
        }), 500

@asistencias_bp.route('/consolidado-test', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def consulta_asistencia_consolidado_test():
    """
    Consulta asistencia consolidada con errores (versión test)
    Campos opcionales: fechaInicio, fechaFin, idArea, dni, apellidos, nombres, idcondicion, dataxmlEmpleados
    """
    data = request.get_json() or {}
    
    try:
        result = Asistencia.consulta_asistencia_consolidado_test(data)
        
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
            'message': f'Error al consultar asistencia consolidada test: {str(e)}'
        }), 500