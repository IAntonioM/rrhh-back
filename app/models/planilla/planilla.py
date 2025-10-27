from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.planilla.planilla import PlanillaModel
from ...utils.error_handlers import handle_response
import re

planilla_bp = Blueprint('planilla', __name__)

# Handler para errores SQL
def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'


@planilla_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_planilla():
    """
    Crear una nueva planilla - @mquery = 1
    Body JSON:
    {
        "idGrupo": int,
        "idPeriodo": int,
        "fechaDesde": "YYYY-MM-DD",
        "fechaHasta": "YYYY-MM-DD",
        "observaciones": str (opcional)
    }
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validaciones
    required_fields = ['idGrupo', 'idPeriodo', 'fechaDesde', 'fechaHasta']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'message': f'El campo {field} es obligatorio'
            }), 400
    
    success, message = PlanillaModel.create_planilla(
        data,
        current_user,
        request.remote_addr
    )
    
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409


@planilla_bp.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_planilla(id):
    """
    Eliminar una planilla - @mquery = 3
    Solo se pueden eliminar planillas en estado 1 (Registrada) o 5 (Anulada)
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    success, message = PlanillaModel.delete_planilla(
        id,
        current_user,
        request.remote_addr
    )
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409


@planilla_bp.route('/list', methods=['GET', 'POST'])
@jwt_required()
@handle_response
def list_planillas():
    """
    Listar planillas con filtros - @mquery = 5
    Query params o JSON body:
    - idPeriodoDesde: int (opcional)
    - idPeriodoHasta: int (opcional)
    """
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = request.args.to_dict()
    
    filters = {
        'idPeriodoDesde': int(data.get('idPeriodoDesde', 0)) if data.get('idPeriodoDesde') else 0,
        'idPeriodoHasta': int(data.get('idPeriodoHasta', 0)) if data.get('idPeriodoHasta') else 0
    }
    
    result = PlanillaModel.list_planillas(filters)
    return jsonify(result), 200


@planilla_bp.route('/count', methods=['GET'])
@jwt_required()
@handle_response
def count_planillas():
    """Contar planillas activas - @mquery = 6"""
    result = PlanillaModel.count_planillas()
    return jsonify(result), 200


@planilla_bp.route('/procesar/<int:id>', methods=['POST'])
@jwt_required()
@handle_response
def procesar_planilla(id):
    """
    Procesar planilla CAS - @mquery = 10
    Solo se pueden procesar planillas en estado 1 (Registrada)
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    success, message = PlanillaModel.procesar_planilla_cas(
        id,
        current_user,
        request.remote_addr
    )
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409


@planilla_bp.route('/reprocesar/<int:id>', methods=['POST'])
@jwt_required()
@handle_response
def reprocesar_planilla(id):
    """
    Reprocesar planilla CAS - @mquery = 11
    Body JSON:
    {
        "motivo": str (obligatorio)
    }
    Solo se pueden reprocesar planillas en estado 2 (Procesada) o 3 (Reprocesada)
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validar motivo
    motivo = data.get('motivo', '').strip()
    if not motivo:
        return jsonify({
            'success': False,
            'message': 'El motivo es obligatorio para reprocesar la planilla'
        }), 400
    
    success, message = PlanillaModel.reprocesar_planilla_cas(
        id,
        motivo,
        current_user,
        request.remote_addr
    )
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409


@planilla_bp.route('/anular/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
@handle_response
def anular_planilla(id):
    """Anular una planilla - @mquery = 12"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    success, message = PlanillaModel.anular_planilla(
        id,
        current_user,
        request.remote_addr
    )
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409


@planilla_bp.route('/cerrar/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
@handle_response
def cerrar_planilla(id):
    """Cerrar una planilla - @mquery = 13"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    success, message = PlanillaModel.cerrar_planilla(
        id,
        current_user,
        request.remote_addr
    )
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409


@planilla_bp.route('/conceptos/<int:idPlanilla>/<int:idEmpleado>', methods=['GET'])
@jwt_required()
@handle_response
def get_conceptos_consolidados(idPlanilla, idEmpleado):
    """
    Obtener conceptos consolidados de un empleado en una planilla - @mquery = 50
    """
    result = PlanillaModel.get_conceptos_consolidados(idPlanilla, idEmpleado)
    return jsonify(result), 200


@planilla_bp.route('/estados', methods=['GET'])
@jwt_required()
@handle_response
def get_estados():
    """Obtener la lista de estados disponibles para planillas"""
    estados = [
        {'id': 1, 'nombre': 'REGISTRADA', 'color': 'info'},
        {'id': 2, 'nombre': 'PROCESADA', 'color': 'success'},
        {'id': 3, 'nombre': 'REPROCESADA', 'color': 'warning'},
        {'id': 4, 'nombre': 'CERRADA', 'color': 'secondary'},
        {'id': 5, 'nombre': 'ANULADA', 'color': 'danger'},
        {'id': 99, 'nombre': 'ELIMINADA', 'color': 'dark'}
    ]
    
    return jsonify({
        'success': True,
        'data': estados
    }), 200