# controllers/reporte_controller.py
from flask import Blueprint, request, send_file, jsonify
from app.services.reporte import ReporteService
from ...models.seguridad.usuario import UsuarioModel
from flask_jwt_extended import jwt_required, get_jwt_identity

reporte_blueprint = Blueprint('reporte', __name__)
reporte_service = ReporteService()

@reporte_blueprint.route('', methods=['POST'])
@jwt_required()
def generar_reporte():
    try:
        # Obtener usuario actual
        current_user = get_jwt_identity()
        if not current_user:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

        # Obtener datos de la solicitud
        data = request.json or {}
        
        # Configuraciones básicas
        plantilla_nombre = data.pop('plantilla', 'default.html')
        params_str = data.pop('params', '')
        version = data.pop('version', 'v1')
        tipo_reporte = data.pop('tipo', 'pdf')
        custom_title = data.pop('custom_title', 'sin_definir')
        
        # Nuevos parámetros para manejo de múltiples tablas
        usar_legacy = data.pop('usar_legacy', False)  # Para compatibilidad hacia atrás
        tabla_especifica = data.pop('tabla_especifica', None)  # Para usar una tabla específica

        # Procesar parámetros dinámicos
        parametros = {}
        if params_str:
            param_pairs = params_str.split('|')
            for pair in param_pairs:
                if '^' in pair:
                    key, value = pair.split('^', 1)
                    parametros[key] = value

        # Incluir versión y datos adicionales
        parametros['version'] = version
        parametros.update(data)

        # Buscar información del usuario
        filtros = {'username': current_user}
        usuario_current = UsuarioModel.get_usuarios_filter(filtros, current_page=1, per_page=1)

        # Verificar existencia de la plantilla según el tipo de reporte
        if tipo_reporte == 'pdf':
            if not reporte_service.verificar_plantilla(plantilla_nombre):
                return jsonify({'error': f'Plantilla PDF {plantilla_nombre} no encontrada'}), 404
            
            # Ejecutar procedimiento y obtener datos
            if usar_legacy:
                datos = reporte_service.ejecutar_procedimiento_legacy(parametros, plantilla_nombre)
            else:
                datos = reporte_service.ejecutar_procedimiento(parametros, plantilla_nombre)
                
                # Si se especifica una tabla específica, extraer solo esa tabla
                if tabla_especifica is not None and isinstance(datos, list) and len(datos) > tabla_especifica:
                    datos = datos[tabla_especifica]['data']
            
            # Generar PDF
            output_file, download_name = reporte_service.generar_pdf(
                plantilla_nombre, parametros, datos, usuario_current
            )
            content_type = 'application/pdf'
            
        elif tipo_reporte == 'excel':
            if not reporte_service.verificar_plantilla_excel(plantilla_nombre):
                return jsonify({'error': f'Plantilla Excel {plantilla_nombre} no encontrada'}), 404
            
            # Generar Excel (ya maneja múltiples tablas internamente)
            output_file, download_name = reporte_service.generar_excel(
                plantilla_nombre,
                parametros,
                usuario_current,
                custom_title
            )
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            return jsonify({'error': 'Tipo de reporte no soportado'}), 400

        # Enviar archivo generado
        return send_file(
            output_file,
            as_attachment=True,
            download_name=download_name,
            mimetype=content_type
        )

    except Exception as e:
        return jsonify({'error': f'Error al procesar solicitud: {str(e)}'}), 500

@reporte_blueprint.route('/info', methods=['POST'])
@jwt_required()
def obtener_info_reporte():
    """
    Endpoint para obtener información sobre las tablas que devuelve un procedimiento
    sin generar el reporte completo
    """
    try:
        current_user = get_jwt_identity()
        if not current_user:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

        data = request.json or {}
        plantilla_nombre = data.pop('plantilla', 'default.html')
        params_str = data.pop('params', '')
        version = data.pop('version', 'v1')

        # Procesar parámetros dinámicos
        parametros = {}
        if params_str:
            param_pairs = params_str.split('|')
            for pair in param_pairs:
                if '^' in pair:
                    key, value = pair.split('^', 1)
                    parametros[key] = value

        parametros['version'] = version
        parametros.update(data)

        # Ejecutar procedimiento para obtener estructura
        datos = reporte_service.ejecutar_procedimiento(parametros, plantilla_nombre)
        
        # Preparar información resumida
        info_tablas = []
        for tabla in datos:
            info_tablas.append({
                'table_index': tabla['table_index'],
                'table_name': tabla['table_name'],
                'columns': tabla['columns'],
                'row_count': tabla['row_count'],
                'sample_data': tabla['data'][:3] if tabla['data'] else []  # Primeras 3 filas como muestra
            })

        return jsonify({
            'success': True,
            'total_tables': len(datos),
            'tables_info': info_tablas
        })

    except Exception as e:
        return jsonify({'error': f'Error al obtener información: {str(e)}'}), 500

@reporte_blueprint.route('/plantillas', methods=['GET'])
def listar_plantillas():
    try:
        plantillas_pdf = reporte_service.listar_plantillas()
        plantillas_excel = reporte_service.listar_plantillas_excel()
        
        return jsonify({
            'plantillas_pdf': plantillas_pdf,
            'plantillas_excel': plantillas_excel
        })
    except Exception as e:
        return jsonify({'error': f'Error al listar plantillas: {str(e)}'}), 500

@reporte_blueprint.route('/test-procedure', methods=['POST'])
@jwt_required()
def test_procedure():
    """
    Endpoint para probar procedimientos almacenados y ver qué tablas devuelven
    """
    try:
        data = request.json or {}
        plantilla_nombre = data.get('plantilla', 'default.html')
        params_str = data.get('params', '')
        
        # Procesar parámetros
        parametros = {}
        if params_str:
            param_pairs = params_str.split('|')
            for pair in param_pairs:
                if '^' in pair:
                    key, value = pair.split('^', 1)
                    parametros[key] = value
        
        # Ejecutar procedimiento
        datos = reporte_service.ejecutar_procedimiento(parametros, plantilla_nombre)
        
        # Devolver estructura detallada
        return jsonify({
            'success': True,
            'total_tables': len(datos),
            'tables_detail': datos
        })
        
    except Exception as e:
        return jsonify({'error': f'Error en test: {str(e)}'}), 500