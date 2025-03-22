import pyodbc
import re
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class ConceptosMuniModel:
    
    @staticmethod
    def create_concepto_muni(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblConceptosMUNI] 
                    @accion = 1,
                    @condicion_laboral = ?, 
                    @ccodcpto_Anterior = ?, 
                    @codigoPDT = ?, 
                    @codigoInterno = ?, 
                    @concepto = ?, 
                    @tipo = ?, 
                    @tipoCalculo = ?, 
                    @idTipoMonto = ?, 
                    @flag_ATM = ?, 
                    @monto = ?, 
                    @fecha_registro = ?, 
                    @estacion_registro = ?, 
                    @operador_registro = ?, 
                    @fecha_modificacion = ?, 
                    @estacion_modificacion = ?, 
                    @operador_modificacion = ?, 
                    @flag_estado = ?, 
                    @flag_apldialab = ?
            ''', (
                data['idCondicionLaboral'], data['ccodcpto_Anterior'], data['codigoPDT'], 
                data['codigoInterno'], data['concepto'], data['tipo'], data['tipoCalculo'], 
                data['idTipoMonto'], data['flag_ATM'], data['monto'], data['fecha_registro'], 
                data['estacion_registro'], data['operador_registro'], data['fecha_modificacion'], 
                data['estacion_modificacion'], data['operador_modificacion'], 
                data['flag_estado'], data['flag_apldialab']
            ))

            conn.commit()
            return True, 'Concepto MUNI registrado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar concepto MUNI'
        
        finally:
            conn.close()

    @staticmethod
    def update_concepto_muni(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblConceptosMUNI] 
                    @accion = 2,
                    @idConcepto = ?, 
                    @condicion_laboral = ?, 
                    @ccodcpto_Anterior = ?, 
                    @codigoPDT = ?, 
                    @codigoInterno = ?, 
                    @concepto = ?, 
                    @tipo = ?, 
                    @tipoCalculo = ?, 
                    @idTipoMonto = ?, 
                    @flag_ATM = ?, 
                    @monto = ?, 
                    @fecha_registro = ?, 
                    @estacion_registro = ?, 
                    @operador_registro = ?, 
                    @fecha_modificacion = ?, 
                    @estacion_modificacion = ?, 
                    @operador_modificacion = ?, 
                    @flag_estado = ?, 
                    @flag_apldialab = ?
            ''', (
                data['idConcepto'], data['idCondicionLaboral'], data['ccodcpto_Anterior'], 
                data['codigoPDT'], data['codigoInterno'], data['concepto'], data['tipo'], 
                data['tipoCalculo'], data['idTipoMonto'], data['flag_ATM'], data['monto'], 
                data['fecha_registro'], data['estacion_registro'], data['operador_registro'], 
                data['fecha_modificacion'], data['estacion_modificacion'], data['operador_modificacion'], 
                data['flag_estado'], data['flag_apldialab']
            ))

            conn.commit()
            return True, 'Concepto MUNI actualizado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar concepto MUNI'
        
        finally:
            conn.close()

    @staticmethod
    def get_conceptos_muni_list():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblConceptosMUNI] 
                    @accion = 4;  -- Acción 4 para seleccionar todos los conceptos MUNI activos
            ''')  # No es necesario pasar parámetros en este caso

            conceptos_muni = cursor.fetchall()

            # Procesar y retornar los resultados en forma de lista de diccionarios
            return [{
                'idConcepto': c[0],
                'idCondicionLaboral': c[1],
                'ccodcpto_Anterior': c[2],
                'codigoPDT': c[3],
                'codigoInterno': c[4],
                'concepto': c[5],
                'tipo': c[6],
                'tipoCalculo': c[7],
                'idTipoMonto': c[8],
                'flag_ATM': c[9],
                'monto': c[10],
                'fecha_registro': c[11],
                'estacion_registro': c[12],
                'operador_registro': c[13],
                'fecha_modificacion': c[14],
                'estacion_modificacion': c[15],
                'operador_modificacion': c[16],
                'flag_estado': c[17],
                'flag_apldialab': c[18]
            } for c in conceptos_muni]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de conceptos MUNI'

        finally:
            conn.close()


    @staticmethod
    def get_conceptos_muni_active():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblConceptosMUNI] 
                    @accion = 5;  -- Acción 5 para obtener todos los registros activos (flag_estado = 1)
            ''')

            conceptos_muni = cursor.fetchall()

            # Procesar y retornar los resultados en forma de lista de diccionarios
            return [{
                'idConcepto': c[0],
                'idCondicionLaboral': c[1],
                'ccodcpto_Anterior': c[2],
                'codigoPDT': c[3],
                'codigoInterno': c[4],
                'concepto': c[5],
                'tipo': c[6],
                'tipoCalculo': c[7],
                'idTipoMonto': c[8],
                'flag_ATM': c[9],
                'monto': c[10],
                'fecha_registro': c[11],
                'estacion_registro': c[12],
                'operador_registro': c[13],
                'fecha_modificacion': c[14],
                'estacion_modificacion': c[15],
                'operador_modificacion': c[16],
                'flag_estado': c[17],
                'flag_apldialab': c[18]
            } for c in conceptos_muni]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de conceptos MUNI activos'

        finally:
            conn.close()

    @staticmethod
    def get_conceptos_muni_by_employee(id_empleado, tipo=None):
        try:
            # Establish DB connection
            conn = get_db_connection()
            cursor = conn.cursor()

            # Execute the stored procedure with parameters
            cursor.execute('''
                EXEC [dbo].[sp_tblConceptosMUNI] 
                    @accion = 6,  -- Acción 6 to filter by employee
                    @idEmpleado = ?,  -- Employee ID
                    @tipo = ?  -- Tipo parameter
            ''', (id_empleado, tipo))

            # Fetch the results
            conceptos_muni = cursor.fetchall()

            # Process the results into a list of dictionaries
            return [{
                'idConcepto': c[0],
                'idCondicionLaboral': c[1],
                'ccodcpto_Anterior': c[2],
                'codigoPDT': c[3],
                'codigoInterno': c[4],
                'concepto': c[5],
                'tipo': c[6],
                'tipoCalculo': c[7],
                'idTipoMonto': c[8],
                'flag_ATM': c[9],
                'monto': c[10],
                'fecha_registro': c[11],
                'estacion_registro': c[12],
                'operador_registro': c[13],
                'fecha_modificacion': c[14],
                'estacion_modificacion': c[15],
                'operador_modificacion': c[16],
                'flag_estado': c[17],
                'flag_apldialab': c[18],
                # 'condicion_laboral_nombre': c[19]
            } for c in conceptos_muni]

        except pyodbc.ProgrammingError as e:
            # Error handling for DB errors
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error retrieving data'

        finally:
            # Ensure connection is closed
            conn.close()