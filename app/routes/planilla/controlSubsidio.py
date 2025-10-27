from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.planilla.controlSubsidio import ControlSubsidioModel
from ...utils.error_handlers import handle_response
import re

contro_subsidio_bp = Blueprint('control_subsidio', __name__)

# Handler para errores SQL
def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'


@contro_subsidio_bp.route('/list', methods=['GET', 'POST'])
@jwt_required()
@handle_response
def list_subsidios():
    """
    Listar subsidios con filtros y paginación
    Query params o JSON body:
    - page: int (default: 1)
    - per_page: int (default: 10)
    - idCentroCosto: int (opcional)
    - dni: str (opcional)
    - nombre_completo: str (opcional)
    - estado: int (0-4, opcional, -1 para todos)
    - fechaDesde: str (YYYY-MM-DD, opcional)
    - fechaHasta: str (YYYY-MM-DD, opcional)
    """
    # Aceptar filtros por query params o JSON body
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = request.args.to_dict()
    
    page = int(data.get('page', 1))
    per_page = int(data.get('per_page', 10))
    
    filters = {
        'idCentroCosto': int(data.get('idCentroCosto', 0)) if data.get('idCentroCosto') else 0,
        'dni': data.get('dni', ''),
        'nombre_completo': data.get('nombre_completo', ''),
        'estado': int(data.get('estado', -1)) if data.get('estado') else -1,
        'fechaDesde': data.get('fechaDesde', None),
        'fechaHasta': data.get('fechaHasta', None),
        'idCondicionLaboral': int(data.get('idCondicionLaboral', 0)) if data.get('idCondicionLaboral') else 0,
        'idCargo': int(data.get('idCargo', 0)) if data.get('idCargo') else 0,
        'mes': int(data.get('mes', 0)) if data.get('mes') else 0,
        'anio': int(data.get('anio', 0)) if data.get('anio') else 0
    }
    
    result = ControlSubsidioModel.list_subsidios(filters, page, per_page)
    return jsonify(result), 200




@contro_subsidio_bp.route('/get/<int:id>', methods=['GET'])
@jwt_required()
@handle_response
def get_subsidio(id):
    """Obtener un subsidio por ID"""
    result = ControlSubsidioModel.get_subsidio_by_id(id)
    return jsonify(result), 200


@contro_subsidio_bp.route('/update/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
@handle_response
def update_estado(id):
    """
    Actualizar el estado de un subsidio
    Body JSON:
    {
        "estado": int (0=No atendido, 1=Atendido, 2=Proc.Judicial, 3=Perdido, 4=Por cobrar)
    }
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validación del estado
    estado = data.get('estado')
    if estado is None:
        return jsonify({
            'success': False,
            'message': 'El estado es obligatorio'
        }), 400
    
    if not isinstance(estado, int) or estado < 0 or estado > 4:
        return jsonify({
            'success': False,
            'message': 'Estado inválido. Use: 0=No atendido, 1=Atendido, 2=Proc.Judicial, 3=Perdido, 4=Por cobrar'
        }), 400
    
    success, message = ControlSubsidioModel.update_estado_subsidio(
        id, 
        estado, 
        current_user, 
        request.remote_addr
    )
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409



@contro_subsidio_bp.route('/count', methods=['GET', 'POST'])
@jwt_required()
@handle_response
def count_subsidios():
    """
    Contar subsidios con filtros
    Query params o JSON body:
    - idCentroCosto: int (opcional)
    - dni: str (opcional)
    - nombre_completo: str (opcional)
    - estado: int (0-4, opcional)
    """
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = request.args.to_dict()
    
    filters = {
        'idCentroCosto': int(data.get('idCentroCosto', 0)) if data.get('idCentroCosto') else 0,
        'dni': data.get('dni', ''),
        'nombre_completo': data.get('nombre_completo', ''),
        'estado': int(data.get('estado', -1)) if data.get('estado') else -1
    }
    
    result = ControlSubsidioModel.count_subsidios(filters)
    return jsonify(result), 200


@contro_subsidio_bp.route('/estados', methods=['GET'])
@jwt_required()
@handle_response
def get_estados():
    """Obtener la lista de estados disponibles"""
    estados = [
        {'id': 0, 'nombre': 'NO ATENDIDO', 'color': 'warning'},
        {'id': 1, 'nombre': 'ATENDIDO', 'color': 'success'},
        {'id': 2, 'nombre': 'PROCESO JUDICIAL', 'color': 'info'},
        {'id': 3, 'nombre': 'PERDIDO', 'color': 'danger'},
        {'id': 4, 'nombre': 'POR COBRAR', 'color': 'primary'}
    ]
    
    return jsonify({
        'success': True,
        'data': estados
    }), 200