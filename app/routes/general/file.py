from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from flask import send_file

file_bp = Blueprint('file_upload', __name__)

# Lista de directorios permitidos para guardar archivos
ALLOWED_FILE_TYPES = ['cv', 'perfil_img']

# Extensiones permitidas por tipo
ALLOWED_EXTENSIONS = {
    'cv': ['.pdf', '.docx'],
    'perfil_img': ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.svg', '.jfif', '.pjpeg', '.pjp', '.avif']
}

# Función para verificar si el archivo tiene una extensión permitida
def allowed_file(filename, file_type):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS.get(file_type, [])

# Función para guardar los archivos
def save_file(file, file_type):
    # Validar que el tipo de archivo esté en los tipos permitidos
    if file_type not in ALLOWED_FILE_TYPES:
        raise ValueError("Tipo de archivo no permitido")

    # Validar la extensión del archivo según su tipo
    if not allowed_file(file.filename, file_type):
        raise ValueError(f"Extensión de archivo no permitida para el tipo '{file_type}'")

    # Definir la carpeta de almacenamiento según el tipo de archivo
    upload_folder = os.path.join('app', 'storage', file_type)
    os.makedirs(upload_folder, exist_ok=True)

    # Crear un nombre único para el archivo
    filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
    secure_filename_result = secure_filename(filename)
    filepath = os.path.join(upload_folder, secure_filename_result)
    
    # Guardar el archivo en el sistema
    file.save(filepath)

    # Retornar la ruta del archivo guardado
    return os.path.join('app', 'storage', file_type, secure_filename_result)

@file_bp.route('/upload', methods=['POST'])
def upload_file():
    # Verificar si el archivo está presente en la solicitud
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No se proporcionó un archivo'}), 400

    file = request.files['file']
    
    # Obtener el tipo de archivo desde los parámetros de la solicitud
    file_type = request.form.get('type', '')  # Si no se especifica, es vacío
    
    if not file_type:
        return jsonify({'success': False, 'message': 'Debe especificar un tipo de archivo'}), 400
    
    # Validar que el tipo de archivo esté en la lista permitida
    if file_type not in ALLOWED_FILE_TYPES:
        return jsonify({'success': False, 'message': f'>{file_type}< Tipo de archivo no permitido'}), 400

    try:
        # Guardar el archivo según su tipo
        file_path = save_file(file, file_type)
        
        # Obtener la ruta relativa desde la carpeta donde guardas los archivos
        base_path = 'app\\storage'  # Asegúrate de que sea la ruta base correcta
        relative_path = file_path.replace(base_path, '')  # Reemplazar la parte base de la ruta

        return jsonify({
            'success': True,
            'message': 'Archivo subido exitosamente',
            'path': relative_path  # Aquí devolvemos la ruta relativa
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cargar el archivo: {str(e)}'
        }), 500


# Ruta para mostrar el archivo
@file_bp.route('/<file_type>/<path:filename>', methods=['GET'])
def mostrar_archivo(file_type, filename):
    if file_type not in ['cv', 'perfil_img']:
        return jsonify({'error': 'Tipo de archivo no válido'}), 400
    upload_folder = os.path.join('app', 'storage', file_type)
    filepath = os.path.join(upload_folder, filename)
    if os.path.exists(filepath):
        if file_type == 'cv':
            mimetype = 'application/pdf'  # PDF para CVs
        elif file_type == 'perfil_img':
            ext = os.path.splitext(filename)[1].lower()
            if ext in ['.jpg', '.jpeg']:
                mimetype = 'image/jpeg'
            elif ext == '.png':
                mimetype = 'image/png'
            else:
                mimetype = 'application/octet-stream'  # Default para imágenes no soportadas
        
        return send_file(filepath, mimetype=mimetype)
    else:
        return jsonify({'error': 'Archivo no encontrado'}), 404