import pyodbc
import re
from config import get_db_connection
from ...utils.audit import AuditFields

class CentroCostoModel:
    
    @staticmethod
    def create_centro_costo(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblCentroCosto] 
                    @accion = 1,
                    @idCentroCosto = ?,
                    @centro_costo = ?,
                    @resumen = ?,
                    @id_superior = ?,
                    @meta = ?,
                    @orden_orga = ?,
                    @fecha_registro = ?,
                    @operador_registro = ?,
                    @estacion_registro = ?,
                    @fecha_modificacion = ?,
                    @operador_modificacion = ?,
                    @estacion_modificacion = ?,
                    @flag_estado = ?
            ''', (
                data['idCentroCosto'], data['centro_costo'], data['resumen'], 
                data['id_superior'], data['meta'], data['orden_orga'], 
                data['fecha_registro'], data['operador_registro'], data['estacion_registro'],
                data['fecha_modificacion'], data['operador_modificacion'], 
                data['estacion_modificacion'], data['flag_estado']
            ))
            
            conn.commit()
            return True, 'Centro de costo registrado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar centro de costo'
            
        finally:
            conn.close()

    @staticmethod
    def update_centro_costo(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblCentroCosto] 
                    @accion = 2,
                    @idCentroCosto = ?,
                    @centro_costo = ?,
                    @resumen = ?,
                    @id_superior = ?,
                    @meta = ?,
                    @orden_orga = ?,
                    @fecha_registro = ?,
                    @operador_registro = ?,
                    @estacion_registro = ?,
                    @fecha_modificacion = ?,
                    @operador_modificacion = ?,
                    @estacion_modificacion = ?,
                    @flag_estado = ?
            ''', (
                data['idCentroCosto'], data['centro_costo'], data['resumen'], 
                data['id_superior'], data['meta'], data['orden_orga'], 
                data['fecha_registro'], data['operador_registro'], data['estacion_registro'],
                data['fecha_modificacion'], data['operador_modificacion'], 
                data['estacion_modificacion'], data['flag_estado']
            ))
            
            conn.commit()
            return True, 'Centro de costo actualizado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar centro de costo'
            
        finally:
            conn.close()

    @staticmethod
    def get_centros_costo_list():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblCentroCosto] 
                    @accion = 4;  -- Acción 4 para seleccionar todos los centros de costo activos
            ''')  # No es necesario pasar parámetros en este caso

            centros_costo = cursor.fetchall()

            # Procesar y retornar los resultados en forma de lista de diccionarios
            return [{
                'idCentroCosto': c[0], 
                'centro_costo': c[1], 
                'resumen': c[2], 
                'id_superior': c[3], 
                'meta': c[4], 
                'orden_orga': c[5],
                'fecha_registro': c[6], 
                'operador_registro': c[7], 
                'estacion_registro': c[8],
                'fecha_modificacion': c[9], 
                'operador_modificacion': c[10], 
                'estacion_modificacion': c[11], 
                'flag_estado': c[12]
            } for c in centros_costo]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de centros de costo'
        
        finally:
            conn.close()

