import pyodbc
import re
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class GrupoModel:
    @staticmethod
    def execute_sp(mquery, params):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Usar SET NOCOUNT ON para evitar problemas con múltiples resultsets
            cursor.execute("SET NOCOUNT ON")
            
            cursor.execute('''
                EXEC [dbo].[sp_grupos]
                    @mquery = ?,
                    @idGrupo = ?,
                    @nombre = ?,
                    @observaciones = ?,
                    @estacion = ?,
                    @operador = ?,
                    @inicio = ?,
                    @final = ?,
                    @periodo = ?,
                    @idEmpleado = ?,
                    @idEmpGrupo = ?,
                    @tipo = ?
            ''', (
                mquery,
                params.get('idGrupo', 0),
                params.get('nombre', ''),
                params.get('observaciones', ''),
                params.get('estacion', ''),
                params.get('operador', ''),
                params.get('inicio', 0),
                params.get('final', 0),
                params.get('periodo', 0),
                params.get('idEmpleado', 0),
                params.get('idEmpGrupo', 0),
                params.get('tipo', '')
            ))

            if mquery in [1, 22, 3, 6, 7]:  # INSERT, UPDATE, DELETE, INSERT_EMP, DELETE_EMP
                # Verificar si hay resultados antes de fetchear
                if cursor.description:
                    result = cursor.fetchone()
                    conn.commit()
                    
                    if result:
                        return {
                            'success': result[0] == 'TRUE',
                            'message': result[1] if len(result) > 1 else 'Operación exitosa'
                        }
                else:
                    conn.commit()
                
                return {
                    'success': True,
                    'message': 'Operación exitosa'
                }
                
            else:  # Para SELECT (2, 4, 5, 8, 20, 21)
                if not cursor.description:
                    return {
                        'success': True,
                        'data': []
                    }
                    
                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()
                
                if not results:
                    return {
                        'success': True,
                        'data': []
                    }

                # Convertir los resultados a diccionario
                data = []
                for row in results:
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[columns[i]] = value
                    data.append(row_dict)

                return {
                    'success': True,
                    'data': data
                }

        except pyodbc.Error as e:
            if conn:
                conn.rollback()
            print(f"Error ODBC en execute_sp: {str(e)}")
            return {
                'success': False,
                'message': f'Error en base de datos: {str(e)}'
            }
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error en execute_sp: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def create_grupo(data, current_user, remote_addr):
        """Crear un nuevo grupo - @mquery = 1"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        result = GrupoModel.execute_sp(1, data)
        return result['success'], result.get('message', 'Error al crear grupo')

    @staticmethod
    def get_grupo_by_id(idGrupo):
        """Obtener un grupo por ID - @mquery = 2"""
        result = GrupoModel.execute_sp(2, {'idGrupo': idGrupo})
        return result

    @staticmethod
    def update_grupo(data, current_user, remote_addr):
        """Actualizar un grupo - @mquery = 22"""
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        result = GrupoModel.execute_sp(22, data)
        return result['success'], result.get('message', 'Error al actualizar grupo')

    @staticmethod
    def delete_grupo(idGrupo, current_user, remote_addr):
        """Eliminar un grupo - @mquery = 3"""
        data = {
            'idGrupo': idGrupo
        }
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        result = GrupoModel.execute_sp(3, data)
        return result['success'], result.get('message', 'Error al eliminar grupo')

    @staticmethod
    def list_grupos():
        """Listar todos los grupos activos - @mquery = 4"""
        result = GrupoModel.execute_sp(4, {})
        return result

    @staticmethod
    def count_grupos():
        """Contar grupos activos - @mquery = 5"""
        result = GrupoModel.execute_sp(5, {})
        return result

    @staticmethod
    def add_empleado_grupo(idEmpleado, idGrupo, current_user, remote_addr):
        """Agregar empleado a un grupo - @mquery = 6"""
        data = {
            'idEmpleado': idEmpleado,
            'idGrupo': idGrupo
        }
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        result = GrupoModel.execute_sp(6, data)
        return result['success'], result.get('message', 'Error al agregar empleado al grupo')

    @staticmethod
    def remove_empleado_grupo(idEmpGrupo, current_user, remote_addr):
        """Eliminar empleado de un grupo - @mquery = 7"""
        data = {
            'idEmpGrupo': idEmpGrupo
        }
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        result = GrupoModel.execute_sp(7, data)
        return result['success'], result.get('message', 'Error al eliminar empleado del grupo')

    @staticmethod
    def list_empleados_by_grupo(idGrupo):
        """Listar empleados de un grupo - @mquery = 8"""
        result = GrupoModel.execute_sp(8, {'idGrupo': idGrupo})
        return result

    @staticmethod
    def combo_grupos_planilla():
        """Combo de grupos de planilla - @mquery = 20"""
        result = GrupoModel.execute_sp(20, {})
        return result

    @staticmethod
    def combo_grupos_planilla_asis(periodo):
        """Combo de grupos de planilla por periodo - @mquery = 21"""
        result = GrupoModel.execute_sp(21, {'periodo': periodo})
        return result
