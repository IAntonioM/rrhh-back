from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.planilla.regimenPensionarioSUNAT import RegimenPensionarioSUNATModel
from ...utils.error_handlers import handle_response
import re

regimen_pensionario_bp = Blueprint('regimen_pensionario_sunat', __name__)

def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@regimen_pensionario_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_regimen_pensionario():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = RegimenPensionarioSUNATModel.create_regimen_pensionario(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@regimen_pensionario_bp.route('/update', methods=['PUT'])
@jwt_required()
@handle_response
def update_regimen_pensionario():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = RegimenPensionarioSUNATModel.update_regimen_pensionario(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@regimen_pensionario_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_regimen_pensionarios():
    filtros = {
        'codigoPDT': request.args.get('codigoPDT') or None,
        'regimenPensionario': request.args.get('regimenPensionario') or None,
        'tipo': request.args.get('tipo') or None,
        'flag_estado': request.args.get('flag_estado') or None
    }
    regimenes_list = RegimenPensionarioSUNATModel.get_regimen_pensionarios_list(filtros)
    return jsonify({
        'success': True,
        'data': regimenes_list
    }), 200
