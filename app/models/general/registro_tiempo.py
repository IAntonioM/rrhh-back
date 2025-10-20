import pyodbc
import re
from config import get_db_connection

class TiempoProcesamiento:
    
    @staticmethod
    def guardar_tiempo_procesamiento(tiempo_modal, tipo):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_guardar_tiempo_procesamiento] 
                    @tiempo_modal = ?,
                    @tipo = ?
            ''', (tiempo_modal, tipo))

            conn.commit()
            return True, 'Tiempo de procesamiento registrado con éxito'

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar tiempo de procesamiento'

        finally:
            conn.close()

    @staticmethod
    def get_registros_procesamiento(filtros=None):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Consulta simple para obtener todos los registros
            # Si necesitas filtros específicos, deberías crear un nuevo procedimiento almacenado
            cursor.execute('''
                SELECT 
                    id_registro,
                    tiempo_modal,
                    tiempo_registro,
                    tiempo_procesamiento,
                    tipo
                FROM Registro_Procesamiento
                ORDER BY tiempo_registro DESC
            ''')

            registros = cursor.fetchall()

            return [{
                'id_registro': r[0],
                'tiempo_modal': r[1],
                'tiempo_registro': r[2],
                'tiempo_procesamiento': r[3],
                'tipo': r[4]
            } for r in registros]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al obtener registros de procesamiento'

        finally:
            conn.close()