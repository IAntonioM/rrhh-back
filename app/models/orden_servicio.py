import pyodbc
from config import get_db_connection
from ..utils.auditv2 import AuditFieldsv2

class OrdenServicio:
    @staticmethod
    def execute_sp(accion, params=None):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            if accion == 'SELECT':
                cursor.execute('''
                    EXEC [dbo].[sp_orden_servicio] 
                        @accion = ?, 
                        @id = ?, 
                        @id_empleado = ?, 
                        @id_cargo = ?, 
                        @id_area = ?
                ''', (
                    accion,
                    params.get('id'),
                    params.get('id_empleado'),
                    params.get('id_cargo'),
                    params.get('id_area')
                ))
            else:
                cursor.execute('''
                    EXEC [dbo].[sp_orden_servicio] 
                        @accion = ?, 
                        @id = ?, 
                        @id_empleado = ?, 
                        @id_cargo = ?, 
                        @id_area = ?, 
                        @descripcion = ?, 
                        @fecha_inicio = ?, 
                        @fecha_termino = ?, 
                        @monto = ?, 
                        @estado = ?, 
                        @usuario = ?, 
                        @estacion = ?
                ''', (
                    accion,
                    params.get('id'),
                    params.get('id_empleado'),
                    params.get('id_cargo'),
                    params.get('id_area'),
                    params.get('descripcion'),
                    params.get('fecha_inicio'),
                    params.get('fecha_termino'),
                    params.get('monto'),
                    params.get('estado', '1'),
                    params.get('usuario'),
                    params.get('estacion')
                ))

            if accion in ['INSERT', 'UPDATE', 'DELETE']:
                conn.commit()
                return {'success': True, 'message': 'Operación exitosa'}
            
            elif accion == 'SELECT':
                results = cursor.fetchall()
                if not results:
                    return {'data': []}
                
                data = [dict(zip([column[0] for column in cursor.description], row)) for row in results]
                return {'data': data}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
        finally:
            conn.close()

    @staticmethod
    @staticmethod
    def create_orden_servicio(data, current_user, remote_addr):
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        
        # Asegurándonos de que los campos de auditoría estén correctamente mapeados
        if 'usuario_creacion' not in data and 'usuario' in data:
            data['usuario_creacion'] = data['usuario']
        elif 'usuario_creacion' not in data:
            data['usuario_creacion'] = current_user
            
        if 'estacion_creacion' not in data and 'estacion' in data:
            data['estacion_creacion'] = data['estacion']
        elif 'estacion_creacion' not in data:
            data['estacion_creacion'] = remote_addr
        
        # Mapear campos de auditoría a los parámetros del SP
        data['usuario'] = data.get('usuario_creacion', current_user)
        data['estacion'] = data.get('estacion_creacion', remote_addr)
        
        return OrdenServicio.execute_sp('INSERT', data)

    @staticmethod
    def update_orden_servicio(data, current_user, remote_addr):
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return OrdenServicio.execute_sp('UPDATE', data)

    @staticmethod
    def delete_orden_servicio(id, current_user, remote_addr):
        data = {
            'id': id,
            'estado': '0'
        }
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return OrdenServicio.execute_sp('DELETE', data)

    @staticmethod
    def get_orden_servicio(filtros=None):
        filtros = filtros or {}
        return OrdenServicio.execute_sp('SELECT', filtros)