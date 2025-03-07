import pyodbc
import re
from config import get_db_connection
from ..utils.auditv2 import AuditFieldsv2

class ComposicionFamiliarModel:
    SP_NAME = "[dbo].[sp_composicion_familiar]"
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
            'id', 'idEmpleado', 'apellido_paterno', 'apellido_materno', 'nombres',
            'fecha_nacimiento', 'idVinculo', 'idEstadoCivil', 'ocupacion',
            'fecha_registro', 'estacion_registro', 'operador_registro', 
            'fecha_modificacion', 'estacion_modificacion', 'operador_modificacion',
            'current_page', 'last_page', 'per_page', 'total','otro','vinculo_nombre','estadocivil_nombre'
        ],
        "list_active": [
            'id', 'idEmpleado', 'apellido_paterno', 'apellido_materno', 'nombres',
            'fecha_nacimiento', 'idVinculo', 'idEstadoCivil', 'ocupacion',
            'fecha_registro', 'estacion_registro', 'operador_registro', 
            'fecha_modificacion', 'estacion_modificacion', 'operador_modificacion'
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
            query = f"EXEC {ComposicionFamiliarModel.SP_NAME} {', '.join(sp_params)}"
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
            
        column_mapping = ComposicionFamiliarModel.COLUMN_MAPPINGS.get(action_type, [])
        if not column_mapping:
            return result_rows
            
        return [
            {column_mapping[i]: value for i, value in enumerate(row) if i < len(column_mapping)}
            for row in result_rows
        ]
    
    @staticmethod
    def create_composicion_familiar(data, current_user, remote_addr):
        data = ComposicionFamiliarModel._prepare_audit_data(data, current_user, remote_addr)
        
        params = {
            'idEmpleado': data['idEmpleado'],
            'apellido_paterno': data['apellido_paterno'],
            'apellido_materno': data['apellido_materno'],
            'nombres': data['nombres'],
            'fecha_nacimiento': data['fecha_nacimiento'],
            'idVinculo': data['idVinculo'],
            'idEstadoCivil': data['idEstadoCivil'],
            'ocupacion': data['ocupacion'],
            'fecha_registro': data['fecha_registro'],
            'estacion_registro': data['estacion_registro'],
            'operador_registro': data['operador_registro'],
            'fecha_modificacion': data['fecha_modificacion'],
            'estacion_modificacion': data['estacion_modificacion'],
            'operador_modificacion': data['operador_modificacion']
        }
        
        result = ComposicionFamiliarModel._execute_sp(
            ComposicionFamiliarModel.ACTIONS["create"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Composición familiar registrada con éxito')

    @staticmethod
    def update_composicion_familiar(data, current_user, remote_addr):
        data = ComposicionFamiliarModel._prepare_audit_data(data, current_user, remote_addr)
        
        params = {
            'id': data['id'],
            'idEmpleado': data['idEmpleado'],
            'apellido_paterno': data['apellido_paterno'],
            'apellido_materno': data['apellido_materno'],
            'nombres': data['nombres'],
            'fecha_nacimiento': data['fecha_nacimiento'],
            'idVinculo': data['idVinculo'],
            'idEstadoCivil': data['idEstadoCivil'],
            'ocupacion': data['ocupacion'],
            'fecha_modificacion': data['fecha_modificacion'],
            'estacion_modificacion': data['estacion_modificacion'],
            'operador_modificacion': data['operador_modificacion']
        }
        
        result = ComposicionFamiliarModel._execute_sp(
            ComposicionFamiliarModel.ACTIONS["update"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Composición familiar actualizada con éxito')

    @staticmethod
    def get_composiciones_familiares_filter(filtros, current_page, per_page):
        params = {
            'idEmpleado': filtros.get('idEmpleado', None),
            'apellido_paterno': filtros.get('apellido_paterno', None),
            'apellido_materno': filtros.get('apellido_materno', None),
            'nombres': filtros.get('nombres', None),
            'estado': filtros.get('estado', None),
            'current_page': current_page,
            'per_page': per_page
        }
        
        result = ComposicionFamiliarModel._execute_sp(
            ComposicionFamiliarModel.ACTIONS["list"], 
            params,
            fetch=True
        )
        
        return ComposicionFamiliarModel._map_result_to_dict(result, "list")

    @staticmethod
    def change_composicion_familiar_status(id, estado, current_user, remote_addr):
        params = {
            'id': id,
            'estado': estado
        }
        
        result = ComposicionFamiliarModel._execute_sp(
            ComposicionFamiliarModel.ACTIONS["change_status"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Estado de la composición familiar actualizado con éxito')

    @staticmethod
    def delete_composicion_familiar(id, current_user, remote_addr):
        params = {
            'id': id
        }
        
        result = ComposicionFamiliarModel._execute_sp(
            ComposicionFamiliarModel.ACTIONS["delete"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Composición familiar eliminada con éxito')

    @staticmethod
    def get_active_composiciones_familiares():
        result = ComposicionFamiliarModel._execute_sp(
            ComposicionFamiliarModel.ACTIONS["list_active"],
            fetch=True
        )
        
        return ComposicionFamiliarModel._map_result_to_dict(result, "list_active")
