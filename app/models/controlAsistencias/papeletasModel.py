import pyodbc
import re
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class PapeletaModel:
    @staticmethod
    def execute_sp(mquery, params=None):
        """
        Ejecuta el stored procedure sp_papeleta con los parámetros especificados
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Parámetros por defecto
            default_params = {
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
            
            # Combinar parámetros por defecto con los proporcionados
            if params:
                default_params.update(params)
            
            # Ejecutar el stored procedure
            cursor.execute("""
                EXEC [dbo].[sp_papeleta] 
                    @mquery=?, @idPapeleta=?, @idSede=?, @idArea=?, @idsuperior=?,
                    @idSolicitante=?, @idTipoSalida=?, @motivoSalida=?, @fecha_salida=?,
                    @idTipoPapeleta=?, @horaSalida=?, @horaRetorno=?, @motivoModificacion=?,
                    @idUsuario_registro=?, @idUsuario_mod=?, @idUsuario_rrhh=?,
                    @idUsuario_jefe=?, @idUsuario_seg=?, @estacion=?, @operador=?,
                    @fechainicio=?, @fechafin=?, @inicio=?, @final=?, @nro=?,
                    @anio=?, @nombres=?, @apellidos=?, @solicitante=?, @idEmpleado=?
            """, mquery, default_params['idPapeleta'], default_params['idSede'], 
                default_params['idArea'], default_params['idsuperior'], default_params['idSolicitante'],
                default_params['idTipoSalida'], default_params['motivoSalida'], default_params['fecha_salida'], 
                default_params['idTipoPapeleta'], default_params['horaSalida'], default_params['horaRetorno'], 
                default_params['motivoModificacion'], default_params['idUsuario_registro'],
                default_params['idUsuario_mod'], default_params['idUsuario_rrhh'], default_params['idUsuario_jefe'], 
                default_params['idUsuario_seg'], default_params['estacion'], default_params['operador'], 
                default_params['fechainicio'], default_params['fechafin'], default_params['inicio'], 
                default_params['final'], default_params['nro'], default_params['anio'], 
                default_params['nombres'], default_params['apellidos'], default_params['solicitante'], 
                default_params['idEmpleado'])
            
            # Manejo de respuestas según el tipo de operación
            if mquery in [1, 2, 15, 16, 17, 18, 19, 25, 26, 28, 111]:  # Operaciones de modificación
                conn.commit()
                result = cursor.fetchone()
                message = result[0] if result and len(result) > 0 else 'Operación exitosa'
                if cursor.description:  # Solo hacer fetchone si hay resultados
                    result = cursor.fetchone()
                    message = result[0] if result and len(result) > 0 else 'Operación exitosa'
                else:
                    message = 'Operación exitosa'
                
                return {'success': True, 'message': message}
            
            elif mquery in [5, 7, 9, 11]:  # Consultas con paginación
                results = cursor.fetchall()
                if not results:
                    return {'data': [], 'pagination': {}}
                
                # Obtener datos y columnas
                columns = [column[0] for column in cursor.description] if cursor.description else []
                data = [dict(zip(columns, row)) for row in results]
                
                return {'data': data}
            
            elif mquery in [6, 8, 10, 12]:  # Conteos
                result = cursor.fetchone()
                count = result[0] if result else 0
                return {'count': count}
            
            else:  # Consultas simples (seleccionar, historial, etc.)
                results = cursor.fetchall()
                columns = [column[0] for column in cursor.description] if cursor.description else []
                data = [dict(zip(columns, row)) for row in results]
                return {'data': data}
                
        except Exception as e:
            return {'success': False, 'message': f"Error ejecutando procedimiento: {str(e)}"}
        finally:
            conn.close()

    # Métodos de inserción
    @staticmethod
    def create_papeleta(data, current_user, remote_addr):
        """Insertar nueva papeleta (mquery = 1)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaModel.execute_sp(1, data)
    
    @staticmethod
    def create_papeleta_rrhh(data, current_user, remote_addr):
        """Insertar papeleta por RRHH - aprobada automáticamente (mquery = 111)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaModel.execute_sp(111, data)

    # Métodos de edición
    @staticmethod
    def update_papeleta(data, current_user, remote_addr):
        """Editar papeleta existente (mquery = 2)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaModel.execute_sp(2, data)
    
    @staticmethod
    def update_papeleta_jefe(data, current_user, remote_addr):
        """Modificar papeleta por jefe (mquery = 19)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaModel.execute_sp(19, data)
    
    @staticmethod
    def update_papeleta_rrhh(data, current_user, remote_addr):
        """Modificar papeleta por RRHH (mquery = 28)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaModel.execute_sp(28, data)

    # Métodos de consulta
    @staticmethod
    def get_papeleta(idPapeleta):
        """Seleccionar papeleta específica (mquery = 4)"""
        return PapeletaModel.execute_sp(4, {'idPapeleta': idPapeleta})
    
    @staticmethod
    def get_papeleta_seguridad(idPapeleta):
        """Seleccionar papeleta para seguridad (mquery = 20)"""
        return PapeletaModel.execute_sp(20, {'idPapeleta': idPapeleta})
    
    @staticmethod
    def get_papeleta_rrhh(idPapeleta):
        """Seleccionar papeleta para RRHH (mquery = 21)"""
        return PapeletaModel.execute_sp(21, {'idPapeleta': idPapeleta})

    # Métodos de listado
    @staticmethod
    def list_papeletas(filtros=None):
        """Consulta de papeletas con paginación (mquery = 5)"""
        filtros = filtros or {}
        return PapeletaModel.execute_sp(5, filtros)
    
    @staticmethod
    def list_papeletas_rrhh(filtros=None):
        """Consulta de papeletas para RRHH (mquery = 7)"""
        filtros = filtros or {}
        return PapeletaModel.execute_sp(7, filtros)
    
    @staticmethod
    def list_papeletas_seguridad(filtros=None):
        """Consulta de papeletas para Seguridad (mquery = 9)"""
        filtros = filtros or {}
        return PapeletaModel.execute_sp(9, filtros)
    
    @staticmethod
    def list_papeletas_jefe(filtros=None):
        """Consulta de papeletas por área - jefe (mquery = 11)"""
        filtros = filtros or {}
        return PapeletaModel.execute_sp(11, filtros)

    # Métodos de conteo
    @staticmethod
    def count_papeletas(filtros=None):
        """Contar papeletas (mquery = 6)"""
        filtros = filtros or {}
        return PapeletaModel.execute_sp(6, filtros)
    
    @staticmethod
    def count_papeletas_rrhh(filtros=None):
        """Contar papeletas para RRHH (mquery = 8)"""
        filtros = filtros or {}
        return PapeletaModel.execute_sp(8, filtros)
    
    @staticmethod
    def count_papeletas_seguridad(filtros=None):
        """Contar papeletas para Seguridad (mquery = 10)"""
        filtros = filtros or {}
        return PapeletaModel.execute_sp(10, filtros)
    
    @staticmethod
    def count_papeletas_jefe(filtros=None):
        """Contar papeletas por área - jefe (mquery = 12)"""
        filtros = filtros or {}
        return PapeletaModel.execute_sp(12, filtros)

    # Métodos de aprobación y rechazo
    @staticmethod
    def approve_rrhh(data, current_user, remote_addr):
        """Aprobar papeleta por RRHH (mquery = 15)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaModel.execute_sp(15, data)
    
    @staticmethod
    def reject_rrhh(data, current_user, remote_addr):
        """Rechazar papeleta por RRHH (mquery = 16)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaModel.execute_sp(16, data)
    
    @staticmethod
    def approve_jefe(data, current_user, remote_addr):
        """Aprobar papeleta por jefe (mquery = 17)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaModel.execute_sp(17, data)
    
    @staticmethod
    def reject_jefe(data, current_user, remote_addr):
        """Rechazar papeleta por jefe (mquery = 18)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaModel.execute_sp(18, data)

    # Métodos de registro de horarios
    @staticmethod
    def register_departure_time(data, current_user, remote_addr):
        """Registrar hora de salida (mquery = 25)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaModel.execute_sp(25, data)
    
    @staticmethod
    def register_return_time(data, current_user, remote_addr):
        """Registrar hora de retorno (mquery = 26)"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return PapeletaModel.execute_sp(26, data)

    # Método de historial
    @staticmethod
    def get_approval_history(idPapeleta):
        """Obtener historial de aprobaciones (mquery = 27)"""
        return PapeletaModel.execute_sp(27, {'idPapeleta': idPapeleta})