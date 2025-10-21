from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.planilla.grupo import GrupoModel
from ...utils.error_handlers import handle_response
import re

grupo_bp = Blueprint('grupo', __name__)

# Handler para errores SQL
def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'


@grupo_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_grupo():
    """Crear un nuevo grupo"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validaciones básicas
    if not data.get('nombre'):
        return jsonify({
            'success': False,
            'message': 'El nombre del grupo es obligatorio'
        }), 400
    
    success, message = GrupoModel.create_grupo(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409


@grupo_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response
def list_grupos():
    """Listar todos los grupos activos"""
    result = GrupoModel.list_grupos()
    return jsonify(result), 200


@grupo_bp.route('/get/<int:id>', methods=['GET'])
@jwt_required()
@handle_response
def get_grupo(id):
    """Obtener un grupo por ID"""
    result = GrupoModel.get_grupo_by_id(id)
    return jsonify(result), 200


@grupo_bp.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
@handle_response
def update_grupo(id):
    """Actualizar un grupo"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    data['idGrupo'] = id
    
    # Validaciones básicas
    if not data.get('nombre'):
        return jsonify({
            'success': False,
            'message': 'El nombre del grupo es obligatorio'
        }), 400
    
    success, message = GrupoModel.update_grupo(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409


@grupo_bp.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_grupo(id):
    """Eliminar un grupo"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    success, message = GrupoModel.delete_grupo(id, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409


@grupo_bp.route('/count', methods=['GET'])
@jwt_required()
@handle_response
def count_grupos():
    """Contar grupos activos"""
    result = GrupoModel.count_grupos()
    return jsonify(result), 200


# ===== ENDPOINTS PARA EMPLEADOS EN GRUPOS =====

@grupo_bp.route('/empleado/add', methods=['POST'])
@jwt_required()
@handle_response
def add_empleado_grupo():
    """Agregar un empleado a un grupo"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validaciones
    if not data.get('idEmpleado'):
        return jsonify({
            'success': False,
            'message': 'El ID del empleado es obligatorio'
        }), 400
    
    if not data.get('idGrupo'):
        return jsonify({
            'success': False,
            'message': 'El ID del grupo es obligatorio'
        }), 400
    
    success, message = GrupoModel.add_empleado_grupo(
        data['idEmpleado'],
        data['idGrupo'],
        current_user,
        request.remote_addr
    )
    
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409


@grupo_bp.route('/empleado/remove/<int:idEmpGrupo>', methods=['DELETE'])
@jwt_required()
@handle_response
def remove_empleado_grupo(idEmpGrupo):
    """Eliminar un empleado de un grupo"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    success, message = GrupoModel.remove_empleado_grupo(
        idEmpGrupo,
        current_user,
        request.remote_addr
    )
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409


@grupo_bp.route('/empleados', methods=['GET'])
@jwt_required()
@handle_response
def list_empleados_by_grupo():
    """Listar empleados de un grupo específico con paginación"""
    # Obtener parámetros de la query
    id_grupo = request.args.get('idGrupo', type=int)
    # Validar parámetros obligatorios
    if not id_grupo:
        return jsonify({'error': 'Falta el parámetro idGrupo'}), 400

    # Llamar al modelo con los parámetros
    result = GrupoModel.list_empleados_by_grupo(id_grupo)

    return jsonify(result), 200


# ===== ENDPOINTS PARA COMBOS =====

@grupo_bp.route('/combo/planilla', methods=['GET'])
@jwt_required()
@handle_response
def combo_grupos_planilla():
    """Obtener combo de grupos de planilla"""
    result = GrupoModel.combo_grupos_planilla()
    return jsonify(result), 200


@grupo_bp.route('/combo/planilla-asistencia/<int:periodo>', methods=['GET'])
@jwt_required()
@handle_response
def combo_grupos_planilla_asis(periodo):
    """Obtener combo de grupos de planilla por periodo para asistencia"""
    result = GrupoModel.combo_grupos_planilla_asis(periodo)
    return jsonify(result), 200