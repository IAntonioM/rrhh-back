from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models.conceptoPDT import ConceptosPDT
from ..utils.error_handlers import handle_response

conceptos_bp = Blueprint('conceptosPDT', __name__)

@conceptos_bp.route('/list', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def list_conceptos():
    tipo = request.args.get('tipo', None)

    result = ConceptosPDT.list_conceptos(tipo)

    return jsonify({'success': True, 'data': result}), 200
