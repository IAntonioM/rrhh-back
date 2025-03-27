import pyodbc
import re
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class OrdenServicioModel:
    SP_NAME = "[Terceros].[sp_orden_servicio]"
    ACTIONS = {
        "create": 1,
        "update": 2,
        "list": 3,
        "change_status": 4,
        "delete": 5,
        
    }
    
    # Mapeo de columnas para cada tipo de consulta
    COLUMN_MAPPINGS = {
        "list": [
            'id', 'id_datos_personales', 'id_cargo', 'id_area', 'id_sede', 'id_banco', 'id_meta', 'num_cuenta',
            'descripcion', 'fecha_inicio', 'fecha_termino', 'estado', 
            # Add missing fields to the mapping
            'id_tipo_presupuesto', 'id_proceso_seleccion', 'id_tipo_operacion', 'id_tipo_adquisicion', 
            'id_tipo_consumo', 'numero_certificacion_siga', 'concepto',
            # End of missing fields
            'fecha_registro', 'estacion_registro',
            'operador_registro', 'fecha_modificacion', 'estacion_modificacion', 'operador_modificacion', 
            'num_servicio', 'id_estado_servicio', 'cuadro_adq', 'nro_proc_select', 'id_orden_recepcion', 
            'fecha_recepcion', 'numero_contrato', 'fecha_contrato', 'doc_siaf', 'resumen_adq', 'id_concepto', 
            'justificacion_compra', 'id_osce', 'contenido_osce', 'id_moneda', 'tipo_cambio', 'igv_estado',
            'fecha_orden', 'fecha_mejor_pago', 'num_cert_siga', 'monto', 
            'MES', 'DIA', 'anio', 'DNI', 'proveedor_nombres',
            # New fields
            'centroCosto_nombre', 'cargo_nombre', 'concepto_servicio', 'estado_os',
            # Pagination info
            'current_page', 'last_page', 'per_page', 'total'
        ],
        "list_active": [
            'id', 'id_datos_personales', 'id_cargo', 'id_area', 'id_sede', 'id_banco', 'id_meta', 'num_cuenta',
            'descripcion', 'fecha_inicio', 'fecha_termino', 'estado', 
            # Add missing fields to the mapping
            'id_tipo_presupuesto', 'id_proceso_seleccion', 'id_tipo_operacion', 'id_tipo_adquisicion', 
            'id_tipo_consumo', 'numero_certificacion_siga', 'concepto',
            # End of missing fields
            'fecha_registro', 'estacion_registro',
            'operador_registro', 'fecha_modificacion', 'estacion_modificacion', 'operador_modificacion', 
            'num_servicio', 'id_estado_servicio', 'cuadro_adq', 'nro_proc_select', 'id_orden_recepcion', 
            'fecha_recepcion', 'numero_contrato', 'fecha_contrato', 'doc_siaf', 'resumen_adq', 'id_concepto', 
            'justificacion_compra', 'id_osce', 'contenido_osce', 'id_moneda', 'tipo_cambio', 'igv_estado',
            'fecha_orden', 'fecha_mejor_pago', 'num_cert_siga', 'monto','proovedor_nombres'
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
            query = f"EXEC {OrdenServicioModel.SP_NAME} {', '.join(sp_params)}"
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
            
        column_mapping = OrdenServicioModel.COLUMN_MAPPINGS.get(action_type, [])
        if not column_mapping:
            return result_rows
            
        return [
            {column_mapping[i]: value for i, value in enumerate(row) if i < len(column_mapping)}
            for row in result_rows
        ]
    
    @staticmethod
    def create_orden_servicio(data, current_user, remote_addr):
        data = OrdenServicioModel._prepare_audit_data(data, current_user, remote_addr)
        
        params = {
            'id_datos_personales': data['id_datos_personales'], 
            'id_cargo': data.get('id_cargo'),
            'id_area': data.get('id_area'),
            'id_sede': data.get('id_sede'),
            'id_banco': data.get('id_banco'),
            'id_meta': data.get('id_meta'),
            'num_cuenta': data.get('num_cuenta'),
            'descripcion': data.get('descripcion'),
            'fecha_inicio': data.get('fecha_inicio'),
            'fecha_termino': data.get('fecha_termino'),
            'estado': data.get('estado'),
            # Adding missing parameters
            'id_tipo_presupuesto': data.get('id_tipo_presupuesto'),
            'id_proceso_seleccion': data.get('id_proceso_seleccion'),
            'id_tipo_operacion': data.get('id_tipo_operacion'),
            'id_tipo_adquisicion': data.get('id_tipo_adquisicion'),
            'id_tipo_consumo': data.get('id_tipo_consumo'),
            'numero_certificacion_siga': data.get('numero_certificacion_siga'),
            'concepto': data.get('concepto'),
            # End of missing parameters
            'fecha_registro': data.get('fecha_registro'),
            'estacion_registro': data.get('estacion_registro'),
            'operador_registro': data.get('operador_registro'),
            'fecha_modificacion': data.get('fecha_modificacion'),
            'estacion_modificacion': data.get('estacion_modificacion'),
            'operador_modificacion': data.get('operador_modificacion'),
            'num_servicio': data.get('num_servicio'),
            'id_estado_servicio': data.get('id_estado_servicio'),
            'cuadro_adq': data.get('cuadro_adq'),
            'nro_proc_select': data.get('nro_proc_select'),
            'id_orden_recepcion': data.get('id_orden_recepcion'),
            'fecha_recepcion': data.get('fecha_recepcion'),
            'numero_contrato': data.get('numero_contrato'),
            'fecha_contrato': data.get('fecha_contrato'),
            'doc_siaf': data.get('doc_siaf'),
            'resumen_adq': data.get('resumen_adq'),
            'id_concepto': data.get('id_concepto'),
            'justificacion_compra': data.get('justificacion_compra'),
            'id_osce': data.get('id_osce'),
            'contenido_osce': data.get('contenido_osce'),
            'id_moneda': data.get('id_moneda'),
            'tipo_cambio': data.get('tipo_cambio'),
            'igv_estado': data.get('igv_estado'),
            'fecha_orden': data.get('fecha_orden'),
            'fecha_mejor_pago': data.get('fecha_mejor_pago'),
            'num_cert_siga': data.get('num_cert_siga'),
            'monto': data.get('monto')
        }
        
        result = OrdenServicioModel._execute_sp(
            OrdenServicioModel.ACTIONS["create"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Orden de servicio registrada con éxito')

    @staticmethod
    def update_orden_servicio(data, current_user, remote_addr):
        data = OrdenServicioModel._prepare_audit_data(data, current_user, remote_addr)
    
        params = {
            'id': data['id'],  # Este es obligatorio, es el ID de la orden de servicio
            'id_datos_personales': data['id_datos_personales'], 
            'id_cargo': data.get('id_cargo'),
            'id_area': data.get('id_area'),
            'id_sede': data.get('id_sede'),
            'id_banco': data.get('id_banco'),
            'id_meta': data.get('id_meta'),
            'num_cuenta': data.get('num_cuenta'),
            'descripcion': data.get('descripcion'),
            'fecha_inicio': data.get('fecha_inicio'),
            'fecha_termino': data.get('fecha_termino'),
            'estado': data.get('estado'),  # Si se quiere actualizar el estado, se mantiene
            'id_tipo_presupuesto': data.get('id_tipo_presupuesto'),
            'id_proceso_seleccion': data.get('id_proceso_seleccion'),
            'id_tipo_operacion': data.get('id_tipo_operacion'),
            'id_tipo_adquisicion': data.get('id_tipo_adquisicion'),
            'id_tipo_consumo': data.get('id_tipo_consumo'),
            'numero_certificacion_siga': data.get('numero_certificacion_siga'),
            'concepto': data.get('concepto'),
            
            # Campos adicionales
            'fecha_modificacion': data.get('fecha_modificacion'),
            'estacion_modificacion': data.get('estacion_modificacion'),
            'operador_modificacion': data.get('operador_modificacion'),
            
            'num_servicio': data.get('num_servicio'),
            'id_estado_servicio': data.get('id_estado_servicio'),
            'cuadro_adq': data.get('cuadro_adq'),
            'nro_proc_select': data.get('nro_proc_select'),
            'id_orden_recepcion': data.get('id_orden_recepcion'),
            'fecha_recepcion': data.get('fecha_recepcion'),
            'numero_contrato': data.get('numero_contrato'),
            'fecha_contrato': data.get('fecha_contrato'),
            'doc_siaf': data.get('doc_siaf'),
            'resumen_adq': data.get('resumen_adq'),
            'id_concepto': data.get('id_concepto'),
            'justificacion_compra': data.get('justificacion_compra'),
            'id_osce': data.get('id_osce'),
            'contenido_osce': data.get('contenido_osce'),
            'id_moneda': data.get('id_moneda'),
            'tipo_cambio': data.get('tipo_cambio'),
            'igv_estado': data.get('igv_estado'),
            'fecha_orden': data.get('fecha_orden'),
            'fecha_mejor_pago': data.get('fecha_mejor_pago'),
            'num_cert_siga': data.get('num_cert_siga'),
            'monto': data.get('monto')
        }
        
        result = OrdenServicioModel._execute_sp(
            OrdenServicioModel.ACTIONS["update"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Orden de servicio actualizada con éxito')


    @staticmethod
    def get_ordenes_servicio_filter(filtros, current_page, per_page):
        params = {
            'num_servicio': filtros.get('num_servicio', None),
            'fecha_orden': filtros.get('fecha_orden', None),
            'id_datos_personales': filtros.get('id_datos_personales', None),
            'id_estado_servicio': filtros.get('id_estado_servicio', None),
            'estado': filtros.get('estado', None),
            # Añadir filtros existentes adicionales
            'id_tipo_presupuesto': filtros.get('id_tipo_presupuesto', None),
            'id_proceso_seleccion': filtros.get('id_proceso_seleccion', None),
            'concepto': filtros.get('concepto', None),
            # Nuevos filtros
            'mes': filtros.get('mes', None),
            'dia': filtros.get('dia', None),
            'anio': filtros.get('anio', None),
            'dni': filtros.get('dni', None),
            'nombres': filtros.get('nombres', None),
            # Parámetros de paginación
            'current_page': current_page,
            'per_page': per_page
        }
        
        result = OrdenServicioModel._execute_sp(
            OrdenServicioModel.ACTIONS["list"],
            params,
            fetch=True
        )
        
        return OrdenServicioModel._map_result_to_dict(result, "list")

    @staticmethod
    def change_orden_servicio_status(num_service, current_user, remote_addr, estado):
        params = {
            'estacion_modificacion': remote_addr,
            'operador_modificacion': current_user,
            'num_servicio': num_service,  # Make sure this is the primary identifier
            'estado': estado,
        }
        
        result = OrdenServicioModel._execute_sp(
            OrdenServicioModel.ACTIONS["change_status"], 
            params
        )
        
        return result if isinstance(result, tuple) else (True, 'Estado de la orden de servicio actualizado con éxito')

    @staticmethod
    def delete_orden_servicio(num_service, current_user, remote_addr, estado):
        # Explicitly log or print the parameters to verify they're correct
        print(f"Delete Params: num_service={num_service}, current_user={current_user}, remote_addr={remote_addr}, estado={estado}")

        params = {
            'num_servicio': num_service,  # Make sure this is the primary identifier
            'estado': estado,
            'estacion_modificacion': remote_addr,
            'operador_modificacion': current_user,
        }
        
        try:
            result = OrdenServicioModel._execute_sp(
                OrdenServicioModel.ACTIONS["delete"], 
                params
            )
            
            # Add more detailed error checking
            if result is None:
                return False, "No se pudo eliminar la orden de servicio"
            
            return result if isinstance(result, tuple) else (True, 'Orden de servicio eliminada con éxito')
        
        except Exception as e:
            # Log the full exception for debugging
            print(f"Error in delete_orden_servicio: {str(e)}")
            return False, f"Error al eliminar la orden de servicio: {str(e)}"

    @staticmethod
    def get_active_ordenes_servicio():
        result = OrdenServicioModel._execute_sp(
            OrdenServicioModel.ACTIONS["list_active"],
            fetch=True
        )
        
        return OrdenServicioModel._map_result_to_dict(result, "list_active")
