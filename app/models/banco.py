
import pyodbc
import re
from config import get_db_connection
from ..utils.auditv2 import AuditFieldsv2


import pyodbc
import re

class BancoModel:

    @staticmethod
    def create_banco(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblBanco] 
                    @accion = 2,
                    @Banco = ?,
                    @fecha_registro = ?,
                    @operador_registro = ?,
                    @estacion_registro = ?,
                    @fecha_modificacion = ?,
                    @operador_modificacion = ?,
                    @estacion_modificacion = ?,
                    @flag_estado = ?
            ''', (data['Banco'], data['fecha_registro'], data['operador_registro'], 
                  data['estacion_registro'], data['fecha_modificacion'], 
                  data['operador_modificacion'], data['estacion_modificacion'], 
                  data['flag_estado']))

            conn.commit()
            return True, 'Banco registrado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar banco'

        finally:
            conn.close()

    @staticmethod
    def update_banco(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblBanco] 
                    @accion = 3,
                    @idBanco_update = ?,
                    @Banco = ?,
                    @fecha_registro = ?,
                    @operador_registro = ?,
                    @estacion_registro = ?,
                    @fecha_modificacion = ?,
                    @operador_modificacion = ?,
                    @estacion_modificacion = ?,
                    @flag_estado = ?
            ''', (data['idBanco_update'], data['Banco'], data['fecha_registro'], 
                  data['operador_registro'], data['estacion_registro'], 
                  data['fecha_modificacion'], data['operador_modificacion'], 
                  data['estacion_modificacion'], data['flag_estado']))

            conn.commit()
            return True, 'Banco actualizado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar banco'

        finally:
            conn.close()

    @staticmethod
    def get_bancos_list(filtros=None):
        conn = get_db_connection()
        try:
            # Definir los valores de los filtros por defecto (si no se pasan)
            flag_estado = filtros.get('flag_estado', None) if filtros else None

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblBanco] 
                    @accion = 4,
                    @flag_estado = ?
            ''', (flag_estado,))

            bancos = cursor.fetchall()

            # Procesar y retornar los resultados en forma de lista de diccionarios
            return [{
                'idBanco': b[0], 
                'Banco': b[1], 
                'fecha_registro': b[2], 
                'operador_registro': b[3],
                'estacion_registro': b[4],
                'fecha_modificacion': b[5],
                'operador_modificacion': b[6],
                'estacion_modificacion': b[7],
                'flag_estado': b[8]
            } for b in bancos]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de bancos'

        finally:
            conn.close()

