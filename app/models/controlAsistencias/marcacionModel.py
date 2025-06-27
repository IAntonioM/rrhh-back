import pyodbc
from config import get_db_connection
from ...utils.auditv2 import AuditFieldsv2

class Marcaciones:
    @staticmethod
    def execute_sp_consulta_directa(params):
        """
        Ejecuta la consulta de marcaciones directamente sin usar el SP dinámico
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Construir la consulta base
            base_query = """
                SELECT 
                    m.idMarcacion,
                    e.idCentroCosto,
                    cc.centro_costo,
                    e.idcargo,
                    tc.cargo,
                    m.dni,
                    (dp.apellido_paterno + ' ' + dp.apellido_materno) as apellidos,
                    dp.nombres,
                    CONVERT(char(10), m.fecha_hora, 103) as fecha,
                    CONVERT(char(8), m.fecha_hora, 108) as hora,
                    m.flag_manual,
                    m.id_marca_movil,
                    m.observacion,
                    m.fecha_registro
                FROM marcacion m
                LEFT JOIN datosPersonales dp ON dp.dni = m.dni
                LEFT JOIN Planilla.empleado e ON dp.idDatosPersonales = e.idDatosPersonales
                LEFT JOIN tblCentroCosto cc ON cc.idCentroCosto = e.idCentroCosto
                LEFT JOIN tblCargo tc ON tc.idCargo = e.idCargo
                WHERE m.flag_estado = 1
            """
            
            # Construir condiciones WHERE dinámicamente
            conditions = []
            query_params = []
            
            # Filtros de fecha
            if params.get('deFecha') and params['deFecha'] != '1900-01-01':
                conditions.append("m.fecha_hora >= ?")
                query_params.append(params['deFecha'])
            
            if params.get('hastaFecha') and params['hastaFecha'] != '1900-01-01':
                conditions.append("m.fecha_hora < ?")
                # Agregar un día para incluir todo el día final
                from datetime import datetime, timedelta
                hasta_fecha = datetime.strptime(params['hastaFecha'], '%Y-%m-%d')
                hasta_fecha += timedelta(days=1)
                query_params.append(hasta_fecha.strftime('%Y-%m-%d'))
            
            # Filtros adicionales
            if params.get('idArea') and params['idArea'] != '':
                conditions.append("e.idCentroCosto = ?")
                query_params.append(params['idArea'])
            
            if params.get('idCargo') and params['idCargo'] != '':
                conditions.append("e.idcargo = ?")
                query_params.append(params['idCargo'])
            
            if params.get('dni') and params['dni'] != '':
                conditions.append("m.dni = ?")
                query_params.append(params['dni'])
            
            if params.get('nombres') and params['nombres'] != '':
                conditions.append("(ISNULL(dp.nombres, '') + ISNULL(dp.apellido_paterno, '') + ISNULL(dp.apellido_materno, '')) LIKE ?")
                nombres_pattern = '%' + params['nombres'].replace(' ', '%') + '%'
                query_params.append(nombres_pattern)
            
            # Agregar condiciones WHERE
            if conditions:
                base_query += " AND " + " AND ".join(conditions)
            
            # Agregar ordenamiento
            base_query += " ORDER BY m.fecha_hora DESC"
            
            # Agregar paginación si se especifica
            if params.get('inicio', 0) != 0 and params.get('final', 0) != 0:
                base_query += f" OFFSET {params['inicio'] - 1} ROWS FETCH NEXT {params['final'] - params['inicio'] + 1} ROWS ONLY"
            
            print(f"DEBUG: Ejecutando consulta: {base_query}")
            print(f"DEBUG: Parámetros: {query_params}")
            
            cursor.execute(base_query, query_params)
            results = cursor.fetchall()
            columns = [column[0] for column in cursor.description] if cursor.description else []
            data = [dict(zip(columns, row)) for row in results] if columns else []
            
            return {'data': data}
            
        except pyodbc.Error as e:
            print(f"DEBUG: Error de pyodbc en consulta: {e}")
            return {'success': False, 'message': f'Error de base de datos: {str(e)}'}
        except Exception as e:
            print(f"DEBUG: Error general en consulta: {e}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def execute_sp_count_directa(params):
        """
        Ejecuta el conteo de marcaciones directamente sin usar el SP dinámico
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Construir la consulta de conteo
            base_query = """
                SELECT COUNT(*) as total
                FROM marcacion m
                LEFT JOIN datosPersonales dp ON dp.dni = m.dni
                LEFT JOIN Planilla.empleado e ON dp.idDatosPersonales = e.idDatosPersonales
                LEFT JOIN tblCentroCosto cc ON cc.idCentroCosto = e.idCentroCosto
                LEFT JOIN tblCargo tc ON tc.idCargo = e.idCargo
                WHERE m.flag_estado = 1
            """
            
            # Construir condiciones WHERE dinámicamente
            conditions = []
            query_params = []
            
            # Filtros de fecha
            if params.get('deFecha') and params['deFecha'] != '1900-01-01':
                conditions.append("m.fecha_hora >= ?")
                query_params.append(params['deFecha'])
            
            if params.get('hastaFecha') and params['hastaFecha'] != '1900-01-01':
                conditions.append("m.fecha_hora < ?")
                # Agregar un día para incluir todo el día final
                from datetime import datetime, timedelta
                hasta_fecha = datetime.strptime(params['hastaFecha'], '%Y-%m-%d')
                hasta_fecha += timedelta(days=1)
                query_params.append(hasta_fecha.strftime('%Y-%m-%d'))
            
            # Filtros adicionales
            if params.get('idArea') and params['idArea'] != '':
                conditions.append("e.idCentroCosto = ?")
                query_params.append(params['idArea'])
            
            if params.get('idCargo') and params['idCargo'] != '':
                conditions.append("e.idcargo = ?")
                query_params.append(params['idCargo'])
            
            if params.get('dni') and params['dni'] != '':
                conditions.append("m.dni = ?")
                query_params.append(params['dni'])
            
            if params.get('nombres') and params['nombres'] != '':
                conditions.append("(ISNULL(dp.nombres, '') + ISNULL(dp.apellido_paterno, '') + ISNULL(dp.apellido_materno, '')) LIKE ?")
                nombres_pattern = '%' + params['nombres'].replace(' ', '%') + '%'
                query_params.append(nombres_pattern)
            
            # Agregar condiciones WHERE
            if conditions:
                base_query += " AND " + " AND ".join(conditions)
            
            print(f"DEBUG: Ejecutando conteo: {base_query}")
            print(f"DEBUG: Parámetros: {query_params}")
            
            cursor.execute(base_query, query_params)
            result = cursor.fetchone()
            total = result[0] if result else 0
            
            return {'total': total}
            
        except pyodbc.Error as e:
            print(f"DEBUG: Error de pyodbc en conteo: {e}")
            return {'success': False, 'message': f'Error de base de datos: {str(e)}'}
        except Exception as e:
            print(f"DEBUG: Error general en conteo: {e}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def execute_sp(mquery, params=None):
        """
        Ejecuta el stored procedure SP_MARCACIONES con diferentes tipos de operaciones
        
        Args:
            mquery (int): Tipo de operación (1=insertar, 4=consultar, 5=contar)
            params (dict): Parámetros para el stored procedure
            
        Returns:
            dict: Resultado de la operación
        """
        if mquery == 4:  # Consultar marcaciones - usar método directo
            return Marcaciones.execute_sp_consulta_directa(params or {})
        elif mquery == 5:  # Contar marcaciones - usar método directo
            return Marcaciones.execute_sp_count_directa(params or {})
        elif mquery == 1:  # Insertar marcación - usar SP
            return Marcaciones.execute_sp_insert_simple(params or {})
        else:
            return {'success': False, 'message': 'Tipo de consulta no válida'}

    @staticmethod
    def execute_sp_insert_simple(params):
        """
        Método simplificado para insertar marcación sin intentar obtener el resultado del SELECT
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            print(f"DEBUG: Insertando marcación con parámetros: {params}")
            
            # Ejecutar el SP
            cursor.execute('''
                EXEC [dbo].[SP_MARCACIONES]
                    @mquery = 1,
                    @fechaMarcacion = ?,
                    @horaMarcacion = ?,
                    @idEmpleado = ?,
                    @observacion = ?,
                    @estacion = ?,
                    @operador = ?
            ''', (
                params.get('fechaMarcacion'),
                params.get('horaMarcacion'),
                params.get('idEmpleado'),
                params.get('observacion', ''),
                params.get('estacion', ''),
                params.get('operador', '')
            ))
            
            # Commit sin intentar fetchone
            conn.commit()
            print("DEBUG: SP ejecutado y confirmado")
            
            # Verificar que se insertó correctamente
            cursor.execute("""
                SELECT TOP 1 idMarcacion 
                FROM marcacion 
                WHERE idEmpleado = ? 
                AND CONVERT(date, fecha_hora) = CONVERT(date, ?)
                AND CONVERT(time, fecha_hora) = CONVERT(time, ?)
                ORDER BY fecha_registro DESC
            """, (
                params.get('idEmpleado'),
                params.get('fechaMarcacion'),
                params.get('horaMarcacion') + ':00'  # Agregar segundos
            ))
            
            verification = cursor.fetchone()
            if verification:
                print(f"DEBUG: Marcación verificada con ID: {verification[0]}")
                return {'success': True, 'message': 'MARCACIÓN REGISTRADA CORRECTAMENTE.'}
            else:
                print("DEBUG: No se pudo verificar la inserción")
                return {'success': False, 'message': 'Error al verificar la marcación registrada'}
                
        except pyodbc.Error as e:
            print(f"DEBUG: Error de pyodbc: {e}")
            conn.rollback()
            return {'success': False, 'message': f'Error de base de datos: {str(e)}'}
        except Exception as e:
            print(f"DEBUG: Error general: {e}")
            conn.rollback()
            return {'success': False, 'message': f'Error interno: {str(e)}'}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def registrar_marcacion(data, current_user, remote_addr):
        """
        Registra una nueva marcación usando el método simplificado
        """
        try:
            # Validaciones básicas
            required_fields = ['fechaMarcacion', 'horaMarcacion', 'idEmpleado']
            for field in required_fields:
                if not data.get(field):
                    return {'success': False, 'message': f'El campo {field} es requerido'}
            
            # Agregamos campos de auditoría
            data = AuditFieldsv2.add_audit_fields(data, current_user, remote_addr)
            
            # Asignamos valores para el stored procedure
            params = {
                'fechaMarcacion': data.get('fechaMarcacion'),
                'horaMarcacion': data.get('horaMarcacion'),
                'idEmpleado': int(data.get('idEmpleado')),
                'observacion': data.get('observacion', ''),
                'estacion': data.get('estacion', remote_addr),
                'operador': data.get('operador', current_user)
            }
            
            # Usar el método simplificado
            print(f"DEBUG: Usando método simplificado para inserción...")
            result = Marcaciones.execute_sp_insert_simple(params)
            
            return result
            
        except ValueError as e:
            return {'success': False, 'message': f'Error en los datos: {str(e)}'}
        except Exception as e:
            return {'success': False, 'message': f'Error interno: {str(e)}'}

    @staticmethod
    def listar_marcaciones(filtros=None):
        """
        Lista marcaciones con filtros opcionales
        """
        if filtros is None:
            filtros = {}
            
        params = {
            'deFecha': filtros.get('deFecha', '1900-01-01'),
            'hastaFecha': filtros.get('hastaFecha', '1900-01-01'),
            'idArea': filtros.get('idArea', ''),
            'idCargo': filtros.get('idCargo', ''),
            'dni': filtros.get('dni', ''),
            'nombres': filtros.get('nombres', ''),
            'inicio': int(filtros.get('inicio', 0)),
            'final': int(filtros.get('final', 0))
        }
        
        return Marcaciones.execute_sp(4, params)

    @staticmethod
    def contar_marcaciones(filtros=None):
        """
        Cuenta el total de marcaciones con filtros opcionales
        """
        if filtros is None:
            filtros = {}
            
        params = {
            'deFecha': filtros.get('deFecha', '1900-01-01'),
            'hastaFecha': filtros.get('hastaFecha', '1900-01-01'),
            'idArea': filtros.get('idArea', ''),
            'idCargo': filtros.get('idCargo', ''),
            'dni': filtros.get('dni', ''),
            'nombres': filtros.get('nombres', '')
        }
        
        return Marcaciones.execute_sp(5, params)

    