import pyodbc
import re
from config import get_db_connection
from ..utils.auditv2 import AuditFieldsv2

class RolModel:

    @staticmethod
    def create_rol(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Seguridad].[sp_rol]
                    @accion = 1, -- Acción 1 para insertar un nuevo rol
                    @nombre = ?, 
                    @estado = ?, 
                    @fecha_registro = ?, 
                    @estacion_registro = ?, 
                    @operador_registro = ?, 
                    @fecha_modificacion = ?, 
                    @estacion_modificacion = ?, 
                    @operador_modificacion = ?
            ''', (
                data['nombre'], data['estado'], data['fecha_registro'], 
                data['estacion_registro'], data['operador_registro'], 
                data['fecha_modificacion'], data['estacion_modificacion'], 
                data['operador_modificacion']
            ))

            conn.commit()
            return True, 'Rol registrado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar rol'

        finally:
            conn.close()

    @staticmethod
    def update_rol(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Seguridad].[sp_rol]
                    @accion = 2, -- Acción 2 para actualizar un rol
                    @id = ?, 
                    @nombre = ?, 
                    @estado = ?, 
                    @fecha_modificacion = ?, 
                    @estacion_modificacion = ?, 
                    @operador_modificacion = ?
            ''', (
                data['id'], data['nombre'], data['estado'], 
                data['fecha_modificacion'], data['estacion_modificacion'], 
                data['operador_modificacion']
            ))

            conn.commit()
            return True, 'Rol actualizado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar rol'

        finally:
            conn.close()

    @staticmethod
    def get_roles_filter(filtros, current_page, per_page):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Seguridad].[sp_rol] 
                    @accion = 3, -- Acción 3 para listar roles
                    @nombre = ?, 
                    @estado = ?, 
                    @current_page = ?, 
                    @per_page = ?
            ''', (
                filtros.get('nombre', None),
                filtros.get('estado', None),
                current_page,
                per_page
            ))

            roles = cursor.fetchall()

            return [{
                'id': r[0],
                'nombre': r[1],
                'estado': r[2],
                'fecha_registro': r[3],
                'estacion_registro': r[4],
                'operador_registro': r[5],
                'fecha_modificacion': r[6],
                'estacion_modificacion': r[7],
                'operador_modificacion': r[8],
                'current_page': r[9],
                'last_page': r[10],
                'per_page': r[11],
                'total': r[12],
            } for r in roles]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener roles'

        finally:
            conn.close()

    @staticmethod
    def change_rol_status(id, estado, current_user, remote_addr):
        conn = get_db_connection()
        try:
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
                EXEC [Seguridad].[sp_rol]
                    @accion = 4, -- Acción 4 para cambiar el estado
                    @id = ?, 
                    @estado = ?
            ''', (id, estado))

            conn.commit()
            return True, 'Estado del rol actualizado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al cambiar el estado del rol'

        finally:
            conn.close()

    @staticmethod
    def delete_rol(id, current_user, remote_addr):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Seguridad].[sp_rol]
                    @accion = 5, -- Acción 5 para eliminar un rol
                    @id = ?
            ''', (id,))

            conn.commit()
            return True, 'Rol eliminado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al eliminar rol'

        finally:
            conn.close()

    @staticmethod
    def get_active_roles():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Seguridad].[sp_rol]
                    @accion = 6 -- Acción 6 para obtener roles activos
            ''')

            roles = cursor.fetchall()

            return [{
                'id': r[0],
                'nombre': r[1],
                'estado': r[2]
            } for r in roles]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener roles activos'

        finally:
            conn.close()

            
