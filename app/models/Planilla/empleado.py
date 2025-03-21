from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc
import re
from datetime import datetime
from config import get_db_connection
from ..utils.audit import AuditFields
from ...utils.auditv2 import AuditFieldsv2
from ..utils.convertir_a_fecha_sql import convertir_a_fecha_sql
import os
from dotenv import load_dotenv
import pytz

# Cargar variables desde el archivo .env
load_dotenv()

# Obtener la zona horaria desde .env (por defecto America/Lima)
TIMEZONE = os.getenv('APP_TIMEZONE', 'America/Lima')
tz = pytz.timezone(TIMEZONE)

class EmpleadoModel:
    @staticmethod
    def create_empleado(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            fecha_nacimiento = data.get('fecha_nacimiento', None)
            
            if fecha_nacimiento == "":
                print(data)
                fecha_nacimiento = None
            
            # Añadir auditoría a los datos
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)
                    
            current_date = datetime.now(tz)  # Usar la zona horaria configurada
        
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
                    @flag_estado = 1,
                    @flag_terceros = ?
                    
            ''', (
                data['codEmpleado'], data['idCondicionLaboral'], current_date.strftime('%Y-%m-%d %H:%M:%S'), data['idEstado'], 
                data['apellido_paterno'], 
                data['apellido_materno'], data['nombres'], data['idSexo'], 
                fecha_nacimiento, data['idEstadoCivil'], data['telefono_fijo'], 
                data['celular'], data['dni'], data['ruc'], data['idDistrito'], 
                data['direccion'], data['email'], data['foto'], data['fecha_reg'], 
                data['estacion_reg'], data['operador_reg'], data['fecha_act'], 
                data['estacion_act'], data['operador_act'], data['flag_terceros']
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
    def update_empleado2(data, current_user, remote_addr):
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
            return True, 'Empleado registrado con éxito'
        
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar empleado'
        
        finally:
            conn.close()
    
    @staticmethod
    def update_datosPersonales(data, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Add audit fields to the data
            data = AuditFields.add_audit_fields(data, current_user, remote_addr)
            
            fecha_nacimiento = data.get('fecha_nacimiento', None)  # Default to None if not present
            idEstadoCivil = data.get('idEstadoCivil', None)  # Default to None if not present
            
            print(f"Executing stored procedure with data: {data}")  # Debug: print data to be sent
            
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [Planilla].[sp_Empleados] 
                    @accion = 4,  -- Action 4 for updating only personal data
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
                fecha_nacimiento, 
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
            return True, 'Datos Personales actualizados Correctamente'
        
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al registrar empleado'
        
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
                    @dni = ?,
                    @condicionLaboral = ?,
                    @nombreApellido = ?,
                    @centroCosto = ?,
                    @current_page = ?,
                    @per_page = ?
            ''', (
                filtros.get('estado', None), 
                filtros.get('cargo', None), 
                filtros.get('dni', None), 
                filtros.get('condicionLaboral', None),
                filtros.get('nombreApellido', None), 
                filtros.get('centroCosto', None), 
                current_page, 
                per_page
            ))

            empleados = cursor.fetchall()

            # Convertir los resultados a una lista de diccionarios
            return [{
                # Datos de la tabla de empleados
                'idEmpleado': e[0],
                'codEmpleado': e[1],
                'fecha_ingreso': e[2],
                'fecha_cese': e[3],
                'fecha_suspension': e[4],
                'fecha_reingreso': e[5],
                'idEstado': e[6],
                'idMeta': e[7],
                'descMeta': e[8],

                # Datos de DatosPersonales
                'idDatosPersonales': e[9],
                'apellido_paterno': e[10],
                'apellido_materno': e[11],
                'nombres': e[12],
                'dni': e[13],
                'telefono_fijo': e[14],
                'celular': e[15],
                'email': e[16],
                'ruc': e[17],
                'idSexo': e[18],
                'idDistrito': e[19],
                'fecha_nacimiento': e[20],
                'direccion': e[21],
                'foto': e[22],

                # Datos de tblCentroCosto (nombre del centro de costo)
                'centroCosto_nombre': e[23],

                # Datos de tblCondicionLaboral (nombre de la condición laboral)
                'condicionLaboral_nombre': e[24],

                # Datos de tblCargo (nombre del cargo)
                'cargo_nombre': e[25],

                # Estado de empleado
                'estado': e[26],

                # Información de paginación
                'current_page': e[27],
                'last_page': e[28],
                'per_page': e[29],
                'total': e[30],

                # Relaciones adicionales
                'idCargo': e[31],
                'idCondicionLaboral': e[32],
                'idCentroCosto': e[33],
                'idEstadoCivil':e[34]
            } for e in empleados]


        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return {'error': matches.group(1).strip() if matches else 'Error al obtener empleados'}
        
        finally:
            conn.close()

    @staticmethod
    def update_empleado(data, current_user, remote_addr):
        print("update_empleado correcto")
        print(data)
        conn = get_db_connection()
        try:
            # Añadir auditoría a los datos
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
            
            # Extraer los datos de la solicitud
            idEmpleado = data.get('idEmpleado', None)
            codEmpleado = data.get('codEmpleado', None)
            idCondicionLaboral = data.get('idCondicionLaboral', None)
            idCargo = data.get('idCargo', None)
            idCentroCosto = data.get('idCentroCosto', None)
            idMeta = data.get('idMeta', None)
            descMeta = data.get('descMeta', None)
            flag_estado = data.get('flag_estado', None)
            idDatosPersonales = data.get('idDatosPersonales', None)
            
            # Nuevos campos añadidos
            idSede = data.get('idSede', None)
            idsubcentro = data.get('idsubcentro', None)
            nro_resolucion = data.get('nro_resolucion', None)
            # Obtener las fechas de la data
            fecha_ingreso = data.get('fecha_ingreso', None)
            fecha_cese = data.get('fecha_cese', None)
            fecha_resolucion = data.get('fecha_resolucion', None)

            # Convertir las fechas a formato SQL en la zona horaria de Perú
            print(fecha_ingreso)
            fecha_ingreso_sql = convertir_a_fecha_sql(fecha_ingreso)
            print(fecha_ingreso)
            fecha_cese_sql = convertir_a_fecha_sql(fecha_cese)
            fecha_resolucion_sql = convertir_a_fecha_sql(fecha_resolucion)
            codigoRegimenPensionarioSUNAT = data.get('codigoRegimenPensionarioSUNAT', None)
            idTipoComisionAFP = data.get('idTipoComisionAFP', None)
            cuspp = data.get('cuspp', None)
            idBanco = data.get('idBanco', None)
            nrocta = data.get('nrocta', None)
            Id_meta = data.get('Id_meta', None)
            Id_actividad = data.get('Id_actividad', None)
            Id_clasificador = data.get('Id_clasificador', None)
            Id_nivel = data.get('Id_nivel', None)
            
            # Cursor para ejecutar el procedimiento almacenado
            cursor = conn.cursor()
            
            cursor.execute('''
                EXEC [Planilla].[sp_DatosLaborales]
                    @Accion = 5,
                    @idDatosPersonales = ?,
                    @flag_estado = ?,
                    @idCondicionLaboral = ?,
                    @idCargo = ?,
                    @idCentroCosto = ?,
                    @idMeta = ?,
                    @descMeta = ?,
                    @codEmpleado = ?,
                    @idSede = ?,
                    @idsubcentro = ?,
                    @nro_resolucion =?,
                    @fecha_ingreso =?,
                    @fecha_cese =?,
                    @fecha_resolucion = ?,
                    @codigoRegimenPensionarioSUNAT = ?,
                    @idTipoComisionAFP = ?,
                    @cuspp = ?,
                    @idBanco = ?,
                    @nrocta = ?,
                    @Id_meta = ?,
                    @Id_actividad = ?,
                    @Id_clasificador = ?,
                    @Id_nivel = ?
            ''', (
                idDatosPersonales,
                flag_estado,
                idCondicionLaboral,
                idCargo,
                idCentroCosto,
                idMeta,
                descMeta,
                codEmpleado,
                idSede,
                idsubcentro,
                nro_resolucion,
                fecha_ingreso_sql,
                fecha_cese_sql,
                fecha_resolucion_sql,
                codigoRegimenPensionarioSUNAT,
                idTipoComisionAFP,
                cuspp,
                idBanco,
                nrocta,
                Id_meta,
                Id_actividad,
                Id_clasificador,
                Id_nivel
            ))
            
            # Confirmar los cambios en la base de datos
            conn.commit()
            return True, 'Datos del empleado actualizados con éxito'
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() 
            
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

    @staticmethod
    def update_estado_empleado(idEmpleado,idNuevoEstado, current_user, remote_addr):
        conn = get_db_connection()
        try:
            # Añadir auditoría a los datos
            data={};
            # Si tienes una función para añadir campos de auditoría, puedes agregarla aquí
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
            cursor = conn.cursor()
            print(data)
            cursor.execute('''
                EXEC [Planilla].[sp_Empleados] 
                @accion = 6, 
                    @idEstado = ?, 
                    @idEmpleado = ?, 
                    @fecha_modificacion = ?, 
                    @estacion_modificacion = ?, 
                    @operador_modificacion = ?
            ''', (
                idNuevoEstado, 
                idEmpleado,
                data['fecha_modificacion'],       # Nueva fecha de modificación
                data['estacion_modificacion'],    # Estación de modificación
                data['operador_modificacion']     # Operador de la modificación
            ))

            conn.commit()
            return True, 'Estado del empleado actualizado con éxito'
        
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            return False, matches.group(1).strip() if matches else 'Error al actualizar el estado del empleado'
        
        finally:
            conn.close()
