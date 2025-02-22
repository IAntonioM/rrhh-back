import pyodbc
import re
from config import get_db_connection
from ..utils.auditv2 import AuditFieldsv2
class RolMenuModel:

    @staticmethod
    def save_rol_menu(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Agregar campos de auditoría
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            print(data['rol_id'])
            print(data['menuIdList'])
            # Acción 1: Guardar (insertar un nuevo acceso)
            cursor.execute('''
            EXEC [Accesos].[sp_rol_menu]
                @accion = 1,
                @rol_id = ?,
                @menuIdList = ?,
                @fecha_registro = ?,
                @estacion_registro = ?,
                @operador_registro = ?
        ''', (
            data['rol_id'],
            data['menuIdList'],
            data['fecha_registro'],
            data['estacion_registro'],
            data['operador_registro']
        ))


            conn.commit()
            return True, 'Acceso guardado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else matches

        finally:
            conn.close()

    @staticmethod
    def get_rol_menu(rol_id):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Accesos].[sp_rol_menu] 
                    @accion = 2,  -- Acción 2 para consultar accesos
                    @rol_id = ?
            ''', (rol_id))

            # Obtener los resultados de la consulta
            accesos = cursor.fetchall()

            # Convertir los resultados a una lista de diccionarios
            return [{
                'id': acceso[0], 
                'rol_id': acceso[1], 
                'menu_id': acceso[2]
            } for acceso in accesos]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener el acceso'

        finally:
            conn.close()

