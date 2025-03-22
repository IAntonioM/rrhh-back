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
        current_user = get_jwt_identity()
        if not current_user:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        # Obtener datos del cuerpo de la solicitud
        data = request.json or {}
        # Buscar la información del usuario en la base de datos
        filtros = {'username': current_user}
        usuario_current = UsuarioModel.get_usuarios_filter(filtros, current_page=1, per_page=1)
        # Extraer la información estructurada
        plantilla_nombre = data.pop('plantilla', 'default.html')
        params_str = data.pop('params', '')
        version = data.pop('version', 'v1')
        
        # Procesar los parámetros dinámicos (formato: key^value|key2^value2|...)
        parametros = {}
        if params_str:
            param_pairs = params_str.split('|')
            for pair in param_pairs:
                if '^' in pair:
                    key, value = pair.split('^', 1)
                    parametros[key] = value
        
        # Incluir versión en los parámetros
        parametros['version'] = version
        
        # Añadir cualquier parámetro adicional que pudiera venir en el cuerpo del JSON
        parametros.update(data)
                
        # Verificar si la plantilla existe
        if not reporte_service.verificar_plantilla(plantilla_nombre):
            return jsonify({'error': f'Plantilla {plantilla_nombre} no encontrada'}), 404
            
        # Ejecutar el procedimiento almacenado con los parámetros
        datos = reporte_service.ejecutar_procedimiento(parametros)
        
        # Generar el PDF
        output_file, download_name = reporte_service.generar_pdf(
            plantilla_nombre, parametros, datos, usuario_current
        )
        
        # Enviar el archivo PDF al cliente
        return send_file(
            output_file,
            as_attachment=True,
            download_name=download_name
        )
        
    except Exception as e:
        return jsonify({'error': f'Error al procesar la solicitud: {str(e)}'}), 500
    
    
@reporte_blueprint.route('/plantillas', methods=['GET'])
def listar_plantillas():
    plantillas = reporte_service.listar_plantillas()
    return jsonify({'plantillas_disponibles': plantillas})