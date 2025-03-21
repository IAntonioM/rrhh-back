from flask import Blueprint, request, jsonify
from config import get_db_connection

reporte_bp = Blueprint('reporte', __name__)

@reporte_bp.route('/', methods=['GET'])
def get_periodos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, anio, mes, fecha_registro FROM Periodos")
    periodos = [dict(id=row[0], anio=row[1], mes=row[2], fecha_registro=row[3]) for row in cursor.fetchall()]
    conn.close()
    return jsonify(periodos)
