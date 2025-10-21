import pyodbc
from config import get_db_connection
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv

load_dotenv()
APP_TIMEZONE = os.getenv('APP_TIMEZONE', 'UTC')
timezone = pytz.timezone(APP_TIMEZONE)

class Periodo:
    @staticmethod
    def execute_sp(accion, params):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_periodo]
                    @accion = ?,
                    @id = ?,
                    @anio = ?,
                    @mes = ?,
                    @idEstado = ?,
                    @fecha_reg = ?,
                    @operador_reg = ?,
                    @estacion_reg = ?,
                    @fecha_act = ?,
                    @estacion_act = ?,
                    @current_page = ?,
                    @per_page = ?
            ''', (
                accion,
                params.get('id'),
                params.get('anio'),
                params.get('mes'),
                params.get('idEstado'),
                params.get('fecha_reg'),
                params.get('operador_reg'),
                params.get('estacion_reg'),
                params.get('fecha_act'),
                params.get('estacion_act'),
                params.get('current_page', 1),
                params.get('per_page', 10)
            ))
            
            if accion in [1, 2, 4]:  # CREATE, UPDATE, DELETE
                conn.commit()
                
                # Intentar obtener el resultado si existe
                try:
                    if cursor.description:  # Verifica si hay columnas (hay un SELECT)
                        result = cursor.fetchone()
                        message = result[0] if result else 'Operación exitosa'
                    else:
                        # No hay resultado, asignar mensaje por defecto
                        if accion == 1:
                            message = 'Periodo creado exitosamente'
                        elif accion == 2:
                            message = 'Periodo actualizado exitosamente'
                        elif accion == 4:
                            message = 'Estado actualizado exitosamente'
                except Exception:
                    # Si falla el fetch, usar mensaje por defecto
                    if accion == 1:
                        message = 'Periodo creado exitosamente'
                    elif accion == 2:
                        message = 'Periodo actualizado exitosamente'
                    elif accion == 4:
                        message = 'Estado actualizado exitosamente'
                
                return {
                    'success': True,
                    'message': message
                }
            else:  # Para LIST (accion = 3)
                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()
                
                if not results:
                    return {
                        'success': True,
                        'data': [],
                        'pagination': {
                            'current_page': params.get('current_page', 1),
                            'last_page': 1,
                            'per_page': params.get('per_page', 10),
                            'total': 0
                        }
                    }
                
                # Convertir los resultados a diccionario
                data = []
                pagination = {}
                
                for row in results:
                    row_dict = {}
                    for i, value in enumerate(row):
                        column_name = columns[i]
                        if column_name in ['current_page', 'last_page', 'per_page', 'total']:
                            pagination[column_name] = value
                        else:
                            row_dict[column_name] = value
                    data.append(row_dict)
                
                return {
                    'success': True,
                    'data': data,
                    'pagination': pagination
                }
        
        except Exception as e:
            print(f"Error en execute_sp: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
        finally:
            conn.close()
    
    @staticmethod
    def add_audit_fields_periodo(data, current_user, remote_addr, is_create=True):
        """Agrega los campos de auditoría específicos para periodo"""
        current_date = datetime.now(timezone)
        fecha_formateada = current_date.strftime('%Y-%m-%d %H:%M:%S')
        
        if is_create:
            # Para CREATE (acción 1)
            data.update({
                'fecha_reg': fecha_formateada,
                'operador_reg': current_user,
                'estacion_reg': remote_addr,
                'fecha_act': fecha_formateada,
                'estacion_act': remote_addr
            })
        else:
            # Para UPDATE (acción 2)
            data.update({
                'fecha_act': fecha_formateada,
                'estacion_act': remote_addr
            })
        
        return data
    
    @staticmethod
    def create_periodo(data, current_user, remote_addr):
        data = Periodo.add_audit_fields_periodo(data, current_user, remote_addr, is_create=True)
        result = Periodo.execute_sp(1, data)
        return result.get('success'), result.get('message')
    
    @staticmethod
    def update_periodo(data, current_user, remote_addr):
        data = Periodo.add_audit_fields_periodo(data, current_user, remote_addr, is_create=False)
        result = Periodo.execute_sp(2, data)
        return result.get('success'), result.get('message')
    
    @staticmethod
    def list_periodos(filtros=None):
        filtros = filtros or {}
        return Periodo.execute_sp(3, filtros)
    
    @staticmethod
    def change_status_periodo(id_periodo, estado):
        result = Periodo.execute_sp(4, {'id': id_periodo, 'idEstado': estado})
        return result.get('success'), result.get('message')