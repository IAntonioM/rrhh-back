from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...models.controlAsistencias.reportesAsistenciaModel import ReportesAsistenciaModel
from ...utils.error_handlers import handle_response

reportes_asistencia_bp = Blueprint('reportes_asistencia', __name__)

@reportes_asistencia_bp.route('/asistencia-diaria', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_asistencia_diaria():
    """
    REPORTE 1: Asistencia Diaria Detallada
    Parámetros opcionales: fecha_inicio, fecha_fin (formato: YYYY-MM-DD)
    Si no se envían, usa el mes actual
    """
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    try:
        data = ReportesAsistenciaModel.get_reporte_asistencia_diaria(fecha_inicio, fecha_fin)
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@reportes_asistencia_bp.route('/resumen-mensual', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_resumen_mensual():
    """
    REPORTE 2: Resumen Mensual de Asistencias
    Parámetros opcionales: mes (1-12), anio (YYYY)
    Si no se envían, usa el mes y año actual
    """
    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)
    
    try:
        data = ReportesAsistenciaModel.get_reporte_resumen_mensual(mes, anio)
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@reportes_asistencia_bp.route('/marcaciones-irregulares', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_marcaciones_irregulares():
    """
    REPORTE 3: Empleados con Marcaciones Irregulares
    Parámetros opcionales: fecha_inicio, fecha_fin (formato: YYYY-MM-DD)
    """
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    try:
        data = ReportesAsistenciaModel.get_reporte_marcaciones_irregulares(fecha_inicio, fecha_fin)
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@reportes_asistencia_bp.route('/ranking-puntualidad', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_ranking_puntualidad():
    """
    REPORTE 4: Ranking de Puntualidad por Cargo
    Parámetros opcionales: fecha_inicio, fecha_fin (formato: YYYY-MM-DD)
    """
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    try:
        data = ReportesAsistenciaModel.get_reporte_ranking_puntualidad(fecha_inicio, fecha_fin)
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@reportes_asistencia_bp.route('/ausentismo-dia-semana', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_ausentismo_dia_semana():
    """
    REPORTE 5: Ausentismo por Día de la Semana
    Parámetros opcionales: fecha_inicio, fecha_fin (formato: YYYY-MM-DD)
    """
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    try:
        data = ReportesAsistenciaModel.get_reporte_ausentismo_dia_semana(fecha_inicio, fecha_fin)
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@reportes_asistencia_bp.route('/cumplimiento-horario', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_cumplimiento_horario():
    """
    REPORTE 6: Cumplimiento de Horario - Llegadas Tarde
    Parámetros opcionales: fecha_inicio, fecha_fin (formato: YYYY-MM-DD)
    """
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    try:
        data = ReportesAsistenciaModel.get_reporte_cumplimiento_horario(fecha_inicio, fecha_fin)
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@reportes_asistencia_bp.route('/horas-trabajadas', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_horas_trabajadas():
    """
    REPORTE 7: Horas Trabajadas vs Horas Programadas
    Parámetros opcionales: fecha_inicio, fecha_fin (formato: YYYY-MM-DD)
    """
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    try:
        data = ReportesAsistenciaModel.get_reporte_horas_trabajadas(fecha_inicio, fecha_fin)
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@reportes_asistencia_bp.route('/empleados-por-turno', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_empleados_por_turno():
    """
    REPORTE 8: Horarios Rotativos - Empleados por Turno
    Parámetros opcionales: fecha (formato: YYYY-MM-DD)
    Si no se envía, usa la fecha actual
    """
    fecha = request.args.get('fecha')
    
    try:
        data = ReportesAsistenciaModel.get_reporte_empleados_por_turno(fecha)
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@reportes_asistencia_bp.route('/control-refrigerio', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_control_refrigerio():
    """
    REPORTE 9: Control de Refrigerio/Break
    Parámetros opcionales: fecha_inicio, fecha_fin (formato: YYYY-MM-DD)
    """
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    try:
        data = ReportesAsistenciaModel.get_reporte_control_refrigerio(fecha_inicio, fecha_fin)
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

# ============================================================================
# Endpoint consolidado (opcional) - para obtener cualquier reporte por tipo
# ============================================================================
@reportes_asistencia_bp.route('/reporte', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_reporte_general():
    """
    Endpoint consolidado para obtener cualquier reporte
    Parámetros requeridos: tipo_reporte (1-9)
    Parámetros opcionales: fecha_inicio, fecha_fin, mes, anio, fecha
    """
    tipo_reporte = request.args.get('tipo_reporte', type=int)
    
    if not tipo_reporte or tipo_reporte < 1 or tipo_reporte > 9:
        return jsonify({
            'success': False,
            'message': 'Tipo de reporte inválido. Debe ser un número entre 1 y 9'
        }), 400
    
    try:
        if tipo_reporte == 1:
            fecha_inicio = request.args.get('fecha_inicio')
            fecha_fin = request.args.get('fecha_fin')
            data = ReportesAsistenciaModel.get_reporte_asistencia_diaria(fecha_inicio, fecha_fin)
            
        elif tipo_reporte == 2:
            mes = request.args.get('mes', type=int)
            anio = request.args.get('anio', type=int)
            data = ReportesAsistenciaModel.get_reporte_resumen_mensual(mes, anio)
            
        elif tipo_reporte == 3:
            fecha_inicio = request.args.get('fecha_inicio')
            fecha_fin = request.args.get('fecha_fin')
            data = ReportesAsistenciaModel.get_reporte_marcaciones_irregulares(fecha_inicio, fecha_fin)
            
        elif tipo_reporte == 4:
            fecha_inicio = request.args.get('fecha_inicio')
            fecha_fin = request.args.get('fecha_fin')
            data = ReportesAsistenciaModel.get_reporte_ranking_puntualidad(fecha_inicio, fecha_fin)
            
        elif tipo_reporte == 5:
            fecha_inicio = request.args.get('fecha_inicio')
            fecha_fin = request.args.get('fecha_fin')
            data = ReportesAsistenciaModel.get_reporte_ausentismo_dia_semana(fecha_inicio, fecha_fin)
            
        elif tipo_reporte == 6:
            fecha_inicio = request.args.get('fecha_inicio')
            fecha_fin = request.args.get('fecha_fin')
            data = ReportesAsistenciaModel.get_reporte_cumplimiento_horario(fecha_inicio, fecha_fin)
            
        elif tipo_reporte == 7:
            fecha_inicio = request.args.get('fecha_inicio')
            fecha_fin = request.args.get('fecha_fin')
            data = ReportesAsistenciaModel.get_reporte_horas_trabajadas(fecha_inicio, fecha_fin)
            
        elif tipo_reporte == 8:
            fecha = request.args.get('fecha')
            data = ReportesAsistenciaModel.get_reporte_empleados_por_turno(fecha)
            
        elif tipo_reporte == 9:
            fecha_inicio = request.args.get('fecha_inicio')
            fecha_fin = request.args.get('fecha_fin')
            data = ReportesAsistenciaModel.get_reporte_control_refrigerio(fecha_inicio, fecha_fin)
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400