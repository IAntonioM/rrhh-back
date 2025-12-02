import pyodbc
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class EmpHorario:
    @staticmethod
    def execute_sp(mquery, params=None):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Preparar parámetros con valores por defecto
            default_params = {
                'idEmpHorario': 0,
                'idHorario': 0,
                'idEmpleado': None,
                'idTipoHorario': '',
                'fechaDesde': '1900-1-1',
                'fechaHasta': '1900-1-1',
                'estacion': '',
                'operador': '',
                'inicio': 0,
                'final': 0
            }
            
            # Actualizar con los parámetros recibidos
            if params:
                default_params.update(params)
            
            cursor.execute('''
                EXEC [dbo].[sp_emp_horario] 
                    @mquery = ?,
                    @idEmpHorario = ?,
                    @idHorario = ?,
                    @idEmpleado = ?,
                    @idTipoHorario = ?,
                    @fechaDesde = ?,
                    @fechaHasta = ?,
                    @estacion = ?,
                    @operador = ?,
                    @inicio = ?,
                    @final = ?
            ''', (
                mquery,
                default_params['idEmpHorario'],
                default_params['idHorario'],
                default_params['idEmpleado'],
                default_params['idTipoHorario'],
                default_params['fechaDesde'],
                default_params['fechaHasta'],
                default_params['estacion'],
                default_params['operador'],
                default_params['inicio'],
                default_params['final']
            ))

            # mquery 1: INSERT, 2: UPDATE, 3: DELETE
            if mquery in [1, 2, 3]:
                # Intentar obtener el resultado del SELECT del SP
                result = None
                try:
                    # Leer todos los resultsets hasta encontrar el SELECT final
                    while True:
                        try:
                            temp_result = cursor.fetchone()
                            if temp_result:
                                result = temp_result
                            # Intentar pasar al siguiente resultset si existe
                            if not cursor.nextset():
                                break
                        except pyodbc.ProgrammingError:
                            # No hay más resultsets
                            break
                except Exception:
                    pass
                
                conn.commit()
                
                if result:
                    success = result[0] == 'TRUE' if result else False
                    message = result[1] if result and len(result) > 1 else 'Operación exitosa'
                    return {'success': success, 'message': message}
                else:
                    return {'success': True, 'message': 'Operación exitosa'}
            
            # mquery 5: CONSULTA (con paginación)
            elif mquery == 5:
                results = cursor.fetchall()
                if not results:
                    return {'success': True, 'data': [], 'total': 0}
                
                data = [dict(zip([column[0] for column in cursor.description], row)) 
                       for row in results]
                
                return {'success': True, 'data': data}
            
            # mquery 6: COUNT
            elif mquery == 6:
                result = cursor.fetchone()
                total = result[0] if result else 0
                return {'success': True, 'total': total}
            
            # mquery 4: SELECT (obtener un registro específico)
            elif mquery == 4:
                result = cursor.fetchone()
                if result:
                    data = dict(zip([column[0] for column in cursor.description], result))
                    return {'success': True, 'data': data}
                return {'success': False, 'message': 'Registro no encontrado'}
            
        except Exception as e:
            if conn:
                conn.rollback()
            return {'success': False, 'message': str(e)}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def create_horario(data, current_user, remote_addr):
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return EmpHorario.execute_sp(1, data)  # mquery = 1 (INSERT)

    @staticmethod
    def update_horario(data, current_user, remote_addr):
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return EmpHorario.execute_sp(2, data)  # mquery = 2 (UPDATE)

    @staticmethod
    def delete_horario(idEmpHorario):
        return EmpHorario.execute_sp(3, {'idEmpHorario': idEmpHorario})  # mquery = 3 (DELETE)

    @staticmethod
    def get_horario_by_id(idEmpHorario):
        """Obtiene un horario específico por ID"""
        return EmpHorario.execute_sp(4, {'idEmpHorario': idEmpHorario})  # mquery = 4 (SELECT)
    
    @staticmethod
    def get_horario(idEmpleado):
        """Obtiene los horarios de un empleado (sin paginación)"""
        return EmpHorario.execute_sp(5, {
            'idEmpleado': idEmpleado,
            'inicio': 0,
            'final': 0
        })

    @staticmethod
    def list_horarios(filtros=None):
        """Lista horarios con paginación"""
        filtros = filtros or {}
        
        # Obtener parámetros de paginación
        current_page = filtros.get('current_page', 1)
        per_page = filtros.get('per_page', 10)
        
        # Calcular inicio y fin para la paginación
        inicio = (current_page - 1) * per_page + 1
        final = current_page * per_page
        
        filtros['inicio'] = inicio
        filtros['final'] = final
        
        # Obtener datos con paginación (mquery = 5)
        data_result = EmpHorario.execute_sp(5, filtros)
        
        # Obtener total de registros (mquery = 6)
        count_result = EmpHorario.execute_sp(6, filtros)
        total = count_result.get('total', 0)
        
        # Calcular paginación
        import math
        last_page = math.ceil(total / per_page) if per_page > 0 else 1
        
        return {
            'success': True,
            'data': data_result.get('data', []),
            'pagination': {
                'current_page': current_page,
                'last_page': last_page,
                'per_page': per_page,
                'total': total
            }
        }