import pyodbc
import re
from config import get_db_connection
class ReporteModel:
    # Mapeo de plantillas a procedimientos
    plantilla_to_procedure = {
        'default.html': 'sp_GenerarReporte',
        'orden_servicio.html': 'sp_GenerarReporte',
        'plantilla3.html': 'sp_GenerarReporte3',
        # Puedes seguir agregando más plantillas y procedimientos aquí
    }

    @staticmethod
    def ejecutar_procedimiento_reporte(parametros, plantilla_nombre):
        """
        Ejecuta un procedimiento almacenado basado en la plantilla
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Determinar el procedimiento almacenado basado en la plantilla
            procedimiento = ReporteModel.plantilla_to_procedure.get(plantilla_nombre)
            
            if not procedimiento:
                raise Exception(f"No hay procedimiento definido para la plantilla {plantilla_nombre}")
            
            # Preparar los parámetros para el procedimiento
            params = []
            param_placeholders = []
            
            # Excluir parámetros específicos si es necesario
            excluded_params = ['plantilla', 'version']
            
            for key, value in parametros.items():
                if key not in excluded_params:
                    params.append(value)
                    param_placeholders.append(f"@{key} = ?")
            
            # Construir la llamada al procedimiento
            proc_call = f"EXEC [dbo].[{procedimiento}] {', '.join(param_placeholders)}"
            
            # Ejecutar el procedimiento
            cursor.execute(proc_call, params)
            
            # Obtener los resultados
            columns = [column[0] for column in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return True, results
            
        except pyodbc.Error as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            error_detail = matches.group(1).strip() if matches else 'Error al ejecutar procedimiento'
            return False, error_detail
            
        finally:
            conn.close()
