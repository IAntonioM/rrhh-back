import pyodbc
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class Subsidio:
    @staticmethod
    def execute_sp(mquery, params):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_subsidio]
                    @mquery = ?,
                    @idSubsidio = ?,
                    @concepto = ?,
                    @subsidiar = ?,
                    @permitir = ?,
                    @observacion = ?,
                    @estacion = ?,
                    @operador = ?
            ''', (
                mquery,
                params.get('idSubsidio'),
                params.get('concepto'),
                params.get('subsidiar'),
                params.get('permitir'),
                params.get('observacion'),
                params.get('estacion_modificacion'),
                params.get('operador_modificacion')
            ))
            
            if mquery in [1, 2, 3]:  # INSERT, UPDATE, DELETE
                # ✅ PRIMERO obtener el resultado, DESPUÉS hacer commit
                result = cursor.fetchone()
                conn.commit()
                
                message = result[1] if result and len(result) > 1 else 'Operación exitosa'
                
                return {
                    'success': True,
                    'message': message
                }
            elif mquery == 4:  # GET por ID
                columns = [column[0] for column in cursor.description]
                result = cursor.fetchone()
                
                if not result:
                    return {
                        'success': False,
                        'message': 'Subsidio no encontrado'
                    }
                
                data = dict(zip(columns, result))
                return {
                    'success': True,
                    'data': data
                }
            elif mquery == 5:  # LIST
                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()
                
                data = [dict(zip(columns, row)) for row in results]
                return {
                    'success': True,
                    'data': data
                }
            elif mquery == 6:  # COUNT
                result = cursor.fetchone()
                return {
                    'success': True,
                    'data': {'total': result[0] if result else 0}
                }
                
        except Exception as e:
            print(f"Error en execute_sp: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
        finally:
            conn.close()
    
    @staticmethod
    def create_subsidio(data, current_user, remote_addr):
        audit_data = AuditFieldsv2.add_audit_fields({}, current_user, remote_addr, include_reg=True)
        data.update(audit_data)
        return Subsidio.execute_sp(1, data)
    
    @staticmethod
    def update_subsidio(data, current_user, remote_addr):
        audit_data = AuditFieldsv2.add_audit_fields({}, current_user, remote_addr, include_reg=False)
        data.update(audit_data)
        return Subsidio.execute_sp(2, data)
    
    @staticmethod
    def delete_subsidio(idSubsidio, current_user, remote_addr):
        audit_data = AuditFieldsv2.add_audit_fields({}, current_user, remote_addr, include_reg=False)
        data = {'idSubsidio': idSubsidio}
        data.update(audit_data)
        return Subsidio.execute_sp(3, data)
    
    @staticmethod
    def get_subsidio(idSubsidio):
        return Subsidio.execute_sp(4, {'idSubsidio': idSubsidio})
    
    @staticmethod
    def list_subsidios():
        return Subsidio.execute_sp(5, {})
    
    @staticmethod
    def count_subsidios():
        return Subsidio.execute_sp(6, {})