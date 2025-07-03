import pyodbc
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class Asistencia:
    @staticmethod
    def execute_sp(mquery, params=None):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Preparar parámetros con valores por defecto
            default_params = {
                'mquery': mquery,
                'fechaInicio': '01/01/1990',
                'fechaFin': '01/01/1990',
                'idArea': '',
                'dni': '',
                'apellidos': '',
                'nombres': '',
                'idcondicion': '',
                'dataxmlEmpleados': ''
            }
            
            # Actualizar con parámetros proporcionados
            if params:
                default_params.update(params)
            
            cursor.execute('''
                EXEC [dbo].[SP_ASISTENCIAS] 
                    @mquery = ?,
                    @fechaInicio = ?,
                    @fechaFin = ?,
                    @idArea = ?,
                    @dni = ?,
                    @apellidos = ?,
                    @nombres = ?,
                    @idcondicion = ?,
                    @dataxmlEmpleados = ?
            ''', (
                default_params['mquery'],
                default_params['fechaInicio'],
                default_params['fechaFin'],
                default_params['idArea'],
                default_params['dni'],
                default_params['apellidos'],
                default_params['nombres'],
                default_params['idcondicion'],
                default_params['dataxmlEmpleados']
            ))

            # Para consultas que retornan datos
            if mquery in [1, 2, 6, 7, 8, 9, 50, 99]:
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
            
            # Para conteo de empleados (mquery 51)
            elif mquery == 51:
                try:
                    if cursor.description:
                        result = cursor.fetchone()
                        total = result[0] if result else 0
                        return {'success': True, 'total': total}
                    else:
                        return {'success': True, 'total': 0}
                except Exception as e:
                    return {'success': False, 'message': f'Error al obtener conteo: {str(e)}'}
            
        except Exception as e:
            return {'success': False, 'message': f'Error en stored procedure: {str(e)}'}
        finally:
            try:
                conn.close()
            except:
                pass

    @staticmethod
    def consulta_simple(data=None):
        """Consulta simple (mquery = 1)"""
        return Asistencia.execute_sp(1, data)

    @staticmethod
    def consulta_asistencia_empleados(data=None):
        """Consulta asistencia por empleados (mquery = 2)"""
        return Asistencia.execute_sp(2, data)

    @staticmethod
    def consulta_asistencia_empleados_detalle(data=None):
        """Consulta asistencia por empleados con detalle (mquery = 6)"""
        return Asistencia.execute_sp(6, data)

    @staticmethod
    def consulta_faltas_del_dia(data=None):
        """Consulta faltas del día (mquery = 7)"""
        return Asistencia.execute_sp(7, data)

    @staticmethod
    def consulta_tardanzas_del_dia(data=None):
        """Consulta tardanzas del día (mquery = 8)"""
        return Asistencia.execute_sp(8, data)

    @staticmethod
    def consulta_asistencia_consolidado(data=None):
        """Consulta asistencia consolidada (mquery = 9)"""
        return Asistencia.execute_sp(9, data)

    @staticmethod
    def consulta_empleados(data=None):
        """Consulta empleados con filtros (mquery = 50)"""
        return Asistencia.execute_sp(50, data)

    @staticmethod
    def conteo_empleados(data=None):
        """Conteo de empleados (mquery = 51)"""
        return Asistencia.execute_sp(51, data)

    @staticmethod
    def consulta_asistencia_consolidado_test(data=None):
        """Consulta asistencia consolidada con errores (mquery = 99)"""
        return Asistencia.execute_sp(99, data)