# controllers/reporte_controller.py
from flask import Blueprint, request, send_file, jsonify
from app.services.reporte  import ReporteService
from ...models.seguridad.usuario  import UsuarioModel
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
        tipo_reporte = data.pop('tipo', 'pdf')  # Nuevo parámetro para seleccionar tipo de reporte
        custom_title = data.pop('custom_title', 'sin_definir')  # Nuevo parámetro para seleccionar tipo de reporte

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
            
            # Generar PDF
            datos = reporte_service.ejecutar_procedimiento(parametros, plantilla_nombre)
            output_file, download_name = reporte_service.generar_pdf(
                plantilla_nombre, parametros, datos, usuario_current
            )
        
        elif tipo_reporte == 'excel':
            if not reporte_service.verificar_plantilla_excel(plantilla_nombre):
                return jsonify({'error': f'Plantilla Excel {plantilla_nombre} no encontrada'}), 404
            
            # Generar Excel
            output_file, download_name = reporte_service.generar_excel(
                plantilla_nombre, 
                parametros, 
                usuario_current,
                custom_title
            )
        
        else:
            return jsonify({'error': 'Tipo de reporte no soportado'}), 400

        # Enviar archivo generado
        return send_file(
            output_file,
            as_attachment=True,
            download_name=download_name
        )

    except Exception as e:
        return jsonify({'error': f'Error al procesar solicitud: {str(e)}'}), 500
    
    
@reporte_blueprint.route('/plantillas', methods=['GET'])
def listar_plantillas():
    plantillas = reporte_service.listar_plantillas()
    return jsonify({'plantillas_disponibles': plantillas})