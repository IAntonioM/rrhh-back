import pyodbc
import re
from config import get_db_connection
from ..utils.auditv2 import AuditFieldsv2
from ..models.general.datosPersonales import DatosPersonales  # Import DatosPersonales model

class RegistroLocadoresModel:
    SP_NAME = "[Locadores].[sp_registro_locadores]"
    ACTIONS = {
        "register": 1,
        "update": 2,
        "list": 3,
        "list_with_details": 4  # New action for fetching with personal details
    }
    
    COLUMN_MAPPINGS = {
        "list": [
            'id', 'id_datos_personales', 'idCentroCosto', 'id_cargo', 'monto', 'tipo', 'fecha', 
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
    def _map_result_to_dict(result_rows, action_type):
        """Mapea resultados de la consulta a un diccionario usando el mapeo de columnas"""
        if not result_rows:
            return []
            
        column_mapping = RegistroLocadoresModel.COLUMN_MAPPINGS.get(action_type, [])
        if not column_mapping:
            return result_rows
            
        return [
            {column_mapping[i]: value for i, value in enumerate(row) if i < len(column_mapping)}
            for row in result_rows
        ]
    
    @staticmethod
    def get_locadores_with_personal_details(filtros=None, current_page=1, per_page=10):
        """
        Retrieves locadores records with associated personal details
        
        Args:
            filtros (dict, optional): Filters for locadores
            current_page (int, optional): Current page number for pagination
            per_page (int, optional): Number of records per page
        
        Returns:
            dict: Dictionary containing locadores records, pagination info
        """
        # Usar valores predeterminados si no se proporcionan filtros
        filtros = filtros or {}
        
        params = {
            'id_datos_personales': filtros.get('id_datos_personales'),
            'idCentroCosto': filtros.get('idCentroCosto'),
            'id_cargo': filtros.get('id_cargo'),
            'tipo': filtros.get('tipo'),
            'estado': filtros.get('estado'),
            'fecha': filtros.get('fecha'),
            'anio': filtros.get('anio'),
            'mes': filtros.get('mes'),
            'current_page': current_page,
            'per_page': per_page
        }
        
        # Fetch locadores records
        locadores_result = RegistroLocadoresModel._execute_sp(
            RegistroLocadoresModel.ACTIONS["list"], 
            params,
            fetch=True
        )
        
        # Check if result is a tuple (error case)
        if isinstance(locadores_result, tuple):
            return {
                'success': False,
                'message': locadores_result[1] if len(locadores_result) > 1 else 'Error desconocido'
            }
        
        # Map locadores results
        mapped_locadores = RegistroLocadoresModel._map_result_to_dict(locadores_result, "list")
        
        # Fetch personal details for each record
        for locador in mapped_locadores:
            # Fetch personal details using the id_datos_personales
            personal_details_filter = {'idDatosPersonales': locador['id_datos_personales']}
            personal_details_result = DatosPersonales.list_datos_personales(personal_details_filter)
            
            # Add personal details to the locador record
            locador['datos_personales'] = (
                personal_details_result.get('data', [{}])[0] 
                if personal_details_result and 'data' in personal_details_result 
                else {}
            )
        
        # Prepare return dictionary with pagination info
        return {
            'success': True,
            'data': mapped_locadores,
            'pagination': {
                'current_page': current_page,
                'per_page': per_page,
                'total': len(mapped_locadores)
            }
        }
    
    
    @staticmethod
    def _prepare_audit_data(data, current_user, remote_addr):
        """Prepara los datos con campos de auditoría"""
        return AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
    
    @staticmethod
    def register_locador(data, current_user, remote_addr):
        data = RegistroLocadoresModel._prepare_audit_data(data, current_user, remote_addr)
        
        params = {
            'id_datos_personales': data['id_datos_personales'],
            'idCentroCosto': data['idCentroCosto'],
            'id_cargo': data['id_cargo'],
            'tipo': data['tipo'],
            'monto': data['monto'],
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
            'idCentroCosto': data['idCentroCosto'],
            'id_cargo': data['id_cargo'],
            'tipo': data['tipo'],
            'monto': data['monto'],
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
            'idCentroCosto': filtros.get('idCentroCosto', None),
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
    
