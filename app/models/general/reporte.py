import pyodbc
import re
from config import get_db_connection

class ReporteModel:
    # Mapeo de plantillas a procedimientos
    plantilla_to_procedure = {
        'default.html': 'sp_GenerarReporte',
        'orden_servicio.html': 'sp_GenerarReporte',
        'plantilla3.html': 'sp_GenerarReporte3',
        'reporte_orden_servicio.html':'Terceros.sp_orden_servicio_reporte',
        'reporte_orden_servicio_sexo.html':'Terceros.sp_orden_servicio_reporte',
        'reporte_orden_servicio_distrito.html':'Terceros.sp_orden_servicio_reporte',
        'reporte_locadores.html':'Locadores.sp_registro_locadores_reporte',
        'reporte_terceros.html':'Locadores.sp_control_contrato',
        'reporte_terceros_sexo.html':'Locadores.sp_control_contrato',
        'reporte_terceros_distrito.html':'Locadores.sp_control_contrato',
        'reporte_papeletas_rrhh.html':'sp_papeleta_rrhh',
        'reporte_marcaciones.html':'SP_MARCACIONES',
        'reporte_asistencias.html':'sp_asistencias2',
    }

    @staticmethod
    def ejecutar_procedimiento_reporte(parametros, plantilla_nombre):
        """
        Ejecuta un procedimiento almacenado basado en la plantilla
        Maneja múltiples tablas de resultados
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
            proc_call = f"EXEC {procedimiento} {', '.join(param_placeholders)}"
            print(f"Ejecutando: {proc_call}")
            
            # Ejecutar el procedimiento
            cursor.execute(proc_call, params)
            
            # Capturar múltiples tablas de resultados
            all_results = []
            table_index = 0
            
            while True:
                # Obtener columnas de la tabla actual
                if cursor.description:
                    columns = [column[0] for column in cursor.description]
                    results = []
                    
                    # Obtener todas las filas de la tabla actual
                    for row in cursor.fetchall():
                        results.append(dict(zip(columns, row)))
                    
                    all_results.append({
                        'table_index': table_index,
                        'table_name': f'table_{table_index}',
                        'columns': columns,
                        'data': results,
                        'row_count': len(results)
                    })
                    
                    table_index += 1
                    print(f"Tabla {table_index - 1} procesada: {len(results)} filas")
                
                # Intentar avanzar al siguiente conjunto de resultados
                if not cursor.nextset():
                    break
            
            # Si no hay resultados, devolver estructura vacía
            if not all_results:
                all_results = [{
                    'table_index': 0,
                    'table_name': 'table_0',
                    'columns': [],
                    'data': [],
                    'row_count': 0
                }]
            
            print(f"Total de tablas procesadas: {len(all_results)}")
            return True, all_results
            
        except pyodbc.Error as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            error_detail = matches.group(1).strip() if matches else 'Error al ejecutar procedimiento'
            return False, error_detail
            
        finally:
            conn.close()
    
    @staticmethod
    def ejecutar_procedimiento_reporte_excel(parametros, procedure_name):
        """
        Ejecuta un procedimiento almacenado con parámetros dinámicos
        Maneja múltiples tablas de resultados para Excel
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()

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
            proc_call = f"EXEC {procedure_name} {', '.join(param_placeholders)}"
            print(f"Ejecutando Excel: {proc_call}")
            
            # Ejecutar el procedimiento
            cursor.execute(proc_call, params)

            # Capturar múltiples tablas de resultados
            all_results = []
            table_index = 0
            
            while True:
                # Obtener columnas de la tabla actual
                if cursor.description:
                    columns = [column[0] for column in cursor.description]
                    results = []
                    
                    # Obtener todas las filas de la tabla actual
                    for row in cursor.fetchall():
                        results.append(dict(zip(columns, row)))
                    
                    all_results.append({
                        'table_index': table_index,
                        'table_name': f'table_{table_index}',
                        'columns': columns,
                        'data': results,
                        'row_count': len(results)
                    })
                    
                    table_index += 1
                    print(f"Tabla Excel {table_index - 1} procesada: {len(results)} filas")
                
                # Intentar avanzar al siguiente conjunto de resultados
                if not cursor.nextset():
                    break
            
            # Si no hay resultados, devolver estructura vacía
            if not all_results:
                all_results = [{
                    'table_index': 0,
                    'table_name': 'table_0',
                    'columns': [],
                    'data': [],
                    'row_count': 0
                }]
            
            print(f"Total de tablas Excel procesadas: {len(all_results)}")
            return True, all_results
            
        except pyodbc.Error as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            error_detail = matches.group(1).strip() if matches else 'Error al ejecutar procedimiento'
            return False, error_detail

        finally:
            conn.close()
    
    @staticmethod
    def ejecutar_procedimiento_reporte_legacy(parametros, plantilla_nombre):
        """
        Método legacy que mantiene la compatibilidad con código existente
        Devuelve solo la primera tabla como antes
        """
        success, results = ReporteModel.ejecutar_procedimiento_reporte(parametros, plantilla_nombre)
        
        if success and results:
            # Retornar solo los datos de la primera tabla para compatibilidad
            return success, results[0]['data']
        
        return success, results