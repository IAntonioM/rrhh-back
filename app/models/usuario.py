import pyodbc
import re
from config import get_db_connection
from ..utils.auditv2 import AuditFieldsv2
from werkzeug.security import generate_password_hash, check_password_hash
class UsuarioModel:
    
    @staticmethod
    def create_usuario(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir campos de auditoría
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
            data['password'] = generate_password_hash(data['password'])
            cursor = conn.cursor()
            cursor.execute(''' 
                EXEC [Seguridad].[sp_usuarios] 
                    @accion = 1,  -- Acción 1 para insertar un nuevo usuario
                    @username = ?, 
                    @password = ?, 
                    @rol_id = ?, 
                    @estado = ?, 
                    @fecha_registro = ?, 
                    @estacion_registro = ?, 
                    @operador_registro = ?, 
                    @fecha_modificacion = ?, 
                    @estacion_modificacion = ?, 
                    @operador_modificacion = ?, 
                    @idEmpleado = ?
            ''', (
                data['username'], data['password'], data['rol_id'], data['estado'], 
                data['fecha_registro'], data['estacion_registro'], data['operador_registro'], 
                data['fecha_modificacion'], data['estacion_modificacion'], data['operador_modificacion'],
                data['idEmpleado']
            ))

            conn.commit()
            return True, 'Usuario registrado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar usuario'
            
        finally:
            conn.close()

    @staticmethod
    def update_usuario(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir campos de auditoría
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            # Verificar si 'password' existe y no es None antes de encriptarla
            password_hashed = None
            if 'password' in data and data['password']:
                password_hashed = generate_password_hash(data['password'])

            cursor = conn.cursor()
            cursor.execute(''' 
                EXEC [Seguridad].[sp_usuarios] 
                    @accion = 2, 
                    @id = ?, 
                    @username = ?, 
                    @password = ?, 
                    @rol_id = ?, 
                    @estado = ?, 
                    @fecha_registro = ?, 
                    @estacion_registro = ?, 
                    @operador_registro = ?, 
                    @fecha_modificacion = ?, 
                    @estacion_modificacion = ?, 
                    @operador_modificacion = ?, 
                    @idEmpleado = ?
            ''', (
                data.get('id'),
                data.get('username'),
                password_hashed,  # Ahora puede ser None si no se envió
                data.get('rol_id'),
                data.get('estado'),
                data.get('fecha_registro'),
                data.get('estacion_registro'),
                data.get('operador_registro'),
                data.get('fecha_modificacion'),
                data.get('estacion_modificacion'),
                data.get('operador_modificacion'),
                data.get('idEmpleado')
            ))

            conn.commit()
            return True, 'Usuario actualizado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar usuario'

        finally:
            conn.close()

    @staticmethod
    def get_usuarios_filter(filtros, current_page, per_page):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(''' 
                EXEC [Seguridad].[sp_usuarios] 
                    @accion = 3,  -- Acción 3 para listar usuarios con filtros
                    @username = ?, 
                    @nombre_completo = ?, 
                    @estado = ?, 
                    @rol_id = ?, 
                    @current_page = ?, 
                    @per_page = ?
            ''', (
                filtros.get('username', None),
                filtros.get('nombre_completo', None),
                filtros.get('estado', None),
                filtros.get('rol_id', None),
                current_page,
                per_page
            ))

            usuarios = cursor.fetchall()

            # Convertir los resultados a una lista de diccionarios
            return [{
                'id': u[0], 
                'username': u[1], 
                'rol_id': u[2], 
                'estado': u[3], 
                'fecha_registro': u[4],
                'estacion_registro': u[5],
                'operador_registro': u[6],
                'fecha_modificacion': u[7],
                'estacion_modificacion': u[8],
                'operador_modificacion': u[9],
                'idEmpleado': u[10],

                # Paginación
                'current_page': u[11],
                'last_page': u[12],
                'per_page': u[13],
                'total': u[14],
                'area': u[15],
                'rol_nombre': u[16],
                'dni': u[17],
                'nombres': u[18],
            } for u in usuarios]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de usuarios'
            
        finally:
            conn.close()

    @staticmethod
    def change_usuario_status(id, estado, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Generar campos de auditoría
            data = {
                'id': id, 
                'estado': estado, 
                'fecha_modificacion': None, 
                'estacion_modificacion': None, 
                'operador_modificacion': current_user
            }
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute(''' 
                EXEC [Seguridad].[sp_usuarios] 
                    @accion = 4,  -- Acción 4 para cambiar el estado de un usuario
                    @id = ?, 
                    @estado = ?
            ''', (id, estado))

            conn.commit()
            return True, 'Estado del usuario actualizado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al cambiar el estado del usuario'
            
        finally:
            conn.close()

    @staticmethod
    def delete_usuario(id, current_user, remote_addr):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(''' 
                EXEC [Seguridad].[sp_usuarios] 
                    @accion = 5,  -- Acción 5 para eliminar un usuario
                    @id = ?
            ''', (id,))

            conn.commit()
            return True, 'Usuario eliminado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al eliminar usuario'
            
        finally:
            conn.close()

    @staticmethod
    def get_usuarios_list_complete(filtros):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(''' 
                EXEC [Seguridad].[sp_usuarios] 
                    @accion = 6, -- Acción 6 para obtener la lista completa de usuarios
                    @rol_id = ?
            ''', (
                filtros.get('rol_id', None)
            ))

            usuarios = cursor.fetchall()

            # Convertir los resultados a una lista de diccionarios
            return [{
                'id': u[0], 
                'username': u[1], 
                'rol_id': u[2], 
                'estado': u[3], 
                'fecha_registro': u[4],
                'estacion_registro': u[5],
                'operador_registro': u[6],
                'fecha_modificacion': u[7],
                'estacion_modificacion': u[8],
                'operador_modificacion': u[9],
                'idEmpleado': u[10],
            } for u in usuarios]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de usuarios'
            
        finally:
            conn.close()


    @staticmethod
    def get_by_username(username):
        try:
            # Obtiene la conexión a la BD
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Consulta para obtener rol_id
                    query = "SELECT rol_id FROM Seguridad.usuarios WHERE username = ?"
                    cursor.execute(query, (username,))
                    
                    # Obtiene un solo resultado
                    row = cursor.fetchone()

                    # Si se encontró un resultado, devolverlo como diccionario
                    if row:
                        return {"rol_id": row[0]}
                    
                    return None

        except pyodbc.Error as e:
            print(f"Database error: {str(e)}")
            return None
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

