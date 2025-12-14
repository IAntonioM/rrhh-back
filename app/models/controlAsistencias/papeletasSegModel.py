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
                'idSolicitante': '',
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
            # Para registro de hora (mquery 30 y 40)
            elif mquery in (30, 40):
                try:
                    # El SP ejecuta UPDATE y luego SELECT con el mensaje
                    # Necesitamos llegar al último conjunto de resultados
                    message = None
                    
                    # Leer el primer conjunto de resultados (del UPDATE)
                    try:
                        cursor.fetchall()  # Consumir resultados del UPDATE si los hay
                    except:
                        pass
                    
                    # Avanzar al siguiente conjunto de resultados (el SELECT con el mensaje)
                    if cursor.nextset():
                        row = cursor.fetchone()
                        if row:
                            message = row[0]
                    
                    conn.commit()
                    
                    if message:
                        # Verificar si el mensaje indica éxito
                        if 'correctamente' in message.lower():
                            return {'success': True, 'message': message}
                        else:
                            return {'success': True, 'message': message}
                    
                    return {'success': False, 'message': 'No se recibió respuesta del servidor'}
                except Exception as e:
                    try:
                        conn.rollback()
                    except:
                        pass
                    return {'success': False, 'message': f'Error al registrar: {str(e)}'}
            
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
    
    @staticmethod
    def registrar_hora_salida(idPapeleta, idUsuario_seg, estacion):
        """Registrar hora de salida en Seguridad (mquery = 30)"""
        params = {
            'idPapeleta': idPapeleta,
            'idUsuario_seg': idUsuario_seg,
            'estacion': estacion
        }
        result = PapeletaSeg.execute_sp(30, params)
        
        # El SP retorna un mensaje en la primera columna
        if result and 'data' in result and result['data']:
            message = result['data'][0] if isinstance(result['data'], list) else list(result['data'].values())[0]
            return {'success': True, 'message': message}
        return result

    @staticmethod
    def registrar_hora_retorno(idPapeleta, idUsuario_seg, estacion):
        """Registrar hora de retorno en Seguridad (mquery = 40)"""
        params = {
            'idPapeleta': idPapeleta,
            'idUsuario_seg': idUsuario_seg,
            'estacion': estacion
        }
        result = PapeletaSeg.execute_sp(40, params)
        
        # El SP retorna un mensaje en la primera columna
        if result and 'data' in result and result['data']:
            message = result['data'][0] if isinstance(result['data'], list) else list(result['data'].values())[0]
            return {'success': True, 'message': message}
        return result