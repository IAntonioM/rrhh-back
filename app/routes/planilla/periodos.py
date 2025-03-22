from flask import Blueprint, request, jsonify
from config import get_db_connection

periodos_bp = Blueprint('periodos', __name__)

@periodos_bp.route('/', methods=['GET'])
def get_periodos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, anio, mes, fecha_registro FROM Periodos")
    periodos = [dict(id=row[0], anio=row[1], mes=row[2], fecha_registro=row[3]) for row in cursor.fetchall()]
    conn.close()
    return jsonify(periodos)

@periodos_bp.route('/<int:id>', methods=['GET'])
def get_periodo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, anio, mes, fecha_registro FROM Periodos WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify(dict(id=row[0], anio=row[1], mes=row[2], fecha_registro=row[3]))
    return jsonify({'error': 'Periodo no encontrado'}), 404

@periodos_bp.route('/', methods=['POST'])
def create_periodo():
    data = request.get_json()
    anio, mes, fecha_registro = data['anio'], data['mes'], data['fecha_registro']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Periodos (anio, mes, fecha_registro) VALUES (?, ?, ?)", (anio, mes, fecha_registro))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Periodo creado correctamente'}), 201

@periodos_bp.route('/<int:id>', methods=['PUT'])
def update_periodo(id):
    data = request.get_json()
    anio, mes, fecha_registro = data['anio'], data['mes'], data['fecha_registro']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Periodos SET anio=?, mes=?, fecha_registro=? WHERE id=?", (anio, mes, fecha_registro, id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Periodo actualizado correctamente'})

@periodos_bp.route('/<int:id>', methods=['DELETE'])
def delete_periodo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Periodos WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Periodo eliminado correctamente'})
