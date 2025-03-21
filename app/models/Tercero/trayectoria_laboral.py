import pyodbc
import re
from config import get_db_connection
from ..utils.auditv2 import AuditFieldsv2

class TrayectoriaLaboralModel:
    SP_NAME = "[Planilla].[sp_trayectoria_laboral]"
    ACTIONS = {
        "create": 1,
        "update": 2,
        "list": 3,
        "change_status": 4,
        "delete": 5,
        "list_active": 6
    }
    
    # Mapeo de columnas para cada tipo de consulta
    COLUMN_MAPPINGS = {
        "list": [
            'idEmpTrayectoria', 'idEmpleado', 'periodo_inicio', 'periodo_termino',
            'entidad', 'puesto', 'estado', 'fecha_registro', 'estacion_registro',
            'operador_registro', 'fecha_modificacion', 'estacion_modificacion',
            'operador_modificacion', 'current_page', 'last_page', 'per_page', 'total'
        ],
        "list_active": [
            'idEmpTrayectoria', 'idEmpleado', 'periodo_inicio', 'periodo_termino',
            'entidad', 'puesto', 'estado', 'fecha_registro', 'estacion_registro',
            'operador_registro', 'fecha_modificacion', 'estacion_modificacion',
            'operador_modificacion'
        ]
    }
    
    @staticmethod
    def _execute_sp(action, params=None, fetch=False):
        """Método centralizado para ejecutar el procedimiento almacenado"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Preparar los parámetros con la acción
            sp_params = [f"@accion = {action}"]
            param_values = []
            
            # Agregar parámetros adicionales si existen
            if params:
                for key, value in params.items():
                    sp_params.append(f"@{key} = ?")
                    param_values.append(value)
                    
            # Construir y ejecutar la consulta
            query = f"EXEC {TrayectoriaLaboralModel.SP_NAME} {', '.join(sp_params)}"
            cursor.execute(query, param_values)
            
            # Obtener resultados si es necesario
            result = cursor.fetchall() if fetch else None
            
            # Commit si es una operación de escritura
            if not fetch:
                conn.commit()
                return True, "Operación ejecutada con éxito"
            
            return result
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else f'Error al ejecutar la acción {action}'
            
        finally:
            conn.close()
    
    @staticmethod
    def _prepare_audit_data(data, current_user, remote_addr):
        """Prepara los datos con campos de auditoría"""
        return AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
    
    @staticmethod
    def _map_result_to_dict(result_rows, action_type):
        """Mapea resultados de la consulta a un diccionario usando el mapeo de columnas"""
        if not result_rows or isinstance(result_rows, tuple):
            return result_rows
            
        column_mapping = TrayectoriaLaboralModel.COLUMN_MAPPINGS.get(action_type, [])
        if not column_mapping:
            return result_rows
            
        return [
            {column_mapping[i]: value for i, value in enumerate(row) if i < len(column_mapping)}
            for row in result_rows
        ]
    
    @staticmethod
    def create_trayectoria_laboral(data, current_user, remote_addr):
        data = TrayectoriaLaboralModel._prepare_audit_data(data, current_user, remote_addr)
        
        params = {
            'idEmpleado': data['idEmpleado'], 
            'periodo_inicio': data['periodo_inicio'], 
            'periodo_termino': data['periodo_termino'], 
            'entidad': data['entidad'],
            'puesto': data['puesto'], 
            'estado': data['estado'], 
            'fecha_registro': data['fecha_registro'], 
            'estacion_registro': data['estacion_registro'],
            'operador_registro': data['operador_registro'], 
            'fecha_modificacion': data['fecha_modificacion'], 
            'estacion_modificacion': data['estacion_modificacion'],
            'operador_modificacion': data['operador_modificacion']
        }
        
        result = TrayectoriaLaboralModel._execute_sp(
            TrayectoriaLaboralModel.ACTIONS["create"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Trayectoria laboral registrada con éxito')

    @staticmethod
    def update_trayectoria_laboral(data, current_user, remote_addr):
        data = TrayectoriaLaboralModel._prepare_audit_data(data, current_user, remote_addr)
        
        params = {
            'idEmpTrayectoria': data['idEmpTrayectoria'], 
            'idEmpleado': data['idEmpleado'], 
            'periodo_inicio': data['periodo_inicio'], 
            'periodo_termino': data['periodo_termino'],
            'entidad': data['entidad'], 
            'puesto': data['puesto'], 
            'estado': data['estado'], 
            'fecha_modificacion': data['fecha_modificacion'], 
            'estacion_modificacion': data['estacion_modificacion'], 
            'operador_modificacion': data['operador_modificacion']
        }
        
        result = TrayectoriaLaboralModel._execute_sp(
            TrayectoriaLaboralModel.ACTIONS["update"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Trayectoria laboral actualizada con éxito')

    @staticmethod
    def get_trayectorias_laborales_filter(filtros, current_page, per_page):
        params = {
            'idEmpleado': filtros.get('idEmpleado', None),
            'entidad': filtros.get('entidad', None),
            'puesto': filtros.get('puesto', None),
            'estado': filtros.get('estado', None),
            'current_page': current_page,
            'per_page': per_page
        }
        
        result = TrayectoriaLaboralModel._execute_sp(
            TrayectoriaLaboralModel.ACTIONS["list"], 
            params,
            fetch=True
        )
        
        return TrayectoriaLaboralModel._map_result_to_dict(result, "list")

    @staticmethod
    def change_trayectoria_laboral_status(id, estado, current_user, remote_addr):
        params = {
            'idEmpTrayectoria': id,
            'estado': estado
        }
        
        result = TrayectoriaLaboralModel._execute_sp(
            TrayectoriaLaboralModel.ACTIONS["change_status"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Estado de la trayectoria laboral actualizado con éxito')

    @staticmethod
    def delete_trayectoria_laboral(id, current_user, remote_addr):
        params = {
            'idEmpTrayectoria': id
        }
        
        result = TrayectoriaLaboralModel._execute_sp(
            TrayectoriaLaboralModel.ACTIONS["delete"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Trayectoria laboral eliminada con éxito')

    @staticmethod
    def get_active_trayectorias_laborales():
        result = TrayectoriaLaboralModel._execute_sp(
            TrayectoriaLaboralModel.ACTIONS["list_active"],
            fetch=True
        )
        
        return TrayectoriaLaboralModel._map_result_to_dict(result, "list_active")