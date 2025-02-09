from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc
import re
from datetime import datetime
from config import get_db_connection
from ..utils.audit import AuditFields

class EmpleadoModel:
    @staticmethod
    def create_empleado(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir auditoría a los datos
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Planilla].[sp_Empleados] 
                    @accion = 1,
                    @codEmpleado = ?, 
                    @idCondicionLaboral = ?, 
                    @fecha_ingreso = ?, 
                    @idEstado = ?, 
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
                    @fecha_reg = ?, 
                    @estacion_reg = ?, 
                    @operador_reg = ?,
                    @fecha_act = ?, 
                    @estacion_act = ?, 
                    @operador_act = ?,
                    @flag_estado = 1
            ''', (
                data['codEmpleado'], data['idCondicionLaboral'], datetime.utcnow(), data['idEstado'], 
                data['apellido_paterno'], 
                data['apellido_materno'], data['nombres'], data['idSexo'], 
                data['fecha_nacimiento'], data['idEstadoCivil'], data['telefono_fijo'], 
                data['celular'], data['dni'], data['ruc'], data['idDistrito'], 
                data['direccion'], data['email'], data['foto'], data['fecha_reg'], 
                data['estacion_reg'], data['operador_reg'], data['fecha_act'], 
                data['estacion_act'], data['operador_act']
            ))

            conn.commit()
            return True, 'Empleado registrado con éxito'
        
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar empleado'
        
        finally:
            conn.close()

    @staticmethod
    def update_empleado(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir auditoría a los datos
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)

            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Planilla].[sp_Empleados] 
                    @accion = 2,
                    @idEmpleado = ?, 
                    @codEmpleado = ?, 
                    @idCondicionLaboral = ?, 
                    @idCargo = ?, 
                    @idCentroCosto = ?, 
                    @fecha_ingreso = ?, 
                    @fecha_cese = ?, 
                    @fecha_suspension = ?, 
                    @fecha_reingreso = ?, 
                    @idEstado = ?, 
                    @idMeta = ?, 
                    @descMeta = ?, 
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
                    @fecha_act = ?, 
                    @estacion_act = ?, 
                    @operador_act = ?
            ''', (
                data['idEmpleado'], data['codEmpleado'], data['idCondicionLaboral'], 
                data['idCargo'], data['idCentroCosto'], data['fecha_ingreso'], 
                data['fecha_cese'], data['fecha_suspension'], data['fecha_reingreso'], 
                data['idEstado'], data['idMeta'], data['descMeta'], 
                data['apellido_paterno'], data['apellido_materno'], data['nombres'], 
                data['idSexo'], data['fecha_nacimiento'], data['idEstadoCivil'], 
                data['telefono_fijo'], data['celular'], data['dni'], data['ruc'], 
                data['idDistrito'], data['direccion'], data['email'], 
                data['foto'], data['fecha_act'], data['estacion_act'], 
                data['operador_act']
            ))

            conn.commit()
            return True, 'Empleado actualizado con éxito'
        
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar empleado'
        
        finally:
            conn.close()
    
    @staticmethod
    def update_datosPersonales(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir auditoría a los datos
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)
            fecha_nacimiento = data.get('fecha_nacimiento', None)  # Valor predeterminado: None si no existe
            idEstadoCivil = data.get('idEstadoCivil', None)  # Valor p
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Planilla].[sp_Empleados] 
                    @accion = 4,  -- Usamos la acción 4 para actualizar solo datos personales
                    @idEmpleado = ?, 
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
                    @fecha_act = ?, 
                    @estacion_act = ?, 
                    @operador_act = ?, 
                    @idCondicionLaboral = ?
            ''', (
                data['idEmpleado'], 
                data['apellido_paterno'], 
                data['apellido_materno'], 
                data['nombres'], 
                data['idSexo'], 
                fecha_nacimiento , 
                idEstadoCivil, 
                data['telefono_fijo'], 
                data['celular'], 
                data['dni'], 
                data['ruc'], 
                data['idDistrito'], 
                data['direccion'], 
                data['email'], 
                data['foto'], 
                data['fecha_act'], 
                data['estacion_act'], 
                data['operador_act'], 
                data['idCondicionLaboral']
            ))

            conn.commit()
            return True, 'Datos personales del empleado actualizados con éxito'
        
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar empleado'
        
        finally:
            conn.close()


    @staticmethod
    def get_empleados_filtrar(filtros, current_page, per_page):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Planilla].[sp_Empleados] 
                    @accion = 3,
                    @estado = ?,
                    @cargo = ?,
                    @condicionLaboral = ?,
                    @nombreApellido = ?,
                    @centroCosto = ?,
                    @current_page = ?,
                    @per_page = ?
            ''', (
                filtros.get('estado', None), 
                filtros.get('cargo', None), 
                filtros.get('condicionLaboral', None),
                filtros.get('nombreApellido', None), 
                filtros.get('centroCosto', None), 
                current_page, 
                per_page
            ))

            empleados = cursor.fetchall()

            # Convertir los resultados a una lista de diccionarios
            return [{
                'idEmpleado': e[0],
                'codEmpleado': e[1],
                'fecha_ingreso': e[2],
                'fecha_cese': e[3],
                'fecha_suspension': e[4],
                'fecha_reingreso': e[5],
                'idEstado': e[6],
                'idMeta': e[7],
                'descMeta': e[8],
                'idDatosPersonales': e[9],
                'apellido_paterno': e[10],
                'apellido_materno': e[11],
                'nombres': e[12],
                'dni': e[13],
                'telefono_fijo': e[14],
                'celular': e[15],
                'email': e[16],
                'centroCosto_nombre': e[17],
                'condicionLaboral_nombre': e[18],
                'cargo_nombre': e[19],
                'estado': e[20],
                'current_page': e[21],
                'last_page': e[22],
                'per_page': e[23],
                'total': e[24],
                'idCargo': e[25],
                'idCondicionLaboral': e[26],
                'ruc': e[27],
                'idSexo': e[28],
                'idDistrito': e[29],
                'idEmpleado': e[30],
                'idCentroCosto': e[31],
                'fecha_ingreso': e[32],
                'fecha_cese': e[30],
                'fecha_suspension': e[31],
                'fecha_reingreso': e[32],
                'direccion': e[33],
                'foto': e[34],
            } for e in empleados]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return {'error': matches.group(1).strip() if matches else 'Error al obtener empleados'}
        
        finally:
            conn.close()


    @staticmethod
    def update_empleado(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir auditoría a los datos
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)
            
            # Extraer los datos de la solicitud
            idEmpleado = data.get('idEmpleado', None)
            idCondicionLaboral = data.get('idCondicionLaboral', None)
            idCargo = data.get('idCargo', None)
            idCentroCosto = data.get('idCentroCosto', None)
            fecha_ingreso = data.get('fecha_ingreso', None)
            fecha_cese = data.get('fecha_cese', None)
            fecha_suspension = data.get('fecha_suspension', None)
            fecha_reingreso = data.get('fecha_reingreso', None)
            idEstado = data.get('idEstado', None)
            idMeta = data.get('idMeta', None)
            descMeta = data.get('descMeta', None)
            flag_estado = data.get('flag_estado', None)
            
            # Cursor para ejecutar el procedimiento almacenado
            cursor = conn.cursor()

            cursor.execute('''
                EXEC [Planilla].[sp_Empleados] 
                    @accion = 5,  -- Usamos la acción 5 para actualizar los datos en Planilla.Empleado
                    @idEmpleado = ?, 
                    @codEmpleado = ?, 
                    @idCondicionLaboral = ?, 
                    @idCargo = ?, 
                    @idCentroCosto = ?, 
                    @fecha_ingreso = ?, 
                    @fecha_cese = ?, 
                    @fecha_suspension = ?, 
                    @fecha_reingreso = ?, 
                    @idEstado = ?, 
                    @idMeta = ?, 
                    @descMeta = ?, 
                    @flag_estado = ?, 
                    @idDatosPersonales = ?  -- Este campo lo estamos pasando como parte de los datos
            ''', (
                data['idEmpleado'],
                data['codEmpleado'], 
                idCondicionLaboral, 
                idCargo, 
                idCentroCosto, 
                fecha_ingreso, 
                fecha_cese, 
                fecha_suspension, 
                fecha_reingreso, 
                idEstado, 
                idMeta, 
                descMeta, 
                flag_estado,
                data['idDatosPersonales']  # Asegúrate de pasar este campo si es necesario
            ))

            # Confirmar los cambios en la base de datos
            conn.commit()
            return True, 'Datos del empleado actualizados con éxito'
        
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar empleado'
        
        finally:
            conn.close()

    
    @staticmethod
    def get_empleados_datosLaborales(filtros):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC Planilla.sp_DatosLaborales
                    @accion = 1,  -- Acción para obtener datos de empleado
                    @idDatosPersonales = ?, -- Filtro opcional por idDatosPersonales
                    @flag_estado = ?  -- Filtro por flag_estado
            ''', (
                filtros.get('idDatosPersonales', None),  # Filtro por idDatosPersonales
                filtros.get('flag_estado', 1)  # Predeterminado a 1 (activo)
            ))

            empleados = cursor.fetchall()

            # Convertir los resultados a una lista de diccionarios
            return [{
                'idEmpleado': e[0],
                'codEmpleado': e[1],
                'idCondicionLaboral': e[2],
                'idCargo': e[3],
                'idCentroCosto': e[4],
                'fecha_ingreso': e[5],
                'fecha_cese': e[6],
                'fecha_suspension': e[7],
                'fecha_reingreso': e[8],
                'idEstado': e[9],
                'idMeta': e[10],
                'descMeta': e[11],
                'idDatosPersonales': e[12],
                'flag_estado': e[13],
                # Nuevas columnas
                'idSede': e[14],
                'idsubcentro': e[15],
                'nro_resolucion': e[16],
                'fecha_resolucion': e[17],
                'codigoRegimenPensionarioSUNAT': e[18],
                'idTipoComisionAFP': e[19],
                'cuspp': e[20],
                'idBanco': e[21],
                'nrocta': e[22],
                'Id_meta': e[23],
                'Id_actividad': e[24],
                'Id_clasificador': e[25],
                'Id_nivel': e[26],
                'fecha_registro': e[27],
                'estacion_registro': e[28],
                'operador_registro': e[29],
                'fecha_modificacion': e[30],
                'estacion_modificacion': e[31],
                'operador_modificacion': e[32]
            } for e in empleados]

        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return {'error': matches.group(1).strip() if matches else 'Error al obtener empleados'}
        
        finally:
            conn.close()



