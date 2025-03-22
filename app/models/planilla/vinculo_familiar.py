import pyodbc
import re
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class VinculoFamiliarModel:
    SP_NAME = "[dbo].[sp_vinculo_familiar]"
    ACTIONS = {
        "create": 1,
        "update": 2,
        "list": 3,
        "change_status": 4,
        "delete": 5,
    }
    
    # Column mappings for each action
    COLUMN_MAPPINGS = {
        "list": [
            'idVinculo', 'vinculo', 'fecha_registro', 'estacion_registro',
            'operador_registro', 'fecha_modificacion', 'estacion_modificacion',
            'operador_modificacion', 'current_page', 'last_page', 'per_page', 'total'
        ],
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
            query = f"EXEC {VinculoFamiliarModel.SP_NAME} {', '.join(sp_params)}"
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
            
        column_mapping = VinculoFamiliarModel.COLUMN_MAPPINGS.get(action_type, [])
        if not column_mapping:
            return result_rows
            
        return [
            {column_mapping[i]: value for i, value in enumerate(row) if i < len(column_mapping)}
            for row in result_rows
        ]
    
    @staticmethod
    def create_vinculo_familiar(data, current_user, remote_addr):
        data = VinculoFamiliarModel._prepare_audit_data(data, current_user, remote_addr)
        
        params = {
            'vinculo': data['vinculo'], 
            'fecha_registro': data['fecha_registro'],
            'estacion_registro': data['estacion_registro'],
            'operador_registro': data['operador_registro'],
            'fecha_modificacion': data['fecha_modificacion'],
            'estacion_modificacion': data['estacion_modificacion'],
            'operador_modificacion': data['operador_modificacion']
        }
        
        result = VinculoFamiliarModel._execute_sp(
            VinculoFamiliarModel.ACTIONS["create"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Vinculo familiar registrado con éxito')

    @staticmethod
    def update_vinculo_familiar(data, current_user, remote_addr):
        data = VinculoFamiliarModel._prepare_audit_data(data, current_user, remote_addr)
        
        params = {
            'idVinculo': data['idVinculo'], 
            'vinculo': data['vinculo'], 
            'fecha_modificacion': data['fecha_modificacion'],
            'estacion_modificacion': data['estacion_modificacion'],
            'operador_modificacion': data['operador_modificacion']
        }
        
        result = VinculoFamiliarModel._execute_sp(
            VinculoFamiliarModel.ACTIONS["update"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Vinculo familiar actualizado con éxito')

    @staticmethod
    def get_vinculos_familiares_filter(filtros, current_page, per_page):
        params = {
            'vinculo': filtros.get('vinculo', None),
            'current_page': current_page,
            'per_page': per_page
        }
        
        result = VinculoFamiliarModel._execute_sp(
            VinculoFamiliarModel.ACTIONS["list"], 
            params,
            fetch=True
        )
        
        return VinculoFamiliarModel._map_result_to_dict(result, "list")

    @staticmethod
    def change_vinculo_familiar_status(id, estado, current_user, remote_addr):
        params = {
            'idVinculo': id,
        }
        
        result = VinculoFamiliarModel._execute_sp(
            VinculoFamiliarModel.ACTIONS["change_status"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Estado del vínculo familiar actualizado con éxito')

    @staticmethod
    def delete_vinculo_familiar(id, current_user, remote_addr):
        params = {
            'idVinculo': id
        }
        
        result = VinculoFamiliarModel._execute_sp(
            VinculoFamiliarModel.ACTIONS["delete"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Vinculo familiar eliminado con éxito')
