import pyodbc
import re
from config import get_db_connection
from ..utils.auditv2 import AuditFieldsv2

class Egresos:
    @staticmethod
    def execute_sp(accion, params):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            # Actualizado para incluir parámetros de paginación
            cursor.execute('''
                EXEC [dbo].[sp_Egresos] 
                    @accion = ?, 
                    @idConcepto = ?, 
                    @idCondicionLaboral = ?, 
                    @ccodcpto_Anterior = ?, 
                    @codigoPDT = ?, 
                    @codigoInterno = ?, 
                    @concepto = ?, 
                    @tipo = 'E', 
                    @tipoCalculo = ?, 
                    @idTipoMonto = ?, 
                    @flag_ATM = ?, 
                    @monto = ?, 
                    @flag_estado = ?, 
                    @flag_apldialab = ?,
                    @current_page = ?,
                    @per_page = ?
            ''', (
                accion,
                params.get('idConcepto'),
                params.get('idCondicionLaboral'),
                params.get('ccodcpto_Anterior'),
                params.get('codigoPDT'),
                params.get('codigoInterno'),
                params.get('concepto'),
                params.get('tipoCalculo'),
                params.get('idTipoMonto'),
                params.get('flag_ATM'),
                params.get('monto'),
                params.get('flag_estado', 1),
                params.get('flag_apldialab'),
                params.get('current_page', 1),
                params.get('per_page', 10)
            ))

            if accion in ['CREATE', 'UPDATE', 'DELETE']:
                conn.commit()
                result = cursor.fetchone()
                return True, result[0] if result else 'Operación exitosa'
            else:
                # Para LIST, necesitamos procesar la metadata de paginación
                results = cursor.fetchall()
                if not results:
                    return []
                
                # El SP devuelve la metadata de paginación en cada fila
                pagination = {
                    'current_page': results[0].current_page,
                    'last_page': results[0].last_page,
                    'per_page': results[0].per_page,
                    'total': results[0].total
                }
                
                # Convertir los resultados a diccionario excluyendo los campos de paginación
                data = [dict((column[0], value) 
                           for column, value in zip(cursor.description, row)
                           if column[0] not in ['current_page', 'last_page', 'per_page', 'total']) 
                       for row in results]
                
                return {'data': data, 'pagination': pagination}

        except pyodbc.Error as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error en la operación'
        finally:
            conn.close()

    @staticmethod
    def create_egreso(data, current_user, remote_addr):
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return Egresos.execute_sp('CREATE', data)

    @staticmethod
    def update_egreso(data, current_user, remote_addr):
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return Egresos.execute_sp('UPDATE', data)

    @staticmethod
    def delete_egreso(idConcepto):
        return Egresos.execute_sp('DELETE', {'idConcepto': idConcepto, 'flag_estado': 0})

    @staticmethod
    def list_egresos(filtros=None):
        filtros = filtros or {}
        return Egresos.execute_sp('LIST', filtros)