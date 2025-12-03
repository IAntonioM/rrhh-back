from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.reportes.PrediccionAusencias import PrediccionAusencias
from ...utils.error_handlers import handle_response
import os

prediccion_ausencias_bp = Blueprint('prediccion_ausencias', __name__)

@prediccion_ausencias_bp.route('/generar', methods=['POST'])
@jwt_required()
@handle_response
def generar_reportes():
    """
    Genera reportes de predicción de ausencias manualmente
    Solo para testing/emergencias
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    print(f"🔄 Generación manual de reportes iniciada por: {current_user}")
    
    # Ejecutar pipeline
    result = PrediccionAusencias.ejecutar_pipeline_ml()
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': result['message'],
            'data': {
                'timestamp': result['timestamp'],
                'total_registros': result['total_registros']
            }
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': result['message']
        }), 500


@prediccion_ausencias_bp.route('/ultimo', methods=['GET'])
@jwt_required()
@handle_response
def obtener_ultimo_reporte():
    """
    Obtiene el último reporte general generado
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    result = PrediccionAusencias.obtener_ultimo_reporte_general()
    
    if result['success']:
        return jsonify({
            'success': True,
            'data': {
                'nombre': result['nombre'],
                'fecha_creacion': result['fecha_creacion']
            }
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': result['message']
        }), 404


@prediccion_ausencias_bp.route('/ver-ultimo', methods=['GET'])
@jwt_required()
def ver_ultimo_reporte():
    """
    Retorna el HTML del último reporte general
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    # Obtener último reporte
    result = PrediccionAusencias.obtener_ultimo_reporte_general()
    
    if not result['success']:
        return jsonify({
            'success': False,
            'message': result['message']
        }), 404
    
    # Leer contenido
    contenido_result = PrediccionAusencias.leer_reporte_html(result['ruta'])
    
    if not contenido_result['success']:
        return jsonify({
            'success': False,
            'message': contenido_result['message']
        }), 500
    
    # Retornar HTML directamente
    return contenido_result['contenido'], 200, {'Content-Type': 'text/html; charset=utf-8'}


@prediccion_ausencias_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response
def listar_reportes():
    """
    Lista todos los reportes disponibles con paginación
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    # Parámetros de paginación
    page = request.args.get('current_page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    tipo_filtro = request.args.get('tipo', None)  # 'general' o 'individual'
    
    # Obtener reportes
    result = PrediccionAusencias.listar_reportes()
    
    if not result['success']:
        return jsonify({
            'success': False,
            'message': result['message']
        }), 500
    
    reportes = result['data']
    
    # Filtrar por tipo si se especifica
    if tipo_filtro:
        reportes = [r for r in reportes if r['tipo'] == tipo_filtro]
    
    # Paginación manual
    total = len(reportes)
    start = (page - 1) * per_page
    end = start + per_page
    reportes_paginados = reportes[start:end]
    
    return jsonify({
        'success': True,
        'data': reportes_paginados,
        'pagination': {
            'current_page': page,
            'per_page': per_page,
            'total': total,
            'last_page': (total + per_page - 1) // per_page
        }
    }), 200


@prediccion_ausencias_bp.route('/ver/<tipo>/<nombre>', methods=['GET'])
@jwt_required()
def ver_reporte(tipo, nombre):
    """
    Ver un reporte específico por tipo y nombre
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    # Validar tipo
    if tipo not in ['general', 'individual']:
        return jsonify({
            'success': False,
            'message': 'Tipo de reporte inválido'
        }), 400
    
    # Construir ruta
    base_path = PrediccionAusencias.ML_REPORTS_PATH
    if tipo == 'general':
        ruta = os.path.join(base_path, 'generales', nombre)
    else:
        ruta = os.path.join(base_path, 'individuales', nombre)
    
    # Validar que el archivo existe
    if not os.path.exists(ruta):
        return jsonify({
            'success': False,
            'message': 'Reporte no encontrado'
        }), 404
    
    # Leer contenido
    contenido_result = PrediccionAusencias.leer_reporte_html(ruta)
    
    if not contenido_result['success']:
        return jsonify({
            'success': False,
            'message': contenido_result['message']
        }), 500
    
    # Retornar HTML
    return contenido_result['contenido'], 200, {'Content-Type': 'text/html; charset=utf-8'}


@prediccion_ausencias_bp.route('/descargar/<tipo>/<nombre>', methods=['GET'])
@jwt_required()
def descargar_reporte(tipo, nombre):
    """
    Descargar un reporte específico
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    # Validar tipo
    if tipo not in ['general', 'individual']:
        return jsonify({
            'success': False,
            'message': 'Tipo de reporte inválido'
        }), 400
    
    # Construir ruta
    base_path = PrediccionAusencias.ML_REPORTS_PATH
    if tipo == 'general':
        ruta = os.path.join(base_path, 'generales', nombre)
    else:
        ruta = os.path.join(base_path, 'individuales', nombre)
    
    # Validar que el archivo existe
    if not os.path.exists(ruta):
        return jsonify({
            'success': False,
            'message': 'Reporte no encontrado'
        }), 404
    
    # Enviar archivo
    return send_file(
        ruta,
        as_attachment=True,
        download_name=nombre,
        mimetype='text/html'
    )