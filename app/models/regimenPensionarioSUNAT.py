import pyodbc
import re
from config import get_db_connection
from ..utils.auditv2 import AuditFieldsv2

class RegimenPensionarioSUNATModel:

    @staticmethod
    def create_regimen_pensionario(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir campos de auditoría al diccionario de datos
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            # Realizar la ejecución del procedimiento almacenado para la inserción
            cursor = conn.cursor()
            cursor.execute(''' 
                EXEC [dbo].[sp_tblRegimenPensionarioSUNAT] 
                    @accion = 2,
                    @codigoPDT = ?, 
                    @regimenPensionario = ?,
                    @tipo = ?,
                    @flag_estado = ?
            ''', (data['codigoPDT'], data['regimenPensionario'], data['tipo'], data['flag_estado']))

            conn.commit()
            return True, 'Regimen Pensionario registrado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar regimen pensionario'

        finally:
            conn.close()

    @staticmethod
    def update_regimen_pensionario(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir campos de auditoría al diccionario de datos
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            # Realizar la ejecución del procedimiento almacenado para la actualización
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblRegimenPensionarioSUNAT]
                    @accion = 3,
                    @codigoPDT_update = ?,
                    @regimenPensionario = ?,
                    @tipo = ?,
                    @flag_estado = ?
            ''', (data['codigoPDT_update'], data['regimenPensionario'], data['tipo'], data['flag_estado']))

            conn.commit()
            return True, 'Regimen Pensionario actualizado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar regimen pensionario'

        finally:
            conn.close()

    @staticmethod
    def get_regimen_pensionarios_list(filtros=None):
        conn = get_db_connection()
        try:
            # Definir los valores de los filtros por defecto (si no se pasan)
            codigoPDT = filtros.get('codigoPDT', None) if filtros else None
            regimenPensionario = filtros.get('regimenPensionario', None) if filtros else None
            tipo = filtros.get('tipo', None) if filtros else None
            flag_estado = filtros.get('flag_estado', None) if filtros else None

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblRegimenPensionarioSUNAT] 
                    @accion = 1,
                    @codigoPDT = ?,
                    @regimenPensionario = ?,
                    @tipo = ?,
                    @flag_estado = ?
            ''', (codigoPDT, regimenPensionario, tipo, flag_estado))

            regimenes_pensionarios = cursor.fetchall()

            # Procesar y retornar los resultados en forma de lista de diccionarios
            return [{
                'codigoPDT': r[0], 
                'regimenPensionario': r[1], 
                'tipo': r[2], 
                'flag_estado': r[3]
            } for r in regimenes_pensionarios]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de regimenes pensionarios'

        finally:
            conn.close()
