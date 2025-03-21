import pyodbc
import re
from config import get_db_connection
from ..utils.auditv2 import AuditFieldsv2

class ConfiguracionesModel:
    SP_NAME = "[contenedor].[sp_configuraciones]"
    ACTIONS = {
        "create": 1,
        "update": 2,
        "list": 3,
        "delete": 4
    }
    
    # Mapeo de columnas para cada tipo de consulta
    COLUMN_MAPPINGS = {
        "list": [
            'id', 'configuracion_id', 'clave', 'valor', 'estado', 'fecha_registro', 'estacion_registro', 'operador_registro',
            'fecha_modificacion', 'estacion_modificacion', 'operador_modificacion', 'unidad', 'current_page', 
            'last_page', 'per_page', 'total'
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
            query = f"EXEC {ConfiguracionesModel.SP_NAME} {', '.join(sp_params)}"
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
            
        column_mapping = ConfiguracionesModel.COLUMN_MAPPINGS.get(action_type, [])
        if not column_mapping:
            return result_rows
            
        return [
            {column_mapping[i]: value for i, value in enumerate(row) if i < len(column_mapping)}
            for row in result_rows
        ]
    
    @staticmethod
    def create_configuracion(data, current_user, remote_addr):
        data = ConfiguracionesModel._prepare_audit_data(data, current_user, remote_addr)
        
        params = {
            'configuracion_id': data['configuracion_id'], 
            'clave': data['clave'], 
            'valor': data['valor'], 
            'estado': data['estado'], 
            'fecha_registro': data['fecha_registro'],  # Nueva fecha de registro
            'estacion_registro': data['estacion_registro'],  # Nueva estación de registro
            'operador_registro': data['operador_registro'],  # Nuevo operador de registro
            'fecha_modificacion': data['fecha_modificacion'],  # Nueva fecha de modificación
            'estacion_modificacion': data['estacion_modificacion'],  # Nueva estación de modificación
            'operador_modificacion': data['operador_modificacion'],  # Nuevo operador de modificación
            'unidad': data['unidad']
        }
        
        result = ConfiguracionesModel._execute_sp(
            ConfiguracionesModel.ACTIONS["create"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Configuración registrada con éxito')

    @staticmethod
    def update_configuracion(data, current_user, remote_addr):
        data = ConfiguracionesModel._prepare_audit_data(data, current_user, remote_addr)
        
        params = {
            'id': data['id'],
            'configuracion_id': data['configuracion_id'], 
            'clave': data['clave'], 
            'valor': data['valor'], 
            'estado': data['estado'], 
            'fecha_modificacion': data['fecha_modificacion'],  # Nueva fecha de modificación
            'estacion_modificacion': data['estacion_modificacion'],  # Nueva estación de modificación
            'operador_modificacion': data['operador_modificacion'],  # Nuevo operador de modificación
            'unidad': data['unidad']
        }
        
        result = ConfiguracionesModel._execute_sp(
            ConfiguracionesModel.ACTIONS["update"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Configuración actualizada con éxito')

    @staticmethod
    def get_configuraciones_filter(filtros, current_page, per_page):
        params = {
            'configuracion_id': filtros.get('configuracion_id', None),
            'clave': filtros.get('clave', None),
            'valor': filtros.get('valor', None),
            'estado': filtros.get('estado', None),
            'current_page': current_page,
            'per_page': per_page
        }
        
        result = ConfiguracionesModel._execute_sp(
            ConfiguracionesModel.ACTIONS["list"], 
            params,
            fetch=True
        )
        
        return ConfiguracionesModel._map_result_to_dict(result, "list")

    @staticmethod
    def delete_configuracion(id, current_user, remote_addr):
        params = {
            'id': id
        }
        
        result = ConfiguracionesModel._execute_sp(
            ConfiguracionesModel.ACTIONS["delete"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Configuración eliminada con éxito')
