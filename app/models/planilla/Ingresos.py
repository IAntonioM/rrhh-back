import pyodbc
import re
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class Ingresos:
    @staticmethod
    def execute_sp(accion, params):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_Ingresos] 
                    @accion = ?, 
                    @idConcepto = ?, 
                    @idCondicionLaboral = ?, 
                    @ccodcpto_Anterior = ?, 
                    @codigoPDT = ?, 
                    @codigoInterno = ?, 
                    @concepto = ?, 
                    @tipo = 'I', 
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
                return {
                    'success': True,
                    'message': result[0] if result else 'Operación exitosa'
                }
            else:  # Para LIST
                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()
                
                if not results:
                    return {
                        'success': True,
                        'data': [],
                        'pagination': {
                            'current_page': params.get('current_page', 1),
                            'last_page': 1,
                            'per_page': params.get('per_page', 10),
                            'total': 0
                        }
                    }

                # Convertir los resultados a diccionario
                data = []
                pagination = {}
                
                for row in results:
                    row_dict = {}
                    for i, value in enumerate(row):
                        column_name = columns[i]
                        if column_name in ['current_page', 'last_page', 'per_page', 'total']:
                            pagination[column_name] = value
                        else:
                            row_dict[column_name] = value
                    data.append(row_dict)

                return {
                    'success': True,
                    'data': data,
                    'pagination': pagination
                }

        except Exception as e:
            print(f"Error en execute_sp: {str(e)}")  # Para debugging
            return {
                'success': False,
                'message': str(e)
            }
        finally:
            conn.close()

    @staticmethod
    def create_Ingreso(data, current_user, remote_addr):
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return Ingresos.execute_sp('CREATE', data)

    @staticmethod
    def update_Ingreso(data, current_user, remote_addr):
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return Ingresos.execute_sp('UPDATE', data)

    @staticmethod
    def delete_Ingreso(idConcepto):
        return Ingresos.execute_sp('DELETE', {'idConcepto': idConcepto, 'flag_estado': 0})

    @staticmethod
    def list_ingresos(filtros=None):
        filtros = filtros or {}
        return Ingresos.execute_sp('LIST', filtros)