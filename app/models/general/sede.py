import pyodbc
import re
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2


class SedeModel:

    @staticmethod
    def create_sede(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir campos de auditoría
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblSede] 
                    @accion = 2,
                    @sede = ?,
                    @flag_estado = ?
            ''', (data['sede'], data['flag_estado']))

            conn.commit()
            return True, 'Sede registrada con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar sede'

        finally:
            conn.close()

    @staticmethod
    def update_sede(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir campos de auditoría
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblSede] 
                    @accion = 3,
                    @idSede_update = ?,
                    @sede = ?,
                    @flag_estado = ?
            ''', (data['idSede_update'], data['sede'], data['flag_estado']))

            conn.commit()
            return True, 'Sede actualizada con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar sede'

        finally:
            conn.close()

    @staticmethod
    def get_sedes_list(filtros=None):
        conn = get_db_connection()
        try:
            # Definir los valores de los filtros por defecto (si no se pasan)
            flag_estado = filtros.get('flag_estado', None) if filtros else None

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblSede] 
                    @accion = 4,
                    @flag_estado = ?
            ''', (flag_estado,))

            sedes = cursor.fetchall()

            # Procesar y retornar los resultados en forma de lista de diccionarios
            return [{
                'idSede': s[0],
                'sede': s[1],
                'flag_estado': s[2]
            } for s in sedes]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de sedes'

        finally:
            conn.close()
