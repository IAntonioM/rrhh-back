import pyodbc
import re
from config import get_db_connection

class TipoMonto:
    @staticmethod
    def execute_sp(tipo=None):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('EXEC [dbo].[sp_TipoMonto]')

            results = cursor.fetchall()
            if not results:
                return []

            # Convertir los resultados a diccionario
            data = [dict((column[0], value) for column, value in zip(cursor.description, row)) for row in results]

            return data

        except pyodbc.Error as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return {'error': matches.group(1).strip() if matches else 'Error en la operación'}
        finally:
            conn.close()

    @staticmethod
    def list_tipoMonto(tipo=None):
        return TipoMonto.execute_sp(tipo)
