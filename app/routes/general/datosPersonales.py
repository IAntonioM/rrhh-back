from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.general.datosPersonales import DatosPersonales
from ...utils.error_handlers import handle_response
from ...routes.general.file import save_file

datos_personales_bp = Blueprint('datos_personales', __name__)

@datos_personales_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_datos_personales():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    # Obtener los datos JSON
    data = request.form.get('data')
    if not data:
        return jsonify({'success': False, 'message': 'No se proporcionaron datos de usuario'}), 400
    
    # Convertir JSON string a diccionario
    import json
    try:
        data = json.loads(data)
    except:
        return jsonify({'success': False, 'message': 'Formato de datos inválido'}), 400

    # Validar campos requeridos
    required_fields = [
        'apellido_paterno', 'apellido_materno', 'nombres', 
        'idSexo', 'fecha_nacimiento', 'idEstadoCivil',
        'dni', 'idDistrito', 'direccion', 'email'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Campo requerido: {field}'}), 400

    # Procesar archivos si están en la solicitud
    if 'foto' in request.files:
        file = request.files['foto']
        if file.filename:
            try:
                file_path = save_file(file, 'perfil_img')
                data['foto'] = file_path
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error al subir la foto: {str(e)}'}), 400
    
    if 'cv' in request.files:
        file = request.files['cv']
        if file.filename:
            try:
                file_path = save_file(file, 'cv')
                data['cv'] = file_path
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error al subir el CV: {str(e)}'}), 400

    success, message = DatosPersonales.create_datos_personales(data, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 201 if success else 409

@datos_personales_bp.route('/update/<int:idDatosPersonales>', methods=['PUT'])
@jwt_required()
@handle_response
def update_datos_personales(idDatosPersonales):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    # Obtener los datos JSON
    data = request.form.get('data')
    if not data:
        return jsonify({'success': False, 'message': 'No se proporcionaron datos de usuario'}), 400
    
    # Convertir JSON string a diccionario
    import json
    try:
        data = json.loads(data)
    except:
        return jsonify({'success': False, 'message': 'Formato de datos inválido'}), 400

    data['idDatosPersonales'] = idDatosPersonales

    # Procesar archivos si están en la solicitud
    if 'foto' in request.files:
        file = request.files['foto']
        if file.filename:
            try:
                file_path = save_file(file, 'perfil_img')
                data['foto'] = file_path
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error al subir la foto: {str(e)}'}), 400
    
    if 'cv' in request.files:
        file = request.files['cv']
        if file.filename:
            try:
                file_path = save_file(file, 'cv')
                data['cv'] = file_path
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error al subir el CV: {str(e)}'}), 400

    success, message = DatosPersonales.update_datos_personales(data, current_user, request.remote_addr)
    return jsonify({'success': success, 'message': message}), 200 if success else 409

@datos_personales_bp.route('/status/<int:idDatosPersonales>', methods=['PUT'])
@jwt_required()
@handle_response
def delete_datos_personales(idDatosPersonales):
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    success, message = DatosPersonales.delete_datos_personales(idDatosPersonales)
    return jsonify({'success': success, 'message': message}), 200 if success else 409

@datos_personales_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def list_datos_personales():
    # Solo permitir los filtros válidos
    valid_filters = [
        'idDatosPersonales', 'apellido_paterno', 'apellido_materno', 
        'nombres', 'idSexo', 'idEstadoCivil', 'dni', 
        'idDistrito', 'flag_terceros'
    ]
    filtros = {k: v for k, v in request.args.items() if k in valid_filters}
    
    result = DatosPersonales.list_datos_personales(filtros)
    
    if isinstance(result, dict):
        return jsonify({
            'success': True,
            'data': result['data']
        }), 200
    else:
        success, message = result
        return jsonify({'success': success, 'message': message}), 409