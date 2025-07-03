import pyodbc
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class PapeletaJefe:
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
                EXEC [dbo].[sp_papeleta_jefe] 
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

            # Para operaciones de aprobación, rechazo y modificación (mquery 17, 18, 19)
            if mquery in [17, 18, 19]:
                try:
                    # Verificar si hay resultados disponibles
                    if cursor.description:
                        result = cursor.fetchone()
                        if result:
                            message = str(result[0])
                            # Determinar si fue exitoso basándose en el mensaje
                            success = not any(word in message.upper() for word in ['ERROR', 'FALSE', 'NO SE PUEDE', 'YA FUE'])
                            
                            # Para modificación, puede retornar 2 campos
                            if len(result) >= 2:
                                success = str(result[0]).upper() == 'TRUE'
                                message = str(result[1])
                            
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
            
            # Para consulta con paginación (mquery 11)
            elif mquery == 11:
                results = cursor.fetchall()
                data = [dict(zip([column[0] for column in cursor.description], row)) for row in results]
                return {'data': data}
            
            # Para conteo (mquery 12)
            elif mquery == 12:
                result = cursor.fetchone()
                total = result[0] if result else 0
                return {'total': total}
            
        except Exception as e:
            if mquery in [17, 18, 19]:
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
    def consultar_papeletas_jefe(filtros=None):
        """Consultar papeletas para jefe con filtros y paginación (mquery = 11)"""
        filtros = filtros or {}
        return PapeletaJefe.execute_sp(11, filtros)

    @staticmethod
    def contar_papeletas_jefe(filtros=None):
        """Contar papeletas para jefe con filtros (mquery = 12)"""
        filtros = filtros or {}
        return PapeletaJefe.execute_sp(12, filtros)

    @staticmethod
    def aprobar_papeleta_jefe(data, current_user, remote_addr):
        """Aprobar papeleta por jefe (mquery = 17)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaJefe.execute_sp(17, data)

    @staticmethod
    def rechazar_papeleta_jefe(data, current_user, remote_addr):
        """Rechazar papeleta por jefe (mquery = 18)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaJefe.execute_sp(18, data)

    @staticmethod
    def modificar_papeleta_jefe(data, current_user, remote_addr):
        """Modificar papeleta por jefe (mquery = 19)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaJefe.execute_sp(19, data)