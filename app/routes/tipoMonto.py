from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models.tipoMonto import TipoMonto
from ..utils.error_handlers import handle_response

tipoMonto_bp = Blueprint('tipoMonto', __name__)

@tipoMonto_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def list_tipoMonto():

    result = TipoMonto.list_tipoMonto()

    return jsonify({'success': True, 'data': result}), 200
