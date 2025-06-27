from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.controlAsistencias.papeletasModel import PapeletaModel
from ...utils.error_handlers import handle_response

papeletas_bp = Blueprint('papeletas', __name__)

# ==================== MÉTODOS DE CREACIÓN ====================

@papeletas_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_papeleta():
    """Crear nueva papeleta"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    required_fields = [
        'idSede', 'idArea', 'idsuperior', 'idSolicitante', 
        'idTipoSalida', 'motivoSalida', 'fecha_salida', 
        'idTipoPapeleta', 'horaSalida', 'horaRetorno'
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400

    result = PapeletaModel.create_papeleta(data, current_user, request.remote_addr)
    return jsonify(result), 201 if result.get('success') else 409

@papeletas_bp.route('/create-rrhh', methods=['POST'])
@jwt_required()
@handle_response
def create_papeleta_rrhh():
    """Crear papeleta por RRHH (aprobada automáticamente)"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    required_fields = [
        'idSede', 'idArea', 'idsuperior', 'idSolicitante', 
        'idTipoSalida', 'motivoSalida', 'fecha_salida', 
        'idTipoPapeleta', 'horaSalida', 'horaRetorno'
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400

    result = PapeletaModel.create_papeleta_rrhh(data, current_user, request.remote_addr)
    return jsonify(result), 201 if result.get('success') else 409

# ==================== MÉTODOS DE ACTUALIZACIÓN ====================

@papeletas_bp.route('/update/<int:idPapeleta>', methods=['PUT'])
@jwt_required()
@handle_response
def update_papeleta(idPapeleta):
    """Actualizar papeleta existente"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    data['idPapeleta'] = idPapeleta
    
    result = PapeletaModel.update_papeleta(data, current_user, request.remote_addr)
    return jsonify(result), 200 if result.get('success') else 409

@papeletas_bp.route('/update-jefe/<int:idPapeleta>', methods=['PUT'])
@jwt_required()
@handle_response
def update_papeleta_jefe(idPapeleta):
    """Modificar papeleta por jefe"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    data['idPapeleta'] = idPapeleta
    
    result = PapeletaModel.update_papeleta_jefe(data, current_user, request.remote_addr)
    return jsonify(result), 200 if result.get('success') else 409

@papeletas_bp.route('/update-rrhh/<int:idPapeleta>', methods=['PUT'])
@jwt_required()
@handle_response
def update_papeleta_rrhh(idPapeleta):
    """Modificar papeleta por RRHH"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    data['idPapeleta'] = idPapeleta
    
    result = PapeletaModel.update_papeleta_rrhh(data, current_user, request.remote_addr)
    return jsonify(result), 200 if result.get('success') else 409

# ==================== MÉTODOS DE CONSULTA ====================

@papeletas_bp.route('/<int:idPapeleta>', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_papeleta(idPapeleta):
    """Obtener papeleta específica"""
    result = PapeletaModel.get_papeleta(idPapeleta)
    
    if 'data' in result:
        return jsonify({
            'success': True,
            'data': result['data']
        }), 200
    else:
        return jsonify({'success': False, 'message': 'Papeleta no encontrada'}), 404

@papeletas_bp.route('/seguridad/<int:idPapeleta>', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_papeleta_seguridad(idPapeleta):
    """Obtener papeleta para seguridad"""
    result = PapeletaModel.get_papeleta_seguridad(idPapeleta)
    
    if 'data' in result:
        return jsonify({
            'success': True,
            'data': result['data']
        }), 200
    else:
        return jsonify({'success': False, 'message': 'Papeleta no encontrada'}), 404

@papeletas_bp.route('/rrhh/<int:idPapeleta>', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_papeleta_rrhh(idPapeleta):
    """Obtener papeleta para RRHH"""
    result = PapeletaModel.get_papeleta_rrhh(idPapeleta)
    
    if 'data' in result:
        return jsonify({
            'success': True,
            'data': result['data']
        }), 200
    else:
        return jsonify({'success': False, 'message': 'Papeleta no encontrada'}), 404

# ==================== MÉTODOS DE LISTADO ====================

# Agregar este nuevo endpoint POST para filtros complejos
@papeletas_bp.route('/list', methods=['POST'])
@jwt_required()
@handle_response(include_data=True)
def list_papeletas_post():
    """Listar papeletas con filtros JSON"""
    data = request.get_json() or {}
    
    # Obtener parámetros de paginación del JSON o valores por defecto
    page = data.get('inicio', 0)
    per_page = data.get('final', 10)
    
    # Filtros válidos
    valid_filters = [
        'idSede', 'idArea', 'idSolicitante', 'idTipoSalida', 
        'idTipoPapeleta', 'fechainicio', 'fechafin', 'nro', 
        'anio', 'nombres', 'apellidos', 'solicitante', 'idsuperior', 'motivoSalida'
    ]
    
    # Construir filtros desde el JSON
    filtros = {k: v for k, v in data.items() if k in valid_filters}
    
    # Convertir fecha_salida a fechainicio/fechafin si viene en el JSON
    if 'fecha_salida' in data and 'fechainicio' not in filtros and 'fechafin' not in filtros:
        fecha_salida = data['fecha_salida']
        # Si es una fecha completa, extraer solo la fecha
        if 'T' in str(fecha_salida):
            fecha_salida = str(fecha_salida).split('T')[0]
        filtros['fechainicio'] = fecha_salida
        filtros['fechafin'] = fecha_salida
    
    # Agregar parámetros de paginación
    filtros['inicio'] = page
    filtros['final'] = per_page
    
    # Imprimir para debug (remover en producción)
    print(f"Filtros enviados al SP: {filtros}")
    
    result = PapeletaModel.list_papeletas(filtros)
    count_result = PapeletaModel.count_papeletas(filtros)
    
    return jsonify({
        'success': True,
        'data': result.get('data', []),
        'pagination': {
            'total': count_result.get('count', 0),
            'current_page': page,
            'per_page': per_page
        },
        'debug_filters': filtros  # Remover en producción
    }), 200

# Modificar el endpoint GET existente para que sea más claro
@papeletas_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def list_papeletas_get():
    """Listar papeletas con query parameters"""
    # Obtener parámetros de paginación
    page = request.args.get('inicio', 0, type=int)
    per_page = request.args.get('final', 10, type=int)
    
    # Filtros válidos
    valid_filters = [
        'idSede', 'idArea', 'idSolicitante', 'idTipoSalida', 
        'idTipoPapeleta', 'fechainicio', 'fechafin', 'nro', 
        'anio', 'nombres', 'apellidos', 'solicitante', 'idsuperior', 'motivoSalida'
    ]
    filtros = {k: v for k, v in request.args.items() if k in valid_filters}
    
    # Convertir tipos de datos necesarios
    for key in ['idSede', 'idSolicitante', 'idTipoSalida', 'idTipoPapeleta', 'idsuperior', 'motivoSalida']:
        if key in filtros:
            try:
                filtros[key] = int(filtros[key])
            except ValueError:
                pass
    
    # Agregar parámetros de paginación
    filtros['inicio'] = page
    filtros['final'] = per_page
    
    # Imprimir para debug (remover en producción)
    print(f"Filtros GET enviados al SP: {filtros}")
    
    result = PapeletaModel.list_papeletas(filtros)
    count_result = PapeletaModel.count_papeletas(filtros)
    
    return jsonify({
        'success': True,
        'data': result.get('data', []),
        'pagination': {
            'total': count_result.get('count', 0),
            'current_page': page,
            'per_page': per_page
        }
    }), 200

@papeletas_bp.route('/list-rrhh', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def list_papeletas_rrhh():
    """Listar papeletas para RRHH"""
    # Obtener parámetros de paginación
    page = request.args.get('inicio', 0, type=int)
    per_page = request.args.get('final', 10, type=int)
    
    # Filtros válidos
    valid_filters = [
        'idSede', 'idArea', 'idSolicitante', 'idTipoSalida', 
        'idTipoPapeleta', 'fechainicio', 'fechafin', 'nro', 
        'anio', 'nombres', 'apellidos', 'solicitante'
    ]
    filtros = {k: v for k, v in request.args.items() if k in valid_filters}
    
    # Agregar parámetros de paginación
    filtros['inicio'] = page
    filtros['final'] = per_page
    
    result = PapeletaModel.list_papeletas_rrhh(filtros)
    count_result = PapeletaModel.count_papeletas_rrhh(filtros)
    
    return jsonify({
        'success': True,
        'data': result.get('data', []),
        'pagination': {
            'total': count_result.get('count', 0),
            'current_page': page,
            'per_page': per_page
        }
    }), 200

@papeletas_bp.route('/list-seguridad', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def list_papeletas_seguridad():
    """Listar papeletas para Seguridad"""
    # Obtener parámetros de paginación
    page = request.args.get('inicio', 0, type=int)
    per_page = request.args.get('final', 10, type=int)
    
    # Filtros válidos
    valid_filters = [
        'idSede', 'idArea', 'idSolicitante', 'idTipoSalida', 
        'idTipoPapeleta', 'fechainicio', 'fechafin', 'nro', 
        'anio', 'nombres', 'apellidos', 'solicitante'
    ]
    filtros = {k: v for k, v in request.args.items() if k in valid_filters}
    
    # Agregar parámetros de paginación
    filtros['inicio'] = page
    filtros['final'] = per_page
    
    result = PapeletaModel.list_papeletas_seguridad(filtros)
    count_result = PapeletaModel.count_papeletas_seguridad(filtros)
    
    return jsonify({
        'success': True,
        'data': result.get('data', []),
        'pagination': {
            'total': count_result.get('count', 0),
            'current_page': page,
            'per_page': per_page
        }
    }), 200

@papeletas_bp.route('/list-jefe', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def list_papeletas_jefe():
    """Listar papeletas por área - jefe"""
    # Obtener parámetros de paginación
    page = request.args.get('inicio', 0, type=int)
    per_page = request.args.get('final', 10, type=int)
    
    # Filtros válidos
    valid_filters = [
        'idSede', 'idArea', 'idSolicitante', 'idTipoSalida', 
        'idTipoPapeleta', 'fechainicio', 'fechafin', 'nro', 
        'anio', 'nombres', 'apellidos', 'solicitante'
    ]
    filtros = {k: v for k, v in request.args.items() if k in valid_filters}
    
    # Agregar parámetros de paginación
    filtros['inicio'] = page
    filtros['final'] = per_page
    
    result = PapeletaModel.list_papeletas_jefe(filtros)
    count_result = PapeletaModel.count_papeletas_jefe(filtros)
    
    return jsonify({
        'success': True,
        'data': result.get('data', []),
        'pagination': {
            'total': count_result.get('count', 0),
            'current_page': page,
            'per_page': per_page
        }
    }), 200

# ==================== MÉTODOS DE APROBACIÓN Y RECHAZO ====================

@papeletas_bp.route('/approve-rrhh/<int:idPapeleta>', methods=['PUT'])
@jwt_required()
@handle_response
def approve_rrhh(idPapeleta):
    """Aprobar papeleta por RRHH"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json() or {}
    data['idPapeleta'] = idPapeleta
    
    result = PapeletaModel.approve_rrhh(data, current_user, request.remote_addr)
    return jsonify(result), 200 if result.get('success') else 409

@papeletas_bp.route('/reject-rrhh/<int:idPapeleta>', methods=['PUT'])
@jwt_required()
@handle_response
def reject_rrhh(idPapeleta):
    """Rechazar papeleta por RRHH"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json() or {}
    data['idPapeleta'] = idPapeleta
    
    # Validar que se proporcione motivo de rechazo
    if not data.get('motivoModificacion'):
        return jsonify({'success': False, 'message': 'El motivo de rechazo es requerido'}), 400
    
    result = PapeletaModel.reject_rrhh(data, current_user, request.remote_addr)
    return jsonify(result), 200 if result.get('success') else 409

@papeletas_bp.route('/approve-jefe/<int:idPapeleta>', methods=['PUT'])
@jwt_required()
@handle_response
def approve_jefe(idPapeleta):
    """Aprobar papeleta por jefe"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json() or {}
    data['idPapeleta'] = idPapeleta
    
    result = PapeletaModel.approve_jefe(data, current_user, request.remote_addr)
    return jsonify(result), 200 if result.get('success') else 409

@papeletas_bp.route('/reject-jefe/<int:idPapeleta>', methods=['PUT'])
@jwt_required()
@handle_response
def reject_jefe(idPapeleta):
    """Rechazar papeleta por jefe"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json() or {}
    data['idPapeleta'] = idPapeleta
    
    # Validar que se proporcione motivo de rechazo
    if not data.get('motivoModificacion'):
        return jsonify({'success': False, 'message': 'El motivo de rechazo es requerido'}), 400
    
    result = PapeletaModel.reject_jefe(data, current_user, request.remote_addr)
    return jsonify(result), 200 if result.get('success') else 409

# ==================== MÉTODOS DE REGISTRO DE HORARIOS ====================

@papeletas_bp.route('/register-departure/<int:idPapeleta>', methods=['PUT'])
@jwt_required()
@handle_response
def register_departure_time(idPapeleta):
    """Registrar hora de salida"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json() or {}
    data['idPapeleta'] = idPapeleta
    
    result = PapeletaModel.register_departure_time(data, current_user, request.remote_addr)
    return jsonify(result), 200 if result.get('success') else 409

@papeletas_bp.route('/register-return/<int:idPapeleta>', methods=['PUT'])
@jwt_required()
@handle_response
def register_return_time(idPapeleta):
    """Registrar hora de retorno"""
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json() or {}
    data['idPapeleta'] = idPapeleta
    
    result = PapeletaModel.register_return_time(data, current_user, request.remote_addr)
    return jsonify(result), 200 if result.get('success') else 409

# ==================== MÉTODO DE HISTORIAL ====================

@papeletas_bp.route('/history/<int:idPapeleta>', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_approval_history(idPapeleta):
    """Obtener historial de aprobaciones"""
    result = PapeletaModel.get_approval_history(idPapeleta)
    
    if 'data' in result:
        return jsonify({
            'success': True,
            'data': result['data']
        }), 200
    else:
        return jsonify({'success': False, 'message': 'No se encontró historial'}), 404