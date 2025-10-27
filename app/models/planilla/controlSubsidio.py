import pyodbc
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class ControlSubsidioModel:
    @staticmethod
    def execute_sp(mquery, params):
        conn = get_db_connection()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SET NOCOUNT ON")
            
            cursor.execute('''
                EXEC [dbo].[sp_control_subsidios]
                    @mquery = ?,
                    @idEmpSubsidios = ?,
                    @idConcepto = ?,
                    @idEmpleado = ?,
                    @nro_cit = ?,
                    @fechaInicio = ?,
                    @fechaFin = ?,
                    @observaciones = ?,
                    @estado = ?,
                    @fecha = ?,
                    @estacion = ?,
                    @operador = ?,
                    @flag_estado = ?,
                    @idCentroCosto = ?,
                    @dni = ?,
                    @nombre_completo = ?,
                    @inicio = ?,
                    @final = ?,
                    @idEstado = ?,
                    @fechaDesde = ?,
                    @fechaHasta = ?,
                    @idCondicionLaboral = ?,
                    @idCargo = ?,
                    @mes = ?,
                    @anio = ?,
                    @tipoSubsidio = ?
            ''', (
                mquery,
                params.get('idEmpSubsidios', 0),
                params.get('idConcepto', 0),
                params.get('idEmpleado', 0),
                params.get('nro_cit', ''),
                params.get('fechaInicio', '1900-01-01'),
                params.get('fechaFin', None),
                params.get('observaciones', ''),
                params.get('estado', 0),
                params.get('fecha', '1900-01-01'),
                params.get('estacion', ''),
                params.get('operador', ''),
                params.get('flag_estado', 0),
                params.get('idCentroCosto', 0),
                params.get('dni', ''),
                params.get('nombre_completo', ''),
                max(1, params.get('inicio', 1)),
                max(1, params.get('final', 10)),
                params.get('idEstado', 0),
                params.get('fechaDesde', None),
                params.get('fechaHasta', None),
                params.get('idCondicionLaboral', 0),
                params.get('idCargo', 0),
                params.get('mes', 0),
                params.get('anio', 0),
                params.get('tipoSubsidio', 0)
            ))

            if mquery in [2]:  # UPDATE (actualizar estado)
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
                
            else:  # Para SELECT (4, 5, 6)
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
    def update_estado_subsidio(idEmpSubsidios, estado, current_user, remote_addr):
        """
        Actualizar el estado de un subsidio - @mquery = 2
        Estados:
        0 = No atendido
        1 = Atendido
        2 = Proceso judicial
        3 = Perdido
        4 = Por cobrar
        """
        data = {
            'idEmpSubsidios': idEmpSubsidios,
            'estado': estado
        }
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        result = ControlSubsidioModel.execute_sp(2, data)
        return result['success'], result.get('message', 'Error al actualizar estado del subsidio')

    @staticmethod
    def get_subsidio_by_id(idEmpSubsidios):
        """Obtener un subsidio por ID - @mquery = 4"""
        result = ControlSubsidioModel.execute_sp(4, {'idEmpSubsidios': idEmpSubsidios})
        return result

    @staticmethod
    def list_subsidios(filters=None, page=1, per_page=10):
        """
        Listar subsidios con filtros y paginación - @mquery = 5
        Filtros disponibles:
        - idCentroCosto: int
        - dni: str
        - nombre_completo: str
        - estado: int (0=No atendido, 1=Atendido, 2=Proc.Judicial, 3=Perdido, 4=Por cobrar)
        - fechaDesde: datetime
        - fechaHasta: datetime
        """
        if filters is None:
            filters = {}
        
        params = {
            'inicio': page,
            'final': per_page,
            'idCentroCosto': filters.get('idCentroCosto', 0),
            'dni': filters.get('dni', ''),
            'nombre_completo': filters.get('nombre_completo', ''),
            'estado': filters.get('estado', -1),  # -1 para traer todos
            'fechaDesde': filters.get('fechaDesde', None),
            'fechaHasta': filters.get('fechaHasta', None),
            'idCondicionLaboral': filters.get('idCondicionLaboral', 0),
            'idCargo': filters.get('idCargo', 0),
            'mes': filters.get('mes', 0),
            'anio': filters.get('anio', 0)
        }
        
        result = ControlSubsidioModel.execute_sp(5, params)
        return result

    @staticmethod
    def count_subsidios(filters=None):
        """Contar subsidios con filtros - @mquery = 6"""
        if filters is None:
            filters = {}
        
        params = {
            'idCentroCosto': filters.get('idCentroCosto', 0),
            'dni': filters.get('dni', ''),
            'nombre_completo': filters.get('nombre_completo', ''),
            'estado': filters.get('estado', -1)
        }
        
        result = ControlSubsidioModel.execute_sp(6, params)
        return result