import pyodbc
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class PapeletaRRHH:
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
                EXEC [dbo].[sp_papeleta_rrhh] 
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

            # Para operaciones de inserción, aprobación, rechazo y modificación (mquery 111, 15, 16, 28)
            if mquery in [111, 15, 16, 28,30]:
                try:
                    # Verificar si hay resultados disponibles
                    if cursor.description:
                        result = cursor.fetchone()
                        if result:
                            # Manejar tanto formato de 2 campos como de 1 campo
                            if len(result) >= 2:
                                success = str(result[0]).upper() == 'TRUE'
                                message = str(result[1])
                            else:
                                message = str(result[0])
                                success = 'TRUE' in message.upper() or not any(word in message.upper() for word in ['ERROR', 'FALSE', 'NO SE PUEDE', 'NO EXISTE'])
                            
                            # Confirmar la transacción solo si fue exitosa
                            if success:
                                conn.commit()
                            else:
                                conn.rollback()
                                
                            return {'success': success, 'message': message}
                        else:
                            # No hay resultado pero el SP se ejecutó
                            conn.commit()
                            return {'success': True, 'message': 'Operación completada exitosamente'}
                    else:
                        # No hay descripción de cursor, verificar si hay cambios
                        if cursor.rowcount > 0:
                            conn.commit()
                            return {'success': True, 'message': 'Operación completada exitosamente'}
                        else:
                            conn.rollback()
                            return {'success': False, 'message': 'No se realizaron cambios'}
                            
                except Exception as e:
                    conn.rollback()
                    return {'success': False, 'message': f'Error al procesar resultado: {str(e)}'}
            
            # Para consulta con paginación (mquery 7)
            elif mquery == 7:
                results = cursor.fetchall()
                data = [dict(zip([column[0] for column in cursor.description], row)) for row in results]
                return {'data': data}
            
            # Para conteo (mquery 8)
            elif mquery == 8:
                result = cursor.fetchone()
                total = result[0] if result else 0
                return {'total': total}
                
            # Para consulta individual (mquery 21)
            elif mquery == 21:
                result = cursor.fetchone()
                if result:
                    data = dict(zip([column[0] for column in cursor.description], result))
                    return {'data': data}
                return {'data': None}
            
        except Exception as e:
            if mquery in [111, 15, 16, 28]:
                try:
                    conn.rollback()
                except:
                    pass
            return {'success': False, 'message': f'Error en stored procedure: {str(e)}'}
        finally:
            try:
                conn.close()
            except:
                pass

    @staticmethod
    def consultar_papeletas_rrhh(filtros=None):
        """Consultar papeletas RRHH con filtros y paginación (mquery = 7)"""
        filtros = filtros or {}
        return PapeletaRRHH.execute_sp(7, filtros)

    @staticmethod
    def contar_papeletas_rrhh(filtros=None):
        """Contar papeletas RRHH con filtros (mquery = 8)"""
        filtros = filtros or {}
        return PapeletaRRHH.execute_sp(8, filtros)

    @staticmethod
    def aprobar_papeleta_rrhh(data, current_user, remote_addr):
        """Aprobar papeleta por RRHH (mquery = 15)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaRRHH.execute_sp(15, data)

    @staticmethod
    def rechazar_papeleta_rrhh(data, current_user, remote_addr):
        """Rechazar papeleta por RRHH (mquery = 16)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaRRHH.execute_sp(16, data)

    @staticmethod
    def obtener_papeleta_rrhh(idPapeleta):
        """Obtener papeleta individual para RRHH (mquery = 21)"""
        return PapeletaRRHH.execute_sp(21, {'idPapeleta': idPapeleta})

    @staticmethod
    def modificar_papeleta_rrhh(data, current_user, remote_addr):
        """Modificar papeleta desde RRHH (mquery = 28)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaRRHH.execute_sp(28, data)

    @staticmethod
    def crear_papeleta_rrhh(data, current_user, remote_addr):
        """Crear papeleta desde RRHH (mquery = 111)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaRRHH.execute_sp(111, data)
    @staticmethod
    def eliminar_papeleta(data, current_user, remote_addr):
        """Eliminar papeleta (mquery = 30)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaRRHH.execute_sp(30, data)