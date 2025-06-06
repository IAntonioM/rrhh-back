import pyodbc
import re
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class Aportaciones:
    @staticmethod
    def execute_sp(accion, params=None):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            if accion == 'TOTALLIST':
                cursor.execute("EXEC [dbo].[sp_Aportaciones] @accion = ?", (accion,))
            else:
                cursor.execute('''
                    EXEC [dbo].[sp_Aportaciones] 
                        @accion = ?, 
                        @idConcepto = ?, 
                        @idCondicionLaboral = ?,    
                        @ccodcpto_Anterior = ?, 
                        @codigoPDT = ?, 
                        @codigoInterno = ?, 
                        @concepto = ?, 
                        @tipo = 'A', 
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
                message = result[0] if result else 'Operación exitosa'
                return {'success': True, 'message': message}
            
            elif accion == 'LIST':
                results = cursor.fetchall()
                if not results:
                    return {'data': [], 'pagination': {}}
                
                pagination = {
                    'current_page': results[0].current_page,
                    'last_page': results[0].last_page,
                    'per_page': results[0].per_page,
                    'total': results[0].total
                }
                
                data = [dict((column[0], value) 
                           for column, value in zip(cursor.description, row)
                           if column[0] not in ['current_page', 'last_page', 'per_page', 'total']) 
                       for row in results]
                
                return {'data': data, 'pagination': pagination}
            
            elif accion == 'TOTALLIST':
                results = cursor.fetchall()
                data = [dict(zip([column[0] for column in cursor.description], row)) for row in results]
                return {'data': data}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
        finally:
            conn.close()

    @staticmethod
    def create_aportacion(data, current_user, remote_addr):
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return Aportaciones.execute_sp('CREATE', data)

    @staticmethod
    def update_aportacion(data, current_user, remote_addr):
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return Aportaciones.execute_sp('UPDATE', data)

    @staticmethod
    def delete_aportacion(idConcepto):
        return Aportaciones.execute_sp('DELETE', {'idConcepto': idConcepto, 'flag_estado': 0})

    @staticmethod
    def list_aportacions(filtros=None):
        filtros = filtros or {}
        return Aportaciones.execute_sp('LIST', filtros)

    @staticmethod
    def list_total_aportacions():
        return Aportaciones.execute_sp('TOTALLIST')