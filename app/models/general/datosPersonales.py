import pyodbc
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class DatosPersonales:
    @staticmethod
    def execute_sp(accion, params=None):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            if accion == 'LIST':
                cursor.execute('''
                    EXEC [dbo].[sp_DatosPersonales] 
                        @accion = ?,
                        @idDatosPersonales = ?,
                        @apellido_paterno = ?,
                        @apellido_materno = ?,
                        @nombres = ?,
                        @idSexo = ?,
                        @idEstadoCivil = ?,
                        @dni = ?,
                        @idDistrito = ?,
                        @flag_terceros = ?
                ''', (
                    accion,
                    params.get('idDatosPersonales'),
                    params.get('apellido_paterno'),
                    params.get('apellido_materno'),
                    params.get('nombres'),
                    params.get('idSexo'),
                    params.get('idEstadoCivil'),
                    params.get('dni'),
                    params.get('idDistrito'),
                    params.get('flag_terceros')
                ))
            else:
                cursor.execute('''
                    EXEC [dbo].[sp_DatosPersonales] 
                        @accion = ?,
                        @idDatosPersonales = ?,
                        @apellido_paterno = ?,
                        @apellido_materno = ?,
                        @nombres = ?,
                        @idSexo = ?,
                        @fecha_nacimiento = ?,
                        @idEstadoCivil = ?,
                        @telefono_fijo = ?,
                        @celular = ?,
                        @dni = ?,
                        @ruc = ?,
                        @idDistrito = ?,
                        @direccion = ?,
                        @email = ?,
                        @foto = ?,
                        @cv = ?,
                        @flag_terceros = ?
                ''', (
                    accion,
                    params.get('idDatosPersonales'),
                    params.get('apellido_paterno'),
                    params.get('apellido_materno'),
                    params.get('nombres'),
                    params.get('idSexo'),
                    params.get('fecha_nacimiento'),
                    params.get('idEstadoCivil'),
                    params.get('telefono_fijo'),
                    params.get('celular'),
                    params.get('dni'),
                    params.get('ruc'),
                    params.get('idDistrito'),
                    params.get('direccion'),
                    params.get('email'),
                    params.get('foto'),
                    params.get('cv'),
                    params.get('flag_terceros', '1')
                ))

            if accion in ['INSERT', 'UPDATE', 'DELETE']:
                conn.commit()
                return True, 'Operación exitosa'
            
            elif accion == 'LIST':
                results = cursor.fetchall()
                data = [dict(zip([column[0] for column in cursor.description], row)) for row in results]
                return {'data': data}
            
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    @staticmethod
    def create_datos_personales(data, current_user, remote_addr):
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return DatosPersonales.execute_sp('INSERT', data)

    @staticmethod
    def update_datos_personales(data, current_user, remote_addr):
        data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
        return DatosPersonales.execute_sp('UPDATE', data)

    @staticmethod
    def delete_datos_personales(idDatosPersonales):
        return DatosPersonales.execute_sp('DELETE', {'idDatosPersonales': idDatosPersonales})

    @staticmethod
    def list_datos_personales(filtros=None):
        filtros = filtros or {}
        return DatosPersonales.execute_sp('LIST', filtros)