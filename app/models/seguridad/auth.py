from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pyodbc
import re
from config import get_db_connection
from ...utils.audit import AuditFields

class UserModel:
    @staticmethod
    def create_user(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            data['password'] = generate_password_hash(data['password'])
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)
            
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_usuarios] 
                    @accion = 1,
                    @username = ?,
                    @password = ?,
                    @rol_id = ?,
                    @estado = ?,
                    @fecha_reg = ?,
                    @operador_reg = ?,
                    @estacion_reg = ?,
                    @fecha_act = ?,
                    @operador_act = ?,
                    @estacion_act = ?
            ''', (data['username'], data['password'], data.get('rol_id', 1), 
                  data.get('estado', 1), data['fecha_reg'], data['operador_reg'],
                  data['estacion_reg'], data['fecha_act'], data['operador_act'],
                  data['estacion_act']))
            
            conn.commit()
            return True, 'Usuario registrado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar usuario'
            
        finally:
            conn.close()

    @staticmethod
    def authenticate(username, password):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Seguridad].[sp_usuarios] 
                    @accion = 6,
                    @username = ?
            ''', (username,))
            user = cursor.fetchone()
            
            if not user or not check_password_hash(user[1], password):
                return None
            return user[0]  # Return user ID
            
        finally:
            conn.close()

    @staticmethod
    def get_users_list(username_filter, current_page, per_page):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_usuarios] 
                    @accion = 3,
                    @username = ?,
                    @current_page = ?,
                    @per_page = ?
            ''', (username_filter, current_page, per_page))
            
            users = cursor.fetchall()
            return [{
                'id': u[0], 'username': u[1], 'rol_id': u[2], 'estado': u[3],
                'fecha_reg': u[4], 'operador_reg': u[5], 'estacion_reg': u[6],
                'fecha_act': u[7], 'operador_act': u[8], 'estacion_act': u[9],
                'current_page': u[10], 'last_page': u[11], 'per_page': u[12], 'total': u[13],
            } for u in users]
            
        finally:
            conn.close()

    @staticmethod
    def authenticate_by_id(user_id, password):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_usuarios] 
                    @accion = 4,
                    @id = ?
            ''', (user_id,))
            user = cursor.fetchone()
            
            if not user or not check_password_hash(user[1], password):
                return None
            
            # Devolver todos los datos del usuario
            return {
                'id': user[0],
                'username': user[1],
                'rol_id': user[2],
                'estado': user[3],
                'fecha_reg': user[4],
                'operador_reg': user[5],
                'estacion_reg': user[6],
                'fecha_act': user[7],
                'operador_act': user[8],
                'estacion_act': user[9],
                'IdPersonal': user[10]  # Suponiendo que el IdPersonal está en la columna 10
            }
            
        finally:
            conn.close()

    @staticmethod
    def get_user_by_id(user):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_usuarios] 
                    @accion = 5,
                    @username = ?
            ''', (user,))
            user = cursor.fetchone()
            
            # Si no se encuentra el usuario
            if not user:
                return None
            
            # Devolver todos los datos del usuario como un diccionario
            return {
                'id': user[0],
                'username': user[1],
                'rol_id': user[2],
                'estado': user[3],
                'idEmpleado': user[4],
                'idCentroCosto': user[5] # IdPersonal está en el índice 10 (columna 11)
            }
            
        finally:
            conn.close()
