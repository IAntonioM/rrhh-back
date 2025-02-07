import pyodbc
import re
from config import get_db_connection
from ..utils.audit import AuditFields

class CargoModel:
    
    @staticmethod
    def create_cargo(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir campos de auditoría si es necesario
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblCargo] 
                    @accion = 1,
                    @cargo = ?,
                    @funciones = ?,
                    @flag_estado = ?,
                    @fecha_reg = ?,
                    @operador_reg = ?,
                    @estacion_reg = ?
            ''', (data['cargo'], data['funciones'], data['flag_estado'], 
                  data['fecha_reg'], data['operador_reg'], data['estacion_reg']))
            
            conn.commit()
            return True, 'Cargo registrado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar cargo'
            
        finally:
            conn.close()

    @staticmethod
    def update_cargo(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir campos de auditoría si es necesario
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblCargo] 
                    @accion = 2,
                    @idCargo = ?,
                    @cargo = ?,
                    @funciones = ?,
                    @flag_estado = ?,
                    @fecha_act = ?,
                    @operador_act = ?,
                    @estacion_act = ?
            ''', (data['idCargo'], data['cargo'], data['funciones'], 
                  data['flag_estado'], data['fecha_act'], data['operador_act'], 
                  data['estacion_act']))
            
            conn.commit()
            return True, 'Cargo actualizado con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar cargo'
            
        finally:
            conn.close()

    @staticmethod
    def get_cargos_list():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_tblCargo] 
                    @accion = 4;  -- Acción 4 para seleccionar todos los registros activos
            ''')  # No es necesario pasar parámetros en este caso

            cargos = cursor.fetchall()

            # Construir la lista de resultados con los campos de la tabla
            return [{
                'idCargo': c[0], 
                'cargo': c[1], 
                'funciones': c[2], 
                'flag_estado': c[3], 
                'fecha_reg': c[4], 
                'operador_reg': c[5], 
                'estacion_reg': c[6], 
                'fecha_act': c[7], 
                'operador_act': c[8], 
                'estacion_act': c[9]
            } for c in cargos]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de cargos'
        
        finally:
            conn.close()

