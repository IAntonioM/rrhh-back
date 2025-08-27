import pyodbc
import re
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class RegistroLocadorModel:

    @staticmethod
    def create(data, current_user, remote_addr):
        """Inserta un nuevo contrato en la base de datos"""
        conn = get_db_connection()
        try:
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
            
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Locadores].[sp_contrato]
        @accion = 1,
        @id_datos_personales = ?,
        @idCentroCosto = ?,
        @id_cargo = ?,
        @nro_orden_servicio = ?,
        @nro_siaf = ?,
        @devengar = ?,
        @campo1 = ?,
        @campo2 = ?,
        @campo3 = ?,
        @monto = ?,
        @id_concepto = ?,
        @fecha_orden = ?,
        @estado = ?,
        @estado_recepcion = ?,
        @tipo = ?,
        @otros_dir = ?,
        @motivo_reemplazo = ?,
        @mes_anio = ?,
        @flag_padre_madre = ?,
        @estacion_registro = ?,
        @operador_registro = ?
            ''', (
    data['id_datos_personales'], data['idCentroCosto'], data['id_cargo'], 
    data['nro_orden_servicio'], data['nro_siaf'],
    data.get('devengar', 0), 
    data.get('campo1', ''), data.get('campo2', ''), data.get('campo3', ''),
    data['monto'], data['id_concepto'], data['fecha_orden'], 
    data['estado'], data['estado_recepcion'], data['tipo'], 
    data['otros_dir'], data['motivo_reemplazo'],
    data['mes_anio'], data.get('flag_padre_madre', 0),   # 👈 nuevos campos
    data['estacion_registro'], data['operador_registro']
            ))

            conn.commit()
            return True, 'Contrato registrado con éxito'

        except pyodbc.Error as e:
            return False, RegistroLocadorModel._extract_sql_error(e)

        finally:
            conn.close()

    @staticmethod
    def update(data, current_user, remote_addr):
        """Actualiza un contrato existente"""
        conn = get_db_connection()
        try:
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
            
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Locadores].[sp_contrato]
        @accion = 2,
        @id = ?,
        @id_datos_personales = ?,
        @idCentroCosto = ?,
        @id_cargo = ?,
        @nro_orden_servicio = ?,
        @nro_siaf = ?,
        @devengar = ?,
        @campo1 = ?,
        @campo2 = ?,
        @campo3 = ?,
        @fecha_inicio = ?,
        @fecha_fin = ?,
        @monto = ?,
        @id_concepto = ?,
        @fecha_orden = ?,
        @estado = ?,
        @estado_recepcion = ?,
        @tipo = ?,
        @otros_dir = ?,
        @motivo_reemplazo = ?,
        @estacion_modificacion = ?,
        @operador_modificacion = ?,
        @criterio = ?,
        @n_comprobante = ?,
        @fecha_comprobante = ?,
        @flag_recepcion = ?
            ''', (
                data['id'], 
    data.get('id_datos_personales', None),
    data.get('idCentroCosto', None),
    data.get('id_cargo', None),
    data.get('nro_orden_servicio', None),
    data.get('nro_siaf', None),
    data.get('devengar', None),
    data.get('campo1', None),
    data.get('campo2', None),
    data.get('campo3', None),
    data.get('fecha_inicio', None),
    data.get('fecha_fin', None),
    data.get('monto', None),
    data.get('id_concepto', None),
    data.get('fecha_orden', None),
    data.get('estado', None),
    data.get('estado_recepcion', None),
    data.get('tipo', None),
    data.get('otros_dir', None),
    data.get('motivo_reemplazo', None),
    data.get('estacion_modificacion', None),
    data.get('operador_modificacion', None),
    data.get('criterio', None),
    data.get('n_comprobante', None),
    data.get('fecha_comprobante', None),
    data.get('flag_recepcion', 0)   # por defecto 0 si no viene

            ))

            conn.commit()
            return True, 'Contrato actualizado con éxito'

        except pyodbc.Error as e:
            return False, RegistroLocadorModel._extract_sql_error(e)

        finally:
            conn.close()
    
    @staticmethod
    def renew(data, current_user, remote_addr):
        """Renueva (crea uno nuevo) un contrato existente basado en uno anterior"""
        conn = get_db_connection()
        try:
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
            print('ID')
            print(data['id'])
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Locadores].[sp_contrato]
                    @accion = 22,
                    @id = ?,
                    @id_datos_personales = ?,
                    @idCentroCosto = ?,
                    @id_cargo = ?,
                    @nro_orden_servicio = ?,
                    @nro_siaf = ?,
                    @devengar = ?,
                    @campo1 = ?,
                    @campo2 = ?,
                    @campo3 = ?,
                    @fecha_inicio = ?,
                    @fecha_fin = ?,
                    @monto = ?,
                    @id_concepto = ?,
                    @fecha_orden = ?,
                    @estado = ?,
                    @estado_recepcion = ?,
                    @tipo = ?,
                    @otros_dir = ?,
                    @motivo_reemplazo = ?,
                    @estacion_registro = ?,
                    @operador_registro = ?
            ''', (
                data['id'],  # ID del contrato original
                data.get('id_datos_personales'),
                data.get('idCentroCosto'),
                data.get('id_cargo'),
                data.get('nro_orden_servicio'),
                data.get('nro_siaf'),
                data.get('devengar'),
                data.get('campo1'),
                data.get('campo2'),
                data.get('campo3'),
                data.get('fecha_inicio'),
                data.get('fecha_fin'),
                data.get('monto'),
                data.get('id_concepto'),
                data.get('fecha_orden'),
                data.get('estado', 1),  # Por defecto activo
                data.get('estado_recepcion'),
                data.get('tipo'),
                data.get('otros_dir'),
                data.get('motivo_reemplazo'),
                data.get('estacion_registro'),
                data.get('operador_registro')
            ))

            conn.commit()
            return True, 'Contrato renovado con éxito'

        except pyodbc.Error as e:
            return False, RegistroLocadorModel._extract_sql_error(e)

        finally:
            conn.close()


    @staticmethod
    def filter(filtros, current_page, per_page):
        """Obtiene contratos con filtros y paginación"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                EXEC [Locadores].[sp_contrato]
                    @accion = 3,
                    @id = ?,
                    @id_datos_personales = ?,
                    @idCentroCosto = ?,
                    @id_cargo = ?,
                    @nro_orden_servicio = ?,
                    @estado = ?,
                    @estado_recepcion = ?,
                    @mes= ?,
                    @anio= ?,
                    @dni= ?,
                    @nombreApellido= ?,
                    @current_page = ?,
                    @per_page = ?
            ''', (
                filtros.get('id', None), 
                filtros.get('id_datos_personales', None), 
                filtros.get('idCentroCosto', None),
                filtros.get('id_cargo', None),
                filtros.get('nro_orden_servicio', None),
                filtros.get('estado', None),
                filtros.get('estado_recepcion', None),
                filtros.get('mes', None),
                filtros.get('anio', None),
                filtros.get('dni', None),
                filtros.get('nombreApellido', None),
                current_page,
                per_page
            ))
            
            # Obtener nombres de columnas del resultado
            columns = [column[0] for column in cursor.description]
        
            # Convertir cada fila a un diccionario usando los nombres de columnas
            contratos = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return contratos
        
        except pyodbc.Error as e:
            return {
                'success': False,
                'message': RegistroLocadorModel._extract_sql_error(e)
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
                EXEC [Locadores].[sp_contrato]
                    @accion = 4,
                    @id = ?,
                    @estado = ?
            ''', (id, estado))

            conn.commit()
            return True, 'Estado del contrato actualizado con éxito'

        except pyodbc.Error as e:
            return False, RegistroLocadorModel._extract_sql_error(e)

        finally:
            conn.close()
    
    @staticmethod
    def change_status_recepcion_list(id_list, estado, current_user, remote_addr):
        """Cambia el estado de múltiples contratos"""
        if not id_list:
            return False, "La lista de IDs no puede estar vacía"

        conn = get_db_connection()
        try:
  

            # Agregar datos de auditoría
            data = {'id_list':id_list,'estado': estado, 'operador_modificacion': current_user}
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Locadores].[sp_contrato]
                    @accion = 6,
                    @id_list = ?,
                    @estado = ?,
                    @operador_modificacion = ?
            ''', (id_list, estado, current_user))

            conn.commit()
            return True, f"Estado actualizado para {len(id_list)} contratos"

        except pyodbc.Error as e:
            return False, RegistroLocadorModel._extract_sql_error(e)

        finally:
            conn.close()

    @staticmethod
    def delete(id, current_user, remote_addr):
        """Elimina un contrato"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Locadores].[sp_contrato]
                    @accion = 5,
                    @id = ?
            ''', (id,))

            conn.commit()
            return True, 'Contrato eliminado con éxito'

        except pyodbc.Error as e:
            return False, RegistroLocadorModel._extract_sql_error(e)

        finally:
            conn.close()

    @staticmethod
    def _extract_sql_error(error):
        """Extrae y formatea el mensaje de error de SQL Server"""
        error_msg = str(error)
        matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
        return matches.group(1).strip() if matches else 'Error en la base de datos'
    
    @staticmethod
    def duplicar_control_contratos(id_list, mes, anio, current_user, remote_addr):
        """Duplica registros de control_contrato para una nueva programación de mes/año"""
        if not id_list:
            return False, "La lista de IDs no puede estar vacía"
        print("mes")
        print(mes)
        conn = get_db_connection()
        try:
            # Datos de auditoría
            data = {
                'id_list': id_list,
                'mes': mes,
                'anio': anio,
                'operador_registro': current_user
            }
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Locadores].[sp_contrato]
                    @accion = 7,
                    @id_list = ?,
                    @mes = ?,
                    @anio = ?,
                    @fecha_registro = ?,
                    @estacion_registro = ?,
                    @operador_registro = ?
            ''', (
                id_list,
                mes,
                anio,
                data['fecha_registro'],
                data['estacion_registro'],
                data['operador_registro']
            ))

            conn.commit()
            return True, f"Se duplicaron correctamente {len(id_list.split(','))} contratos"

        except pyodbc.Error as e:
            return False, RegistroLocadorModel._extract_sql_error(e)

        finally:
            conn.close()

    @staticmethod
    def actualizar_control_contrato(id_list, estado, current_user, remote_addr,motivo_reemplazo):
        """Duplica registros de control_contrato para una nueva programación de mes/año"""
        if not id_list:
            return False, "La lista de IDs no puede estar vacía"
        conn = get_db_connection()
        try:
            # Datos de auditoría
            data = {
                'id_list': id_list,
                'operador_registro': current_user,
                'motivo_reemplazo':motivo_reemplazo
            }
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Locadores].[sp_contrato]
                    @accion = 77,
                    @id_list = ?,
                    @estado = ?,
                    @motivo_reemplazo = ?,
                    @fecha_registro = ?,
                    @estacion_registro = ?,
                    @operador_registro = ?
            ''', (
                id_list,
                estado,
                motivo_reemplazo,
                data['fecha_registro'],
                data['estacion_registro'],
                data['operador_registro']
            ))

            conn.commit()
            return True, f"Se actualizaron correctamente {len(id_list.split(','))} contratos"

        except pyodbc.Error as e:
            return False, RegistroLocadorModel._extract_sql_error(e)

        finally:
            conn.close()

