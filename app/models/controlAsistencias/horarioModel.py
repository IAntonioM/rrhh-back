import pyodbc
import re
from config import get_db_connection
from ...utils.audit import AuditFields

class HorarioModel:
    
    @staticmethod
    def create_horario(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir campos de auditoría
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_horario] 
                    @mquery = 1,
                    @horario = ?,
                    @estacion = ?,
                    @operador = ?,
                    @dataxmlHorario = ?
            ''', (data['horario'], data['estacion_reg'], data['operador_reg'], data['dataxmlHorario']))
            
            result = cursor.fetchone()
            conn.commit()
            
            if result and result[0] == 'TRUE':
                return True, result[1]
            else:
                return False, 'Error al registrar horario'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar horario'
            
        finally:
            conn.close()

    @staticmethod
    def update_horario(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir campos de auditoría
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_horario] 
                    @mquery = 2,
                    @idHorario = ?,
                    @horario = ?,
                    @estacion = ?,
                    @operador = ?,
                    @dataxmlHorario = ?
            ''', (data['idHorario'], data['horario'], data['estacion_modificacion'], 
                  data['operador_modificacion'], data['dataxmlHorario']))
            
            result = cursor.fetchone()
            conn.commit()
            
            if result and result[0] == 'TRUE':
                return True, result[1]
            else:
                return False, 'Error al actualizar horario'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar horario'
            
        finally:
            conn.close()

    @staticmethod
    def delete_horario(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir campos de auditoría
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_horario] 
                    @mquery = 3,
                    @idHorario = ?,
                    @estacion = ?,
                    @operador = ?
            ''', (data['idHorario'], data['estacion_modificacion'], data['operador_modificacion']))
            
            result = cursor.fetchone()
            conn.commit()
            
            if result and result[0] == 'TRUE':
                return True, result[1]
            else:
                return False, 'Error al eliminar horario'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al eliminar horario'
            
        finally:
            conn.close()

    @staticmethod
    def get_horario_by_id(idHorario):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_horario] 
                    @mquery = 4,
                    @idHorario = ?
            ''', (idHorario))
            
            horario = cursor.fetchone()
            
            if not horario:
                return None
                
            # Obtener el detalle del horario
            cursor.execute('''
                EXEC [dbo].[sp_horario] 
                    @mquery = 7,
                    @idHorario = ?
            ''', (idHorario))
            
            detalles = cursor.fetchall()
            
            # Construir el resultado con los campos de la tabla
            result = {
                'idHorario': horario[0],
                'horario': horario[1],
                'fecha_registro': horario[2],
                'estacion_registro': horario[3],
                'operador_registro': horario[4],
                'fecha_modificacion': horario[5],
                'estacion_modificacion': horario[6],
                'operador_modificacion': horario[7],
                'flag_estado': horario[8],
                'detalles': [{
                    'idHorario': d[0],
                    'dia': d[1],
                    'hora_entrada': d[2],
                    'hora_tardanza': d[3],
                    'hora_salida': d[4],
                    'hora_refrigerio_salida': d[5],
                    'hora_refrigerio_retorno': d[6]
                } for d in detalles]
            }
            
            return result
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener horario'
        
        finally:
            conn.close()

    @staticmethod
    def get_horarios_list():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_horario] 
                    @mquery = 5
            ''')

            horarios = cursor.fetchall()

            # Construir la lista de resultados con los campos de la tabla
            return [{
                'idHorario': h[0],
                'horario': h[1],
                'fecha_registro': h[2],
                'estacion_registro': h[3],
                'operador_registro': h[4],
                'fecha_modificacion': h[5],
                'estacion_modificacion': h[6],
                'operador_modificacion': h[7],
                'flag_estado': h[8]
            } for h in horarios]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de horarios'
        
        finally:
            conn.close()
    
    @staticmethod
    def count_horarios():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_horario] 
                    @mquery = 6
            ''')

            result = cursor.fetchone()
            
            if result:
                return result[0]  # Devuelve el conteo total de horarios
            else:
                return 0

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al contar horarios'
        
        finally:
            conn.close()
    
    @staticmethod
    def get_horario_detalle(idHorario):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_horario] 
                    @mquery = 7,
                    @idHorario = ?
            ''', (idHorario))
            
            detalles = cursor.fetchall()
            
            # Devolver solo los detalles del horario
            return [{
                'idHorario': d[0],
                'dia': d[1],
                'hora_entrada': d[2],
                'hora_tardanza': d[3],
                'hora_salida': d[4],
                'hora_refrigerio_salida': d[5],
                'hora_refrigerio_retorno': d[6]
            } for d in detalles]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener detalle del horario'
        
        finally:
            conn.close()
    
    @staticmethod
    def get_horarios_combo():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_horario] 
                    @mquery = 10
            ''')

            horarios = cursor.fetchall()

            # Construir la lista para el combo
            return [{
                'idHorario': h[0],
                'horario': h[1]
            } for h in horarios]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener la lista de horarios para combo'
        
        finally:
            conn.close()
            
    @staticmethod
    def build_xml_horario(data_horario):
        """
        Construye el XML para los horarios en el formato requerido por el procedimiento almacenado.
        
        Ejemplo del formato esperado:
        <root>
            <row dia="1" HE="08:00" HT="08:15" HS="17:00" HRS="12:30" HRR="13:30" />
            ...
        </root>
        """
        xml = '<root>\n'
        
        for detalle in data_horario:
            xml += f'    <row dia="{detalle["dia"]}" '
            xml += f'HE="{detalle.get("hora_entrada", "")}" '
            xml += f'HT="{detalle.get("hora_tardanza", "")}" '
            xml += f'HS="{detalle.get("hora_salida", "")}" '
            xml += f'HRS="{detalle.get("hora_refrigerio_salida", "")}" '
            xml += f'HRR="{detalle.get("hora_refrigerio_retorno", "")}" />\n'
        
        xml += '</root>'
        
        return xml