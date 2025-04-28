from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.controlAsistencias.horarioModel import HorarioModel
from ...utils.error_handlers import handle_response
import re

horario_bp = Blueprint('horario', __name__)

def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@horario_bp.route('/create', methods=['POST'])
@jwt_required()
@handle_response
def create_horario():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    data = request.get_json()
    success, message = HorarioModel.create_horario(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@horario_bp.route('/update', methods=['PUT'])
@jwt_required()
@handle_response
def update_horario():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    success, message = HorarioModel.update_horario(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@horario_bp.route('/delete', methods=['DELETE'])
@jwt_required()
@handle_response
def delete_horario():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    success, message = HorarioModel.delete_horario(data, current_user, request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 409

@horario_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_horario(id):
    horario = HorarioModel.get_horario_by_id(id)
    if not horario:
        return jsonify({
            'success': False,
            'message': 'Horario no encontrado'
        }), 404
    
    return jsonify({
        'success': True,
        'data': horario
    }), 200

@horario_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_horarios():
    horarios_list = HorarioModel.get_horarios_list()
    return jsonify({
        'success': True,
        'data': horarios_list
    }), 200

@horario_bp.route('/combo', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_horarios_combo():
    horarios_combo = HorarioModel.get_horarios_combo()
    return jsonify({
        'success': True,
        'data': horarios_combo
    }), 200