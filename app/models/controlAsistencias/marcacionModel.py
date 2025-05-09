import pyodbc
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class Marcaciones:
    @staticmethod
    def execute_sp(mquery, params=None):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            if mquery == 1:  # Insertar marcación
                cursor.execute('''
                    EXEC [dbo].[SP_MARCACIONES]
                        @mquery = ?,
                        @fechaMarcacion = ?,
                        @horaMarcacion = ?,
                        @idEmpleado = ?,
                        @observacion = ?,
                        @estacion = ?,
                        @operador = ?
                ''', (
                    mquery,
                    params.get('fechaMarcacion'),
                    params.get('horaMarcacion'),
                    params.get('idEmpleado'),
                    params.get('observacion', ''),
                    params.get('estacion', ''),
                    params.get('operador', '')
                ))
                
                conn.commit()
                result = cursor.fetchone()
                success = result[0] if result else 'FALSE'
                message = result[1] if result else 'Error en la operación'
                return {'success': success == 'TRUE', 'message': message}
            
            elif mquery == 4:  # Consultar marcaciones
                cursor.execute('''
                    EXEC [dbo].[SP_MARCACIONES]
                        @mquery = ?,
                        @idArea = ?,
                        @nombres = ?,
                        @idCargo = ?,
                        @dni = ?,
                        @deFecha = ?,
                        @hastaFecha = ?
                ''', (
                    mquery,
                    params.get('idArea', None),
                    params.get('nombres', None),
                    params.get('idCargo', None),
                    params.get('dni', None),
                    params.get('deFecha', None),
                    params.get('hastaFecha', None)
                ))
                
                results = cursor.fetchall()
                data = [dict(zip([column[0] for column in cursor.description], row)) for row in results]
                return {'data': data}
            
            elif mquery == 5:  # Contar marcaciones
                cursor.execute('''
                    EXEC [dbo].[SP_MARCACIONES]
                        @mquery = ?,
                        @idArea = ?,
                        @nombres = ?,
                        @idCargo = ?,
                        @dni = ?,
                        @deFecha = ?,
                        @hastaFecha = ?
                ''', (
                    mquery,
                    params.get('idArea', ''),
                    params.get('nombres', ''),
                    params.get('idCargo', ''),
                    params.get('dni', ''),
                    params.get('deFecha', '1900-01-01'),
                    params.get('hastaFecha', '1900-01-01')
                ))
                
                result = cursor.fetchone()
                return {'total': result.total if result else 0}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
        finally:
            conn.close()

    @staticmethod
    def registrar_marcacion(data, current_user, remote_addr):
        # Agregamos campos de auditoría
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        
        # Asignamos valores para el stored procedure
        params = {
            'fechaMarcacion': data.get('fechaMarcacion'),
            'horaMarcacion': data.get('horaMarcacion'),
            'idEmpleado': data.get('idEmpleado'),
            'observacion': data.get('observacion', ''),
            'estacion': data.get('estacion', remote_addr),
            'operador': data.get('operador', current_user)
        }
        
        return Marcaciones.execute_sp(1, params)

    @staticmethod
    def listar_marcaciones(filtros=None):
        filtros = filtros or {}
        return Marcaciones.execute_sp(4, filtros)
