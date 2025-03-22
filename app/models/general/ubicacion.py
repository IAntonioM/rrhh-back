import pyodbc
from config import get_db_connection

class UbicacionModel:
    
    @staticmethod
    def list_departamentos():
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_ubicacion]
                    @accion = 1;
            ''')  # Acción 1 para listar los departamentos

            departamentos = cursor.fetchall()

            # Procesar y retornar los resultados en forma de lista de diccionarios
            return [{
                'idDepartamento': d[0],
                'departamento': d[1],
                'flag_estado': d[2]
            } for d in departamentos]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            return False, error_msg
        finally:
            conn.close()

    @staticmethod
    def list_provincias_by_departamento(idDepartamento):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_ubicacion]
                    @accion = 4,
                    @idDepartamento = ?;
            ''', (idDepartamento,))  # Acción 4 para listar provincias por idDepartamento

            provincias = cursor.fetchall()

            return [{
                'idProvincia': p[0],
                'provincia': p[1],
                'flag_estado': p[2]
            } for p in provincias]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            return False, error_msg
        finally:
            conn.close()

    @staticmethod
    def list_ubigeos_by_provincia(idProvincia):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_ubicacion]
                    @accion = 5,
                    @idProvincia = ?;
            ''', (idProvincia,))  # Acción 5 para listar ubigeos por idProvincia

            ubigeos = cursor.fetchall()

            return [{
                'idUbigeo': u[0],
                'ubigeo': u[1],
                'flag_estado': u[2]
            } for u in ubigeos]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            return False, error_msg
        finally:
            conn.close()
