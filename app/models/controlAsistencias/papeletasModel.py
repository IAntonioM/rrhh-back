import pyodbc
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class Papeleta:
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
                'horaSalida': '',
                'horaRetorno': '',
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
                'idEmpleado': 0,
                'fecha_desde': '1900-01-01',
                'fecha_hasta': '1900-01-01',
            }
            
            # Actualizar con parámetros proporcionados
            if params:
                default_params.update(params)
            
            cursor.execute('''
                EXEC [dbo].[sp_papeleta2] 
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
                    @idEmpleado = ?,
                    @fecha_desde = ?,
                    @fecha_hasta = ?
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
                default_params['idEmpleado'],
                default_params['fecha_desde'],
                default_params['fecha_hasta']
            ))

            # Para operaciones de inserción, edición y eliminación (mquery 1, 2, 30)
            if mquery in [1, 2, 30]:
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
                            return {'success': True, 'message': 'Papeleta eliminada exitosamente' if mquery == 30 else 'Operación completada exitosamente'}
                        else:
                            conn.rollback()
                            return {'success': False, 'message': 'No se encontró la papeleta a eliminar' if mquery == 30 else 'No se realizaron cambios'}
                            
                except Exception as e:
                    conn.rollback()
                    return {'success': False, 'message': f'Error al procesar resultado: {str(e)}'}
            
            # Para registro de horas (mquery 25, 26)
            elif mquery in [25, 26]:
                try:
                    result = cursor.fetchone()
                    message = result[0] if result else 'Operación exitosa'
                    conn.commit()
                    return {'success': True, 'message': message}
                except Exception as e:
                    conn.rollback()
                    return {'success': False, 'message': f'Error: {str(e)}'}
            
            # Para consulta individual (mquery 4)
            elif mquery == 4:
                result = cursor.fetchone()
                if result:
                    data = dict(zip([column[0] for column in cursor.description], result))
                    return {'data': data}
                return {'data': None}
            
            # Para consulta con paginación (mquery 5)
            elif mquery == 5:
                results = cursor.fetchall()
                data = [dict(zip([column[0] for column in cursor.description], row)) for row in results]
                return {'data': data}
            
            # Para conteo (mquery 6)
            elif mquery == 6:
                result = cursor.fetchone()
                count = result[0] if result else 0
                return {'count': count}
                
            # Para historial de aprobaciones (mquery 27)
            elif mquery == 27:
                results = cursor.fetchall()
                data = [dict(zip([column[0] for column in cursor.description], row)) for row in results]
                return {'data': data}
            
        except Exception as e:
            if mquery in [1, 2, 25, 26, 30]:
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
    def crear_papeleta(data, current_user, remote_addr):
        """Crear nueva papeleta (mquery = 1)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return Papeleta.execute_sp(1, data)

    @staticmethod
    def editar_papeleta(data, current_user, remote_addr):
        """Editar papeleta existente (mquery = 2)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return Papeleta.execute_sp(2, data)

    @staticmethod
    def obtener_papeleta(idPapeleta):
        """Obtener papeleta por ID (mquery = 4)"""
        return Papeleta.execute_sp(4, {'idPapeleta': idPapeleta})

    @staticmethod
    def consultar_papeletas(filtros=None):
        """Consultar papeletas con filtros (mquery = 5)"""
        filtros = filtros or {}
        return Papeleta.execute_sp(5, filtros)

    @staticmethod
    def contar_papeletas(filtros=None):
        """Contar papeletas con filtros (mquery = 6)"""
        filtros = filtros or {}
        return Papeleta.execute_sp(6, filtros)

    @staticmethod
    def registrar_hora_salida(data, current_user, remote_addr):
        """Registrar hora de salida (mquery = 25)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return Papeleta.execute_sp(25, data)

    @staticmethod
    def registrar_hora_retorno(data, current_user, remote_addr):
        """Registrar hora de retorno (mquery = 26)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return Papeleta.execute_sp(26, data)

    @staticmethod
    def historial_aprobaciones(idPapeleta):
        """Obtener historial de aprobaciones (mquery = 27)"""
        return Papeleta.execute_sp(27, {'idPapeleta': idPapeleta})
    
    @staticmethod
    def eliminar_papeleta(data, current_user, remote_addr):
        """Eliminar papeleta (mquery = 30)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return Papeleta.execute_sp(30, data)