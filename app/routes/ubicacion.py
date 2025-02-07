from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.ubicacion import UbicacionModel
from ..utils.error_handlers import handle_response
import re

ubicacion_bp = Blueprint('ubicacion', __name__)

def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@ubicacion_bp.route('/departamentos', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_departamentos():
    """
    Listar todos los departamentos
    """
    departamentos = UbicacionModel.list_departamentos()
    return jsonify({
        'success': True,
        'data': departamentos
    }), 200

@ubicacion_bp.route('/provincias', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_provincias_by_departamento():
    """
    Listar provincias por departamento (con idDepartamento)
    """
    idDepartamento = request.args.get('idDepartamento')
    if not idDepartamento:
        return jsonify({'success': False, 'message': 'Falta el parámetro idDepartamento'}), 400

    provincias = UbicacionModel.list_provincias_by_departamento(idDepartamento)
    return jsonify({
        'success': True,
        'data': provincias
    }), 200

@ubicacion_bp.route('/ubigeos', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_ubigeos_by_provincia():
    """
    Listar ubigeos por provincia (con idProvincia)
    """
    idProvincia = request.args.get('idProvincia')
    if not idProvincia:
        return jsonify({'success': False, 'message': 'Falta el parámetro idProvincia'}), 400

    ubigeos = UbicacionModel.list_ubigeos_by_provincia(idProvincia)
    return jsonify({
        'success': True,
        'data': ubigeos
    }), 200
