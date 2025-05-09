from flask import Blueprint, request, jsonify
from ...models.controlAsistencias.marcacionModel import Marcaciones
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

marcaciones_bp = Blueprint('marcaciones', __name__)

@marcaciones_bp.route('/registrar', methods=['POST'])
@jwt_required()
def registrar_marcacion():
    current_user = get_jwt_identity()
    remote_addr = request.remote_addr
    
    data = request.get_json()
    result = Marcaciones.registrar_marcacion(data, current_user, remote_addr)
    
    if result.get('success'):
        return jsonify({'success': True, 'message': result.get('message')}), 201
    return jsonify({'success': False, 'message': result.get('message')}), 400

@marcaciones_bp.route('/listar', methods=['GET'])
@jwt_required()
def listar_marcaciones():
    filtros = {
        'idArea': request.args.get('idArea'),
        'nombres': request.args.get('nombres'),
        'idCargo': request.args.get('idCargo'),
        'dni': request.args.get('dni'),
        'deFecha': request.args.get('deFecha'),
        'hastaFecha': request.args.get('hastaFecha')
    }
    
    # Eliminamos filtros vacíos
    filtros = {k: v for k, v in filtros.items() if v is not None}
    
    result = Marcaciones.listar_marcaciones(filtros)
    return jsonify(result), 200
