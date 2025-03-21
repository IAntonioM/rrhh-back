import pyodbc
import re
from config import get_db_connection
from ..utils.auditv2 import AuditFieldsv2

class MenuModel:
    
    @staticmethod
    def create_menu(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute(''' 
                EXEC [Seguridad].[sp_menu] 
                    @accion = 1,  -- Acción 1 para insertar un nuevo menú
                    @nombre = ?, 
                    @url = ?, 
                    @icono = ?, 
                    @padre_id = ?, 
                    @tipo = ?, 
                    @orden = ?, 
                    @estado = ?, 
                    @fecha_registro = ?, 
                    @estacion_registro = ?, 
                    @operador_registro = ?, 
                    @fecha_modificacion = ?, 
                    @estacion_modificacion = ?, 
                    @operador_modificacion = ?
            ''', (
                data['nombre'], data['url'], data['icono'], data['padre_id'], 
                data['tipo'], data['orden'], data['estado'], 
                data['fecha_registro'], data['estacion_registro'], data['operador_registro'], 
                data['fecha_modificacion'], data['estacion_modificacion'], data['operador_modificacion']
            ))

            conn.commit()
            return True, 'Menú registrado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar menú'
            
        finally:
            conn.close()

    @staticmethod
    def update_menu(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute(''' 
                EXEC [Seguridad].[sp_menu] 
                    @accion = 2,  -- Acción 2 para actualizar un menú
                    @id = ?, 
                    @nombre = ?, 
                    @url = ?, 
                    @icono = ?, 
                    @padre_id = ?, 
                    @tipo = ?, 
                    @orden = ?, 
                    @estado = ?, 
                    @fecha_registro = ?, 
                    @estacion_registro = ?, 
                    @operador_registro = ?, 
                    @fecha_modificacion = ?, 
                    @estacion_modificacion = ?, 
                    @operador_modificacion = ?
            ''', (
                data['id'], data['nombre'], data['url'], data['icono'], data['padre_id'], 
                data['tipo'], data['orden'], data['estado'], 
                data['fecha_registro'], data['estacion_registro'], data['operador_registro'], 
                data['fecha_modificacion'], data['estacion_modificacion'], data['operador_modificacion']
            ))

            conn.commit()
            return True, 'Menú actualizado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar menú'
            
        finally:
            conn.close()

    @staticmethod
    def get_menus_filter(filtros, current_page, per_page):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Seguridad].[sp_menu] 
                    @accion = 3, 
                    @nombre = ?, 
                    @url = ?, 
                    @tipo = ?, 
                    @estado = ?, 
                    @current_page = ?, 
                    @per_page = ?
            ''', (
                filtros.get('nombre', None),
                filtros.get('url', None),
                filtros.get('tipo', None),
                filtros.get('estado', None),
                current_page,
                per_page
            ))

            menus = cursor.fetchall()

            # Convert the results into a list of dictionaries
            return [{
                'id': m[0], 
                'nombre': m[1], 
                'url': m[2], 
                'icono': m[3], 
                'padre_id': m[4], 
                'tipo': m[5], 
                'orden': m[6], 
                'estado': m[7], 
                'fecha_registro': m[8],
                'estacion_registro': m[9],
                'operador_registro': m[10],
                'fecha_modificacion': m[11],
                'estacion_modificacion': m[12],
                'operador_modificacion': m[13],

                # Pagination info
                'current_page': m[14], 
                'last_page': m[15], 
                'per_page': m[16], 
                'total': m[17],
                'menu_padre_nombre': m[18],
            } for m in menus]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de menús'
            
        finally:
            conn.close()


    @staticmethod
    def change_menu_status(id, estado, current_user, remote_addr):
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
                EXEC [Seguridad].[sp_menu] 
                    @accion = 4,  -- Acción 4 para cambiar el estado
                    @id = ?, 
                    @estado = ? 
            ''', (id, estado))

            conn.commit()
            return True, 'Estado del menú actualizado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al cambiar el estado del menú'
            
        finally:
            conn.close()

    @staticmethod
    def delete_menu(id, current_user, remote_addr):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(''' 
                EXEC [Seguridad].[sp_menu] 
                    @accion = 5,  -- Acción 5 para eliminar un menú
                    @id = ?
            ''', (id,))

            conn.commit()
            return True, 'Menú eliminado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al eliminar menú'
            
        finally:
            conn.close()



    @staticmethod
    def get_menus_list_complete(filtros):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Seguridad].[sp_menu] 
                    @accion = 6,
                    @padre_id = ?
            ''', (
                filtros.get('padre_id', None)
            ))

            menus = cursor.fetchall()

            # Convert the results into a list of dictionaries
            return [{
                'id': m[0], 
                'nombre': m[1], 
                'url': m[2], 
                'icono': m[3], 
                'padre_id': m[4], 
                'tipo': m[5], 
                'orden': m[6], 
                'estado': m[7], 
                'fecha_registro': m[8],
                'estacion_registro': m[9],
                'operador_registro': m[10],
                'fecha_modificacion': m[11],
                'estacion_modificacion': m[12],
                'operador_modificacion': m[13],

                # Pagination info
                'current_page': m[14], 
                'last_page': m[15], 
                'per_page': m[16], 
                'total': m[17]
            } for m in menus]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de menús'
            
        finally:
            conn.close()