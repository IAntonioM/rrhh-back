import pyodbc
import re
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class RolMenuAccesoModel:

    @staticmethod
    def save_rol_menu_acceso(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Agregar campos de auditoría
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()

            # Imprimir valores para debug (en un entorno de producción estos deben ser eliminados o gestionados adecuadamente)
            print(data['rol_id'])
            print(data['menu_id'])
            print(data['accesoIdList'])  # Lista de accesos en formato CSV (ej. '1,2,3')

            # Acción 1: Guardar (insertar nuevos accesos para un rol y menú)
            cursor.execute('''
            EXEC [Accesos].[sp_rol_menu_acceso]
                @accion = 1,
                @rol_id = ?,
                @menu_id = ?,
                @accesoIdList = ?,
                @fecha_registro = ?,
                @estacion_registro = ?,
                @operador_registro = ?
            ''', (
                data['rol_id'],
                data['menu_id'],  # Asegurándote de que se pase un solo menú_id
                data['accesoIdList'],  # Lista de acceso_id (como una cadena separada por comas)
                data['fecha_registro'],
                data['estacion_registro'],
                data['operador_registro']
            ))

            conn.commit()
            return True, 'Acceso guardado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error en la operación'

        finally:
            conn.close()

    @staticmethod
    def get_rol_menu_acceso(rol_id, menu_id=None):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Accesos].[sp_rol_menu_acceso] 
                    @accion = 2,  -- Acción 2 para consultar accesos
                    @rol_id = ?,
                    @menu_id = ?
            ''', (rol_id, menu_id))

            # Obtener los resultados de la consulta
            accesos = cursor.fetchall()

            # Convertir los resultados a una lista de diccionarios
            return [{
                'id': acceso[0], 
                'rol_id': acceso[1], 
                'menu_id': acceso[2], 
                'acceso_id': acceso[3]
            } for acceso in accesos]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener el acceso'

        finally:
            conn.close()
