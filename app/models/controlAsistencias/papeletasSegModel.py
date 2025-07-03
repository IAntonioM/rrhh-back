import pyodbc
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class PapeletaSeg:
    @staticmethod
    def execute_sp(mquery, params=None):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Preparar parámetros con valores por defecto
            default_params = {
                'mquery': mquery,
                'idPapeleta': 0,
                'idSede': 0,
                'idArea': '',
                'idsuperior': '',
                'idSolicitante': 0,
                'idTipoSalida': 0,
                'motivoSalida': '',
                'fecha_salida': '1900-01-01',
                'idTipoPapeleta': 0,
                'horaSalida': '',
                'horaRetorno': '',
                'motivoModificacion': '',
                'idUsuario_registro': '',
                'idUsuario_mod': '',
                'idUsuario_rrhh': '',
                'idUsuario_jefe': '',
                'idUsuario_seg': '',
                'estacion': '',
                'operador': '',
                'fechainicio': '',
                'fechafin': '',
                'inicio': 0,
                'final': 0,
                'nro': '',
                'anio': '',
                'nombres': '',
                'apellidos': '',
                'solicitante': '',
                'idEmpleado': 0
            }
            
            # Actualizar con parámetros proporcionados
            if params:
                default_params.update(params)
            
            cursor.execute('''
                EXEC [dbo].[sp_papeleta_seg] 
                    @mquery = ?,
                    @idPapeleta = ?,
                    @idSede = ?,
                    @idArea = ?,
                    @idsuperior = ?,
                    @idSolicitante = ?,
                    @idTipoSalida = ?,
                    @motivoSalida = ?,
                    @fecha_salida = ?,
                    @idTipoPapeleta = ?,
                    @horaSalida = ?,
                    @horaRetorno = ?,
                    @motivoModificacion = ?,
                    @idUsuario_registro = ?,
                    @idUsuario_mod = ?,
                    @idUsuario_rrhh = ?,
                    @idUsuario_jefe = ?,
                    @idUsuario_seg = ?,
                    @estacion = ?,
                    @operador = ?,
                    @fechainicio = ?,
                    @fechafin = ?,
                    @inicio = ?,
                    @final = ?,
                    @nro = ?,
                    @anio = ?,
                    @nombres = ?,
                    @apellidos = ?,
                    @solicitante = ?,
                    @idEmpleado = ?
            ''', (
                default_params['mquery'],
                default_params['idPapeleta'],
                default_params['idSede'],
                default_params['idArea'],
                default_params['idsuperior'],
                default_params['idSolicitante'],
                default_params['idTipoSalida'],
                default_params['motivoSalida'],
                default_params['fecha_salida'],
                default_params['idTipoPapeleta'],
                default_params['horaSalida'],
                default_params['horaRetorno'],
                default_params['motivoModificacion'],
                default_params['idUsuario_registro'],
                default_params['idUsuario_mod'],
                default_params['idUsuario_rrhh'],
                default_params['idUsuario_jefe'],
                default_params['idUsuario_seg'],
                default_params['estacion'],
                default_params['operador'],
                default_params['fechainicio'],
                default_params['fechafin'],
                default_params['inicio'],
                default_params['final'],
                default_params['nro'],
                default_params['anio'],
                default_params['nombres'],
                default_params['apellidos'],
                default_params['solicitante'],
                default_params['idEmpleado']
            ))

            # Para consulta con paginación (mquery 9)
            if mquery == 9:
                results = cursor.fetchall()
                data = [dict(zip([column[0] for column in cursor.description], row)) for row in results]
                return {'data': data}
            
            # Para conteo (mquery 10)
            elif mquery == 10:
                result = cursor.fetchone()
                total = result[0] if result else 0
                return {'total': total}
                
            # Para consulta individual (mquery 20)
            elif mquery == 20:
                result = cursor.fetchone()
                if result:
                    data = dict(zip([column[0] for column in cursor.description], result))
                    return {'data': data}
                return {'data': None}
            
        except Exception as e:
            return {'success': False, 'message': f'Error en stored procedure: {str(e)}'}
        finally:
            try:
                conn.close()
            except:
                pass

    @staticmethod
    def consultar_papeletas_seg(filtros=None):
        """Consultar papeletas Seguridad con filtros y paginación (mquery = 9)"""
        filtros = filtros or {}
        return PapeletaSeg.execute_sp(9, filtros)

    @staticmethod
    def contar_papeletas_seg(filtros=None):
        """Contar papeletas Seguridad con filtros (mquery = 10)"""
        filtros = filtros or {}
        return PapeletaSeg.execute_sp(10, filtros)

    @staticmethod
    def obtener_papeleta_seg(idPapeleta):
        """Obtener papeleta individual para Seguridad (mquery = 20)"""
        return PapeletaSeg.execute_sp(20, {'idPapeleta': idPapeleta})