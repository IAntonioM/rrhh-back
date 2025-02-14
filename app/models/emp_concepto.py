import pyodbc
import re
from config import get_db_connection
from ..utils.auditv2 import AuditFieldsv2

class EmpConceptoModel:
    
    @staticmethod
    def create_emp_concepto(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir los campos de auditoría (como quien hace la operación, etc.)
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Planilla].[sp_EmpConceptos] 
                    @accion = 1, 
                    @idEmpleado = ?, 
                    @tipo = ?, 
                    @idConcepto = ?, 
                    @idTipoMonto = ?, 
                    @monto = ?, 
                    @secuencia = ?, 
                    @flag_ATM = ?, 
                    @periodo_mes_desde = ?, 
                    @periodo_anio_desde = ?, 
                    @periodo_mes_hasta = ?, 
                    @periodo_anio_hasta = ?, 
                    @comentario = ?, 
                    @estado = 1, 
                    @fecha_registro = ?, 
                    @estacion_registro = ?, 
                    @operador_registro = ?, 
                    @fecha_modificacion = ?, 
                    @estacion_modificacion = ?, 
                    @operador_modificacion = ?, 
                    @flag_estado = 1, 
                    @flag_descuento = 0
            ''', (
                 data['idEmpleado'], data['tipo'], data['idConcepto'], data['idTipoMonto'], 
                data['monto'], data['secuencia'], data['flag_ATM'], data['periodo_mes_desde'], data['periodo_anio_desde'],
                data['periodo_mes_hasta'], data['periodo_anio_hasta'], data['comentario'], 
                data['fecha_registro'], data['estacion_registro'], data['operador_registro'], data['fecha_modificacion'],
                data['estacion_modificacion'], data['operador_modificacion']
            ))

            conn.commit()
            return True, 'Concepto registrado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar concepto laboral'
            
        finally:
            conn.close()
    @staticmethod
    def update_estado_emp_concepto(idEmpConcepto, idNuevoEstado, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir auditoría a los datos
            data = {}
            # Si tienes una función para añadir campos de auditoría, puedes agregarla aquí
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
            
            cursor = conn.cursor()
            print(data)
            
            cursor.execute('''
                EXEC [Planilla].[sp_EmpConceptos] 
                @accion = 4, 
                @idEmpConcepto = ?, 
                @estado = ?, 
                @fecha_modificacion = ?, 
                @estacion_modificacion = ?, 
                @operador_modificacion = ?
            ''', (
                idEmpConcepto, 
                idNuevoEstado,
                data['fecha_modificacion'],        # Nueva fecha de modificación
                data['estacion_modificacion'],     # Estación de modificación
                data['operador_modificacion']      # Operador de la modificación
            ))

            conn.commit()
            return True, 'Estado de EmpConcepto actualizado con éxito'
        
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar el estado de EmpConcepto'
        
        finally:
            conn.close()



    @staticmethod
    def update_emp_concepto(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir los campos de auditoría
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Planilla].[sp_EmpConceptos] 
                    @accion = 2, 
                    @idEmpConcepto = ?, 
                    @tipo = ?, 
                    @idConcepto = ?, 
                    @idTipoMonto = ?, 
                    @monto = ?, 
                    @secuencia = ?, 
                    @flag_ATM = ?, 
                    @periodo_mes_desde = ?, 
                    @periodo_anio_desde = ?, 
                    @periodo_mes_hasta = ?, 
                    @periodo_anio_hasta = ?, 
                    @comentario = ?, 
                    @fecha_modificacion = ?, 
                    @estacion_modificacion = ?, 
                    @operador_modificacion = ?
            ''', (
                data['idEmpConcepto'], 
                data['tipo'], 
                data['idConcepto'],
                data['idTipoMonto'], 
                data['monto'], 
                data['secuencia'], 
                data['flag_ATM'], 
                data['periodo_mes_desde'], 
                data['periodo_anio_desde'], 
                data['periodo_mes_hasta'], 
                data['periodo_anio_hasta'], 
                data['comentario'], 
                data['fecha_modificacion'], 
                data['estacion_modificacion'], 
                data['operador_modificacion']
            ))

            conn.commit()
            return True, 'Concepto actualizado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar concepto laboral'
            
        finally:
            conn.close()


    @staticmethod
    def get_emp_conceptos_list():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Planilla].[sp_EmpConceptos] 
                    @accion = 4;  -- Acción 4 para seleccionar todos los conceptos laborales activos
            ''')  # No es necesario pasar parámetros en este caso

            conceptos = cursor.fetchall()

            # Procesar y retornar los resultados en forma de lista de diccionarios
            return [{
                'idEmpConcepto': c[0], 
                'codEmpleado': c[1], 
                'tipo': c[2], 
                'idConcepto': c[3], 
                'idTipoMonto': c[4], 
                'monto': c[5], 
                'secuencia': c[6], 
                'flag_ATM': c[7], 
                'periodo_mes_desde': c[8], 
                'periodo_anio_desde': c[9], 
                'periodo_mes_hasta': c[10], 
                'periodo_anio_hasta': c[11], 
                'comentario': c[12], 
                'estado': c[13],
                'fecha_registro': c[14], 
                'estacion_registro': c[15], 
                'operador_registro': c[16], 
                'fecha_modificacion': c[17],
                'estacion_modificacion': c[18], 
                'operador_modificacion': c[19], 
                'flag_estado': c[20], 
                'flag_descuento': c[21]
            } for c in conceptos]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de conceptos laborales'
        
        finally:
            conn.close()
    @staticmethod
    def consult_emp_concepto_tipo_cod(idEmpleado=None, tipo=None):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            # Llamar al procedimiento almacenado con los parámetros codEmpleado y tipo
            cursor.execute('''
                EXEC [Planilla].[sp_EmpConceptos] 
                    @accion = 5,
                    @idEmpleado = ?, 
                    @tipo = ?;
            ''', (idEmpleado, tipo))  # Pasar los parámetros como tuplas

            conceptos = cursor.fetchall()

            # Procesar y retornar los resultados en forma de lista de diccionarios
            return [{
                'idEmpConcepto': c[0], 
                'codEmpleado': c[1], 
                'tipo': c[2], 
                'idConcepto': c[3], 
                'idTipoMonto': c[4], 
                'monto': c[5], 
                'secuencia': c[6], 
                'flag_ATM': c[7], 
                'periodo_mes_desde': c[8], 
                'periodo_anio_desde': c[9], 
                'periodo_mes_hasta': c[10], 
                'periodo_anio_hasta': c[11], 
                'comentario': c[12], 
                'estado': c[13],
                'fecha_registro': c[14], 
                'estacion_registro': c[15], 
                'operador_registro': c[16], 
                'fecha_modificacion': c[17],
                'estacion_modificacion': c[18], 
                'operador_modificacion': c[19], 
                'flag_estado': c[20], 
                'flag_descuento': c[21],
                'idEmpleado': c[22],  # idEmpleado
                'concepto_nombres': c[23],  # Nombre del concepto
                'tipoMonto_nombre': c[24],  # Nombre del tipo de monto
                'secuencia_nombre': c[25],   # Nombre de la secuencia
                'concepto_codigoInterno': c[26],   # Código interno del concepto
            } for c in conceptos]


        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de conceptos laborales'
        
        finally:
            conn.close()