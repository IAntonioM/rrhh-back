import pyodbc
import re
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class AccesoModel:

    @staticmethod
    def create_acceso(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Seguridad].[sp_acceso]
                    @accion = 1, -- Acción 1 para insertar un nuevo acceso
                    @tipo = ?, 
                    @nombre = ?, 
                    @menu_id = ?, 
                    @objeto_id = ?, 
                    @estado = ?, 
                    @fecha_registro = ?, 
                    @estacion_registro = ?, 
                    @operador_registro = ?, 
                    @fecha_modificacion = ?, 
                    @estacion_modificacion = ?, 
                    @operador_modificacion = ?
            ''', (
                data['tipo'], data['nombre'], data['menu_id'], data['objeto_id'], 
                data['estado'], data['fecha_registro'], data['estacion_registro'], 
                data['operador_registro'], data['fecha_modificacion'], 
                data['estacion_modificacion'], data['operador_modificacion']
            ))

            conn.commit()
            return True, 'Acceso registrado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar acceso'

        finally:
            conn.close()

    @staticmethod
    def update_acceso(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Seguridad].[sp_acceso]
                    @accion = 2, -- Acción 2 para actualizar un acceso
                    @id = ?, 
                    @tipo = ?, 
                    @nombre = ?, 
                    @menu_id = ?, 
                    @objeto_id = ?, 
                    @estado = ?, 
                    @fecha_modificacion = ?, 
                    @estacion_modificacion = ?, 
                    @operador_modificacion = ?
            ''', (
                data['id'], data['tipo'], data['nombre'], data['menu_id'], 
                data['objeto_id'], data['estado'], data['fecha_modificacion'], 
                data['estacion_modificacion'], data['operador_modificacion']
            ))

            conn.commit()
            return True, 'Acceso actualizado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar acceso'

        finally:
            conn.close()

    @staticmethod
    def get_accesos_filter(filtros, current_page, per_page):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Seguridad].[sp_acceso] 
                    @accion = 3, -- Acción 3 para listar accesos
                    @nombre = ?, 
                    @objeto_id = ?, 
                    @tipo = ?, 
                    @estado = ?, 
                    @current_page = ?, 
                    @per_page = ?
            ''', (
                filtros.get('nombre', None), 
                filtros.get('objeto_id', None),
                filtros.get('tipo', None), 
                filtros.get('estado', None),
                current_page,
                per_page
            ))

            accesos = cursor.fetchall()

            return [{
                'id': a[0],
                'tipo': a[1],
                'nombre': a[2],
                'menu_id': a[3],
                'objeto_id': a[4],
                'estado': a[5],
                'fecha_registro': a[6],
                'estacion_registro': a[7],
                'operador_registro': a[8],
                'fecha_modificacion': a[9],
                'estacion_modificacion': a[10],
                'operador_modificacion': a[11],
                'current_page': a[12],
                'last_page': a[13],
                'per_page': a[14],
                'total': a[15],
                'menu_nombre': a[16],
            } for a in accesos]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener accesos'

        finally:
            conn.close()

    @staticmethod
    def change_acceso_status(id, estado, current_user, remote_addr):
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
                EXEC [Seguridad].[sp_acceso]
                    @accion = 4, -- Acción 4 para cambiar el estado
                    @id = ?, 
                    @estado = ?
            ''', (id, estado))

            conn.commit()
            return True, 'Estado del acceso actualizado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al cambiar el estado del acceso'

        finally:
            conn.close()

    @staticmethod
    def delete_acceso(id, current_user, remote_addr):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Seguridad].[sp_acceso]
                    @accion = 5, -- Acción 5 para eliminar un acceso
                    @id = ?
            ''', (id,))

            conn.commit()
            return True, 'Acceso eliminado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al eliminar acceso'

        finally:
            conn.close()

    @staticmethod
    def get_active_accesos():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Seguridad].[sp_acceso]
                    @accion = 6 -- Acción 6 para obtener accesos activos
            ''')

            accesos = cursor.fetchall()

            return [{
                'id': a[0],
                'tipo': a[1],
                'nombre': a[2],
                'menu_id': a[3],
                'objeto_id': a[4],
                'estado': a[5],
                'fecha_registro': a[6],
                'estacion_registro': a[7],
                'operador_registro': a[8],
                'fecha_modificacion': a[9],
                'estacion_modificacion': a[10],
                'operador_modificacion': a[11],
            } for a in accesos]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener accesos activos'

        finally:
            conn.close()
    
    @staticmethod
    def get_accesos_por_menu(filtros):
        conn = get_db_connection()  # Suponiendo que tienes esta función para obtener la conexión
        try:
            cursor = conn.cursor()
            # Ejecutamos la consulta con la acción 7 y el parámetro menu_id
            cursor.execute('''
                EXEC [Seguridad].[sp_acceso]
                    @accion = 7, -- Acción 7 para obtener accesos por menu_id
                    @menu_id = ? -- Pasamos el menu_id como parámetro
            ''', (
                filtros.get('menu_id', None), 
            ))

            accesos = cursor.fetchall()

            # Devuelve los accesos con la estructura que necesitas
            return [{
                'id': a[0],
                'tipo': a[1],
                'nombre': a[2],
                'menu_id': a[3],
                'objeto_id': a[4],
                'estado': a[5],
            } for a in accesos]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener accesos por menu_id'

        finally:
            conn.close()
