from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ...models.seguridad.auth import UserModel
from ...utils.error_handlers import handle_response
import re
import pyodbc

auth_bp = Blueprint('auth', __name__)

def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'

@auth_bp.route('/register', methods=['POST'])
@handle_response
def register():
    #current_user = get_jwt_identity()
    #if not current_user:
     #   return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
    data = request.get_json()
    success, message = UserModel.create_user(data, "DBA", request.remote_addr)
    return jsonify({
        'success': success,
        'message': message
    }), 201 if success else 409

@auth_bp.route('/login', methods=['POST'])
@handle_response
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({
            'success': False,
            'message': 'Credenciales incompletas'
        }), 400

    user_id = UserModel.authenticate(username, password)
    if not user_id:
        return jsonify({
            'success': False,
            'message': 'Credenciales inválidas'
        }), 401

    access_token = create_access_token(identity=user_id)
    return jsonify({
        'success': True,
        'message': 'Inicio de sesión exitoso',
        'access_token': access_token
    }), 200

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
@handle_response(include_data=True)
def get_users():
    username_filter = request.args.get('username', None)
    current_page = int(request.args.get('current_page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    users_list = UserModel.get_users_list(username_filter, current_page, per_page)
    return jsonify({
        'success': True,
        'data': users_list
    }), 200

@auth_bp.route('/user', methods=['GET'])
@jwt_required()  # Requiere que el JWT esté presente y sea válido
@handle_response(include_data=True)  # Este decorador lo usas para manejar la respuesta, si es necesario
def get_user():
    # Obtener el ID del usuario desde el JWT
    user = get_jwt_identity()  # Esto te da el `user_id` de quien hizo la solicitud
    print(user)
    # Usamos la función get_user_by_id para obtener los datos del usuario con el ID
    user_data = UserModel.get_user_by_id(user)
    
    # Si no se encuentra el usuario, devolvemos un error 404
    if not user_data:
        return jsonify({
            'success': False,
            'message': 'Usuario no encontrado.'
        }), 404
    
    # Devolver los datos del usuario como respuesta
    return jsonify({
        'success': True,
        'data': user_data
    }), 200



# from flask import Blueprint, request, jsonify
# from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
# from werkzeug.security import generate_password_hash, check_password_hash
# from config import get_db_connection
# from datetime import datetime
# import pyodbc
# import re

# auth_bp = Blueprint('auth', __name__)
# @auth_bp.route('/register', methods=['POST'])
# def register():
#     try:
#         # Get current user (adapt to your auth system)
#         # current_user = get_jwt_identity()
#         # if not current_user:
#         #     return jsonify({
#         #         'success': False,
#         #         'message': 'Usuario no encontrado'
#         #     }), 404

#         data = request.get_json()
#         getDate = datetime.utcnow()
        
#         # Add audit fields
#         data['operador_reg'] = "current_user"
#         data['estacion_reg'] = request.remote_addr
#         data['fecha_reg'] = getDate
#         data['operador_act'] = "current_user"
#         data['estacion_act'] = request.remote_addr
#         data['fecha_act'] = getDate

#         # Hash password
#         data['password'] = generate_password_hash(data['password'])

#         try:
#             conn = get_db_connection()
#             cursor = conn.cursor()
            
#             cursor.execute('''
#                 EXEC [dbo].[sp_usuarios] 
#                     @accion = 1,
#                     @username = ?,
#                     @password = ?,
#                     @rol_id = ?,
#                     @estado = ?,
#                     @fecha_reg = ?,
#                     @operador_reg = ?,
#                     @estacion_reg = ?,
#                     @fecha_act = ?,
#                     @operador_act = ?,
#                     @estacion_act = ?
#             ''', (data['username'], data['password'], data.get('rol_id', 1), 
#                   data.get('estado', 1), data['fecha_reg'], data['operador_reg'],
#                   data['estacion_reg'], data['fecha_act'], data['operador_act'],
#                   data['estacion_act']))
            
#             conn.commit()
#             return jsonify({
#                 'success': True,
#                 'message': 'Usuario registrado con éxito'
#             }), 201

#         except pyodbc.ProgrammingError as e:
#             error_msg = str(e)
#             # Extract clean message from SQL Server error
#             matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
#             clean_message = matches.group(1).strip() if matches else 'Error al registrar usuario'
            
#             return jsonify({
#                 'success': False,
#                 'message': clean_message
#             }), 409

#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': f'Error al procesar la solicitud: {str(e)}'
#         }), 500

#     finally:
#         if 'conn' in locals():
#             conn.close()


# @auth_bp.route('/login', methods=['POST'])
# def login():
#     try:
#         data = request.get_json()
#         username = data.get('username')
#         password = data.get('password')

#         if not username or not password:
#             return jsonify({
#                 'success': False,
#                 'message': 'Credenciales incompletas'
#             }), 400

#         try:
#             conn = get_db_connection()
#             cursor = conn.cursor()

#             cursor.execute('''
#                 EXEC [dbo].[sp_usuarios] 
#                     @accion = 4,
#                     @username = ?
#             ''', (username,))
#             user = cursor.fetchone()

#             if not user or not check_password_hash(user[1], password):
#                 return jsonify({
#                     'success': False,
#                     'message': 'Credenciales inválidas'
#                 }), 401

#             access_token = create_access_token(identity=user[0])
            
#             return jsonify({
#                 'success': True,
#                 'message': 'Inicio de sesión exitoso',
#                 'access_token': access_token
#             }), 200

#         except pyodbc.ProgrammingError as e:
#             error_msg = str(e)
#             matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
#             clean_message = matches.group(1).strip() if matches else 'Error al iniciar sesión'
            
#             return jsonify({
#                 'success': False,
#                 'message': clean_message
#             }), 409

#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': f'Error en el servidor: {str(e)}'
#         }), 500

#     finally:
#         if 'conn' in locals():
#             conn.close()

# @auth_bp.route('/users', methods=['GET'])
# @jwt_required()
# def get_users():
#     try:
#         username_filter = request.args.get('username', None)
#         current_page = int(request.args.get('current_page', 1))
#         per_page = int(request.args.get('per_page', 10))

#         try:
#             conn = get_db_connection()
#             cursor = conn.cursor()

#             cursor.execute('''
#                 EXEC [dbo].[sp_usuarios] 
#                     @accion = 3,
#                     @username = ?,
#                     @current_page = ?,
#                     @per_page = ?
#             ''', (username_filter, current_page, per_page))

#             users = cursor.fetchall()
#             users_list = [{
#                 'id': u[0], 'username': u[1], 'rol_id': u[2], 'estado': u[3],
#                 'fecha_reg': u[4], 'operador_reg': u[5], 'estacion_reg': u[6],
#                 'fecha_act': u[7], 'operador_act': u[8], 'estacion_act': u[9],
#                 'current_page': u[10], 'last_page': u[11], 'per_page': u[12], 'total': u[13],
#             } for u in users]

#             return jsonify({
#                 'success': True,
#                 'data': users_list
#             }), 200

#         except pyodbc.ProgrammingError as e:
#             error_msg = str(e)
#             matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
#             clean_message = matches.group(1).strip() if matches else 'Error al obtener usuarios'
            
#             return jsonify({
#                 'success': False,
#                 'data': [],
#                 'message': clean_message
#             }), 409

#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'data': [],
#             'message': f'Error en el servidor: {str(e)}'
#         }), 500

#     finally:
#         if 'conn' in locals():
#             conn.close()
