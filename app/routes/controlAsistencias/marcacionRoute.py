from flask import Blueprint, request, jsonify
from ...models.controlAsistencias.marcacionModel import Marcaciones
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

# Crear el blueprint
marcaciones_bp = Blueprint('marcaciones', __name__)

@marcaciones_bp.route('/registrar', methods=['POST'])
@jwt_required()
def registrar_marcacion():
    """
    Registra una nueva marcación
    
    Body JSON:
    {
        "fechaMarcacion": "2025-06-26",
        "horaMarcacion": "08:20",
        "idEmpleado": 2117,
        "observacion": "Ingreso manual"
    }
    """
    try:
        current_user = get_jwt_identity()
        remote_addr = request.remote_addr
        
        data = request.get_json()
        
        # Validar que se envió JSON
        if not data:
            return jsonify({
                'success': False, 
                'message': 'No se enviaron datos en formato JSON'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['fechaMarcacion', 'horaMarcacion', 'idEmpleado']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Campos requeridos faltantes: {", ".join(missing_fields)}'
            }), 400
        
        # Validar formato de fecha
        try:
            datetime.strptime(data['fechaMarcacion'], '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }), 400
        
        # Validar formato de hora
        try:
            datetime.strptime(data['horaMarcacion'], '%H:%M')
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Formato de hora inválido. Use HH:MM'
            }), 400
        
        result = Marcaciones.registrar_marcacion(data, current_user, remote_addr)
        
        if result.get('success'):
            return jsonify({
                'success': True, 
                'message': result.get('message')
            }), 201
        else:
            return jsonify({
                'success': False, 
                'message': result.get('message')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }), 500

@marcaciones_bp.route('/listar', methods=['GET'])
@jwt_required()
def listar_marcaciones():
    """
    Lista marcaciones con filtros opcionales
    
    Query parameters:
    - deFecha: Fecha inicio (YYYY-MM-DD) - REQUERIDO
    - hastaFecha: Fecha fin (YYYY-MM-DD) - REQUERIDO
    - idArea: ID del área
    - idCargo: ID del cargo
    - dni: DNI del empleado
    - nombres: Nombres del empleado (búsqueda parcial)
    - inicio: Número de página inicio (para paginación)
    - final: Número de página fin (para paginación)
    """
    try:
        # Obtener parámetros de consulta
        de_fecha = request.args.get('deFecha', '1900-01-01')
        hasta_fecha = request.args.get('hastaFecha', '1900-01-01')
        
        # Validar que se proporcionen las fechas
        if de_fecha == '1900-01-01' or hasta_fecha == '1900-01-01':
            return jsonify({
                'success': False,
                'message': 'Las fechas de inicio y fin son requeridas'
            }), 400
        
        # Validar formato de fechas
        try:
            datetime.strptime(de_fecha, '%Y-%m-%d')
            datetime.strptime(hasta_fecha, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }), 400
        
        filtros = {
            'deFecha': de_fecha,
            'hastaFecha': hasta_fecha,
            'idArea': request.args.get('idArea', ''),
            'idCargo': request.args.get('idCargo', ''),
            'dni': request.args.get('dni', ''),
            'nombres': request.args.get('nombres', ''),
            'inicio': int(request.args.get('inicio', 0)),
            'final': int(request.args.get('final', 0))
        }
        
        result = Marcaciones.listar_marcaciones(filtros)
        
        if 'data' in result:
            return jsonify({
                'success': True,
                'data': result['data'],
                'total_records': len(result['data'])
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'Error al consultar marcaciones')
            }), 400
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f'Error en los parámetros: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }), 500

@marcaciones_bp.route('/contar', methods=['GET'])
@jwt_required()
def contar_marcaciones():
    """
    Cuenta el total de marcaciones con filtros opcionales
    
    Query parameters:
    - deFecha: Fecha inicio (YYYY-MM-DD)
    - hastaFecha: Fecha fin (YYYY-MM-DD)
    - idArea: ID del área
    - idCargo: ID del cargo
    - dni: DNI del empleado
    - nombres: Nombres del empleado (búsqueda parcial)
    """
    try:
        filtros = {
            'deFecha': request.args.get('deFecha', '1900-01-01'),
            'hastaFecha': request.args.get('hastaFecha', '1900-01-01'),
            'idArea': request.args.get('idArea', ''),
            'idCargo': request.args.get('idCargo', ''),
            'dni': request.args.get('dni', ''),
            'nombres': request.args.get('nombres', '')
        }
        
        # Validar formato de fechas si se proporcionan
        if filtros['deFecha'] != '1900-01-01':
            try:
                datetime.strptime(filtros['deFecha'], '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Formato de fecha de inicio inválido. Use YYYY-MM-DD'
                }), 400
        
        if filtros['hastaFecha'] != '1900-01-01':
            try:
                datetime.strptime(filtros['hastaFecha'], '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Formato de fecha de fin inválido. Use YYYY-MM-DD'
                }), 400
        
        result = Marcaciones.contar_marcaciones(filtros)
        
        if 'total' in result:
            return jsonify({
                'success': True,
                'total': result['total']
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'Error al contar marcaciones')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }), 500

@marcaciones_bp.route('/empleado/<int:id_empleado>/validar', methods=['GET'])

# Ruta de prueba para verificar el funcionamiento
@marcaciones_bp.route('/health', methods=['GET'])
def health_check():
    """
    Verifica el estado del módulo de marcaciones
    """
    return jsonify({
        'success': True,
        'message': 'Módulo de marcaciones funcionando correctamente',
        'timestamp': datetime.now().isoformat()
    }), 200

# Manejo de errores específicos del blueprint
@marcaciones_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint no encontrado'
    }), 404

@marcaciones_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'message': 'Método HTTP no permitido'
    }), 405

@marcaciones_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Error interno del servidor'
    }), 500