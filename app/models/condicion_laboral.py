
import pyodbc
import re
from config import get_db_connection
from ..utils.audit import AuditFields

class CondicionLaboralModel:
    
    @staticmethod
    def create_condicion_laboral(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_condicionlaboral] 
                    @accion = 1,
                    @condicion_laboral = ?,
                    @abreviatura_codigo = ?,
                    @flag_estado = ?
            ''', (data['condicion_laboral'], data['abreviatura_codigo'], data['flag_estado']))
            
            conn.commit()
            return True, 'Condición laboral registrada con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar condición laboral'
            
        finally:
            conn.close()

    @staticmethod
    def update_condicion_laboral(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_condicionlaboral] 
                    @accion = 2,
                    @idCondicionLaboral = ?,
                    @condicion_laboral = ?,
                    @abreviatura_codigo = ?,
                    @flag_estado = ?
            ''', (data['idCondicionLaboral'], data['condicion_laboral'], 
                  data['abreviatura_codigo'], data['flag_estado']))
            
            conn.commit()
            return True, 'Condición laboral actualizada con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar condición laboral'
            
        finally:
            conn.close()

    @staticmethod
    def get_condiciones_laborales_list():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_condicionlaboral] 
                    @accion = 4;  -- Acción 4 para seleccionar todas las condiciones laborales activas
            ''')  # No es necesario pasar parámetros en este caso

            condiciones = cursor.fetchall()

            # Procesar y retornar los resultados en forma de lista de diccionarios
            return [{
                'idCondicionLaboral': c[0], 
                'condicion_laboral': c[1], 
                'abreviatura_codigo': c[2], 
                'flag_estado': c[3]
            } for c in condiciones]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de condiciones laborales'
        
        finally:
            conn.close()

