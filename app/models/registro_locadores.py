import pyodbc
import re
from config import get_db_connection
from ..utils.auditv2 import AuditFieldsv2

class RegistroLocadoresModel:
    SP_NAME = "[Locadores].[sp_registro_locadores]"
    ACTIONS = {
        "register": 1,
        "update": 2,
        "list": 3
    }
    
    # Mapeo de columnas para cada tipo de consulta
    COLUMN_MAPPINGS = {
        "list": [
            'id', 'id_datos_personales', 'id_area', 'id_cargo', 'monto', 'tipo', 'fecha', 
            'estado', 'cv_dir', 'otros_dir', 'fecha_registro', 'motivo_reemplazo', 'estacion_registro',
            'operador_registro', 'fecha_modificacion', 'estacion_modificacion', 'operador_modificacion', 
            'current_page', 'last_page', 'per_page', 'total'
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
            query = f"EXEC {RegistroLocadoresModel.SP_NAME} {', '.join(sp_params)}"
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
            
        column_mapping = RegistroLocadoresModel.COLUMN_MAPPINGS.get(action_type, [])
        if not column_mapping:
            return result_rows
            
        return [
            {column_mapping[i]: value for i, value in enumerate(row) if i < len(column_mapping)}
            for row in result_rows
        ]
    
    @staticmethod
    def register_locador(data, current_user, remote_addr):
        data = RegistroLocadoresModel._prepare_audit_data(data, current_user, remote_addr)
        
        params = {
            'id_datos_personales': data['id_datos_personales'],
            'id_area': data['id_area'],
            'id_cargo': data['id_cargo'],
            'tipo': data['tipo'],
            'estado': data['estado'],
            'fecha': data['fecha'],
            'fecha_registro': data['fecha_registro'],
            'estacion_registro': data['estacion_registro'],
            'operador_registro': data['operador_registro']
        }
        
        result = RegistroLocadoresModel._execute_sp(
            RegistroLocadoresModel.ACTIONS["register"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Registro de locador realizado con éxito')

    @staticmethod
    def update_locador(data, current_user, remote_addr):
        data = RegistroLocadoresModel._prepare_audit_data(data, current_user, remote_addr)
        
        params = {
            'id': data['id'],
            'id_datos_personales': data['id_datos_personales'],
            'id_area': data['id_area'],
            'id_cargo': data['id_cargo'],
            'tipo': data['tipo'],
            'estado': data['estado'],
            'fecha': data['fecha'],
            'fecha_modificacion': data['fecha_modificacion'],
            'estacion_modificacion': data['estacion_modificacion'],
            'operador_modificacion': data['operador_modificacion']
        }
        
        result = RegistroLocadoresModel._execute_sp(
            RegistroLocadoresModel.ACTIONS["update"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Registro de locador actualizado con éxito')

    @staticmethod
    def get_locadores_by_filter(filtros, current_page, per_page):
        params = {
            'id_datos_personales': filtros.get('id_datos_personales', None),
            'id_area': filtros.get('id_area', None),
            'id_cargo': filtros.get('id_cargo', None),
            'tipo': filtros.get('tipo', None),
            'estado': filtros.get('estado', None),
            'fecha': filtros.get('fecha', None),
            'anio': filtros.get('anio', None),
            'mes': filtros.get('mes', None),
            'current_page': current_page,
            'per_page': per_page
        }
        
        result = RegistroLocadoresModel._execute_sp(
            RegistroLocadoresModel.ACTIONS["list"], 
            params,
            fetch=True
        )
        
        return RegistroLocadoresModel._map_result_to_dict(result, "list")
