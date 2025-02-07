import pyodbc
import re
from config import get_db_connection
from ..utils.audit import AuditFields

class MenuModel:
    
    @staticmethod
    def create_menu(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Agregar campos de auditoría al diccionario de datos
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_menu] 
                    @accion = 1,  -- Acción 1 es para crear
                    @nombre = ?, 
                    @url = ?, 
                    @icono = ?, 
                    @padre_id = ?, 
                    @orden = ?, 
                    @estado = ?
            ''', (data['nombre'], data['url'], data.get('icono'), 
                  data.get('padre_id'), data['orden'], data.get('estado')))
            
            conn.commit()
            return True, 'Menú registrado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar el menú'
            
        finally:
            conn.close()

    @staticmethod
    def update_menu(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Agregar campos de auditoría al diccionario de datos
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_menu] 
                    @accion = 2,  -- Acción 2 es para actualizar
                    @id = ?, 
                    @nombre = ?, 
                    @url = ?, 
                    @icono = ?, 
                    @padre_id = ?, 
                    @orden = ?, 
                    @estado = ?
            ''', (data['id'], data['nombre'], data['url'], data.get('icono'), 
                  data.get('padre_id'), data['orden'], data.get('estado')))
            
            conn.commit()
            return True, 'Menú actualizado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar el menú'
            
        finally:
            conn.close()

    @staticmethod
    def get_menus_list():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_menu] 
                    @accion = 3;  -- Acción 3 para listar todos los menús
            ''')  # No es necesario pasar parámetros para esta acción

            menus = cursor.fetchall()

            # Procesar y retornar los resultados en forma de lista de diccionarios
            return [{
                'id': m[0], 
                'nombre': m[1], 
                'url': m[2], 
                'icono': m[3], 
                'padre_id': m[4], 
                'orden': m[5], 
                'estado': m[6], 
                'created_at': m[7], 
                'updated_at': m[8]
            } for m in menus]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de menús'
        
        finally:
            conn.close()
