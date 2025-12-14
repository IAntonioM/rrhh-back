import pyodbc
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class Asistencia:
    @staticmethod
    def execute_sp(mquery, params=None):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Preparar parámetros con valores por defecto para el nuevo SP
            default_params = {
                'mquery': mquery,
                'idEmpleado': '',
                'nombreEmpleado': None,
                'idArea': None,
                'idcondicion': None,
                'dni': None,
                'fecha_desde': None,
                'fecha_hasta': None,
                'idMarcacion': None
            }
            
            # Actualizar con parámetros proporcionados
            if params:
                default_params.update(params)
            
            cursor.execute('''
                EXEC [dbo].[sp_asistencias2] 
                    @mquery = ?,
                    @idEmpleado = ?,
                    @nombreEmpleado = ?,
                    @idArea = ?,
                    @idcondicion = ?,
                    @dni = ?,
                    @fecha_desde = ?,
                    @fecha_hasta = ?,
                    @idMarcacion = ?
            ''', (
                default_params['mquery'],
                default_params['idEmpleado'],
                default_params['nombreEmpleado'],
                default_params['idArea'],
                default_params['idcondicion'],
                default_params['dni'],
                default_params['fecha_desde'],
                default_params['fecha_hasta'],
                default_params['idMarcacion']
            ))

            # Para consultas que retornan datos
            if mquery in [1, 2, 50]:
                try:
                    if cursor.description:
                        results = cursor.fetchall()
                        if results:
                            data = [dict(zip([column[0] for column in cursor.description], row)) for row in results]
                            return {'success': True, 'data': data}
                        else:
                            return {'success': True, 'data': []}
                    else:
                        return {'success': True, 'data': []}
                except Exception as e:
                    return {'success': False, 'message': f'Error al procesar resultado: {str(e)}'}
            
        except Exception as e:
            return {'success': False, 'message': f'Error en stored procedure: {str(e)}'}
        finally:
            try:
                conn.close()
            except:
                pass

    @staticmethod
    def consulta_asistencias_por_empleado(data=None):
        """Consulta asistencias por empleado (mquery = 1)"""
        return Asistencia.execute_sp(1, data)

    @staticmethod
    def consulta_asistencias_detalladas_por_empleado(data=None):
        """Consulta asistencias detalladas por empleado (mquery = 2)"""
        return Asistencia.execute_sp(2, data)

    @staticmethod
    def consulta_empleados(data=None):
        """Consulta empleados con filtros (mquery = 50)"""
        return Asistencia.execute_sp(50, data)