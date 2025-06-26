import pyodbc
from config import get_db_connection
import re
from ...utils.auditv2 import AuditFieldsv2

class ControlContratoModel:

    @staticmethod
    def create(data, current_user, remote_addr):
        """Inserta un nuevo control de contrato en la base de datos"""
        conn = get_db_connection()
        try:
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Locadores].[sp_control_contrato]
                    @accion = 1,
                    @id_contrato = ?,
                    @mes = ?,
                    @anio = ?,
                    @estado = ?,
                    @estado_pago = ?,
                    @motivo_reemplazo = ?,
                    @fecha_registro = ?,
                    @estacion_registro = ?,
                    @operador_registro = ?,
                    @fecha_modificacion = ?,
                    @estacion_modificacion = ?,
                    @operador_modificacion = ?,
                    @monto = ?,
                    @FechaInicio = ?,
                    @FechaFin = ?
            ''', (
                data['id_contrato'], data['mes'], data['anio'], data['estado'],
                data['estado_pago'], data['motivo_reemplazo'], data['fecha_registro'],
                data['estacion_registro'], data['operador_registro'], data['fecha_modificacion'],
                data['estacion_modificacion'], data['operador_modificacion'], data['monto'],
                data['FechaInicio'], data['FechaFin']
            ))

            conn.commit()
            return True, 'Contrato registrado con éxito'

        except pyodbc.Error as e:
            return False, ControlContratoModel._extract_sql_error(e)

        finally:
            conn.close()

    @staticmethod
    def update(data, current_user, remote_addr):
        """Actualiza un control de contrato existente"""
        conn = get_db_connection()
        try:
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Locadores].[sp_control_contrato]
                    @accion = 2,
                    @id = ?,
                    @id_contrato = ?,
                    @mes = ?,
                    @anio = ?,
                    @estado = ?,
                    @estado_pago = ?,
                    @motivo_reemplazo = ?,
                    @fecha_modificacion = ?,
                    @estacion_modificacion = ?,
                    @operador_modificacion = ?,
                    @monto = ?
            ''', (
                data['id'], data['id_contrato'], data['mes'], data['anio'], data['estado'],
                data['estado_pago'], data['motivo_reemplazo'], data['fecha_modificacion'],
                data['estacion_modificacion'], data['operador_modificacion'], data['monto']
            ))

            conn.commit()
            return True, 'Contrato actualizado con éxito'

        except pyodbc.Error as e:
            return False, ControlContratoModel._extract_sql_error(e)

        finally:
            conn.close()

    @staticmethod
    def filter(filtros, current_page, per_page):
        """Consulta control de contratos con filtros y paginación"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            cursor.execute('''
                EXEC [Locadores].[sp_control_contrato]
                    @accion = 3,
                    @id_contrato = ?,
                    @estado = ?,
                    @estado_pago = ?,
                    @mes = ?,
                    @anio = ?,
                    @current_page = ?,
                    @per_page = ?
            ''', (
                filtros.get('id_contrato', None), filtros.get('estado', None),
                filtros.get('estado_pago', None), filtros.get('mes', None),
                filtros.get('anio', None), current_page, per_page
            ))

            # Obtener nombres de columnas del resultado
            columns = [column[0] for column in cursor.description]

            # Convertir cada fila a un diccionario usando los nombres de columnas
            contratos = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return contratos

        except pyodbc.Error as e:
            return {
                'success': False,
                'message': ControlContratoModel._extract_sql_error(e)
            }

        finally:
            conn.close()

    @staticmethod
    def change_status(id, estado, current_user, remote_addr):
        """Cambia el estado de un contrato"""
        conn = get_db_connection()
        try:
            data = {'id': id, 'estado': estado, 'operador_modificacion': current_user}
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Locadores].[sp_control_contrato]
                    @accion = 4,
                    @id = ?,
                    @estado = ?
            ''', (id, estado))

            conn.commit()
            return True, 'Estado del contrato actualizado con éxito'

        except pyodbc.Error as e:
            return False, ControlContratoModel._extract_sql_error(e)

        finally:
            conn.close()

    @staticmethod
    def delete(id, current_user, remote_addr):
        """Elimina un control de contrato"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Locadores].[sp_control_contrato]
                    @accion = 5,
                    @id = ?
            ''', (id,))

            conn.commit()
            return True, 'Contrato eliminado con éxito'

        except pyodbc.Error as e:
            return False, ControlContratoModel._extract_sql_error(e)

        finally:
            conn.close()

    @staticmethod
    def _extract_sql_error(error):
        """Extrae y formatea el mensaje de error de SQL Server"""
        error_msg = str(error)
        matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
        return matches.group(1).strip() if matches else 'Error en la base de datos'



    @staticmethod
    def filter_control_contrato(filtros):
        """Consulta control de contratos con filtros y paginación"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            print('PRUENAAA')
            print(filtros.get('FechaFin', None))
            print(filtros.get('FechaInicio', None))
            cursor.execute('''
                EXEC [Locadores].[sp_control_contrato]
                    @accion = 6,
                    @FechaInicio = ?,
                    @FechaFin = ?,
                    @dni = ?,
                    @nombres = ?
            ''', (
                filtros.get('FechaInicio', None), filtros.get('FechaFin', None),
                filtros.get('dni', None),
                filtros.get('nombres', None)
            ))

            # Obtener nombres de columnas del resultado
            columns = [column[0] for column in cursor.description]

            # Convertir cada fila a un diccionario usando los nombres de columnas
            contratos = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return contratos

        except pyodbc.Error as e:
            return {
                'success': False,
                'message': ControlContratoModel._extract_sql_error(e)
            }

        finally:
            conn.close()
    
    @staticmethod
    def filter_control_contrato_mensual(filtros):
        """Consulta control de contratos con filtros y paginación"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            print('PRUENAAA')
            print(filtros.get('FechaFin', None))
            print(filtros.get('FechaInicio', None))
            cursor.execute('''
                EXEC [Locadores].[sp_control_contrato]
                    @accion = 7,
                    @FechaInicio = ?,
                    @FechaFin = ?,
                    @dni = ?,
                    @nombres = ?
            ''', (
                filtros.get('FechaInicio', None),
                filtros.get('FechaFin', None),
                filtros.get('dni', None),
                filtros.get('nombres', None)
            ))


            # Obtener nombres de columnas del resultado
            columns = [column[0] for column in cursor.description]

            # Convertir cada fila a un diccionario usando los nombres de columnas
            contratos = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return contratos

        except pyodbc.Error as e:
            return {
                'success': False,
                'message': ControlContratoModel._extract_sql_error(e)
            }

        finally:
            conn.close()