import pyodbc
import re
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class EstadoCivilModel:
    SP_NAME = "[dbo].[sp_estado_civil]"
    ACTIONS = {
        "create": 1,        # Acción 1: Insertar
        "update": 2,        # Acción 2: Actualizar
        "list": 3,          # Acción 3: Listar
        "change_status": 4, # Acción 4: Cambiar estado
        "delete": 5,        # Acción 5: Eliminar
    }
    
    # Mapeo de columnas para la acción de listado
    COLUMN_MAPPINGS = {
        "list": [
            'idEstadoCivil', 'estadoCivil', 'flag_estado', 'current_page',
            'last_page', 'per_page', 'total'
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
            query = f"EXEC {EstadoCivilModel.SP_NAME} {', '.join(sp_params)}"
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
    def _map_result_to_dict(result_rows, action_type):
        """Mapea resultados de la consulta a un diccionario usando el mapeo de columnas"""
        if not result_rows or isinstance(result_rows, tuple):
            return result_rows
            
        column_mapping = EstadoCivilModel.COLUMN_MAPPINGS.get(action_type, [])
        if not column_mapping:
            return result_rows
            
        return [
            {column_mapping[i]: value for i, value in enumerate(row) if i < len(column_mapping)}
            for row in result_rows
        ]
    
    @staticmethod
    def create_estado_civil(data):
        """Crea un nuevo estado civil en la base de datos"""
        params = {
            'estadoCivil': data['estadoCivil'],
            'flag_estado': data['flag_estado']
        }
        
        result = EstadoCivilModel._execute_sp(
            EstadoCivilModel.ACTIONS["create"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Estado civil registrado con éxito')

    @staticmethod
    def update_estado_civil(data):
        """Actualiza un estado civil existente"""
        params = {
            'id': data['idEstadoCivil'],
            'estadoCivil': data['estadoCivil'],
            'flag_estado': data['flag_estado']
        }
        
        result = EstadoCivilModel._execute_sp(
            EstadoCivilModel.ACTIONS["update"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Estado civil actualizado con éxito')

    @staticmethod
    def get_estado_civiles_filter(filtros, current_page, per_page):
        """Obtiene una lista filtrada de estados civiles"""
        params = {
            'estadoCivil': filtros.get('estadoCivil', None),
            'flag_estado': filtros.get('flag_estado', None),
            'current_page': current_page,
            'per_page': per_page
        }
        
        result = EstadoCivilModel._execute_sp(
            EstadoCivilModel.ACTIONS["list"], 
            params,
            fetch=True
        )
        
        return EstadoCivilModel._map_result_to_dict(result, "list")

    @staticmethod
    def change_estado_civil_status(id, estado):
        """Cambia el estado de un estado civil (activo/inactivo)"""
        params = {
            'id': id,
            'flag_estado': estado
        }
        
        result = EstadoCivilModel._execute_sp(
            EstadoCivilModel.ACTIONS["change_status"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Estado civil actualizado con éxito')

    @staticmethod
    def delete_estado_civil(id):
        """Elimina un estado civil de la base de datos"""
        params = {
            'id': id
        }
        
        result = EstadoCivilModel._execute_sp(
            EstadoCivilModel.ACTIONS["delete"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Estado civil eliminado con éxito')
