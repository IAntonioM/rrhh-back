import pyodbc
import re
from config import get_db_connection

class ReportesAsistenciaModel:
    
    @staticmethod
    def get_reporte_asistencia_diaria(fecha_inicio=None, fecha_fin=None):
        """
        REPORTE 1: Asistencia Diaria Detallada
        Muestra el detalle de asistencia diaria de todos los empleados
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_ReportesAsistencia] 
                    @TipoReporte = 1,
                    @FechaInicio = ?,
                    @FechaFin = ?
            ''', (fecha_inicio, fecha_fin))
            
            rows = cursor.fetchall()
            
            return [{
                'empleado': row[0],
                'dni': row[1],
                'fecha': row[2],
                'dia_semana': row[3],
                'estado_marcacion': row[4],
                'hora_marcacion': row[5],
                'estacion': row[6],
                'observacion': row[7]
            } for row in rows]
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            raise Exception(matches.group(1).strip() if matches else 'Error al obtener reporte de asistencia diaria')
        finally:
            conn.close()

    @staticmethod
    def get_reporte_resumen_mensual(mes=None, anio=None):
        """
        REPORTE 2: Resumen Mensual de Asistencias por Empleado
        Muestra un resumen del mes con días asistidos, faltados, tardanzas, etc.
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_ReportesAsistencia] 
                    @TipoReporte = 2,
                    @Mes = ?,
                    @Anio = ?
            ''', (mes, anio))
            
            rows = cursor.fetchall()
            
            return [{
                'empleado': row[0],
                'dni': row[1],
                'dias_asistidos': row[2],
                'dias_faltados': row[3],
                'llegadas_tarde': row[4],
                'hora_mas_temprana': row[5],
                'hora_mas_tarde': row[6],
                'id_cargo': row[7],
                'salario': float(row[8]) if row[8] else 0,
                'porcentaje_asistencia': float(row[9]) if row[9] else 0
            } for row in rows]
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            raise Exception(matches.group(1).strip() if matches else 'Error al obtener resumen mensual')
        finally:
            conn.close()

    @staticmethod
    def get_reporte_marcaciones_irregulares(fecha_inicio=None, fecha_fin=None):
        """
        REPORTE 3: Empleados con Marcaciones Irregulares
        Detecta marcaciones múltiples, muy tempranas, muy tardías o únicas
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_ReportesAsistencia] 
                    @TipoReporte = 3,
                    @FechaInicio = ?,
                    @FechaFin = ?
            ''', (fecha_inicio, fecha_fin))
            
            rows = cursor.fetchall()
            
            return [{
                'empleado': row[0],
                'dni': row[1],
                'fecha': row[2],
                'cantidad_marcaciones': row[3],
                'todas_las_horas': row[4],
                'tipo_anomalia': row[5],
                'estacion': row[6],
                'observacion': row[7]
            } for row in rows]
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            raise Exception(matches.group(1).strip() if matches else 'Error al obtener marcaciones irregulares')
        finally:
            conn.close()

    @staticmethod
    def get_reporte_ranking_puntualidad(fecha_inicio=None, fecha_fin=None):
        """
        REPORTE 4: Ranking de Puntualidad por Cargo
        Analiza la puntualidad agrupada por cargo
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_ReportesAsistencia] 
                    @TipoReporte = 4,
                    @FechaInicio = ?,
                    @FechaFin = ?
            ''', (fecha_inicio, fecha_fin))
            
            rows = cursor.fetchall()
            
            return [{
                'cargo': row[0],
                'total_empleados': row[1],
                'empleados_con_marcacion': row[2],
                'porcentaje_asistencia': float(row[3]) if row[3] else 0,
                'porcentaje_llegadas_tarde': float(row[4]) if row[4] else 0,
                'hora_promedio_entrada': row[5],
                'total_marcaciones': row[6],
                'total_salarios': float(row[7]) if row[7] else 0
            } for row in rows]
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            raise Exception(matches.group(1).strip() if matches else 'Error al obtener ranking de puntualidad')
        finally:
            conn.close()

    @staticmethod
    def get_reporte_ausentismo_dia_semana(fecha_inicio=None, fecha_fin=None):
        """
        REPORTE 5: Ausentismo por Día de la Semana
        Analiza patrones de ausentismo según el día de la semana
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_ReportesAsistencia] 
                    @TipoReporte = 5,
                    @FechaInicio = ?,
                    @FechaFin = ?
            ''', (fecha_inicio, fecha_fin))
            
            rows = cursor.fetchall()
            
            return [{
                'dia_semana': row[0],
                'num_dia': row[1],
                'total_empleados_activos': row[2],
                'empleados_que_marcaron': row[3],
                'empleados_ausentes': row[4],
                'porcentaje_asistencia': float(row[5]) if row[5] else 0,
                'porcentaje_llegadas_tarde': float(row[6]) if row[6] else 0
            } for row in rows]
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            raise Exception(matches.group(1).strip() if matches else 'Error al obtener ausentismo por día')
        finally:
            conn.close()

    @staticmethod
    def get_reporte_cumplimiento_horario(fecha_inicio=None, fecha_fin=None):
        """
        REPORTE 6: Cumplimiento de Horario - Llegadas Tarde vs Horario Asignado
        Compara las marcaciones con el horario asignado
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_ReportesAsistencia] 
                    @TipoReporte = 6,
                    @FechaInicio = ?,
                    @FechaFin = ?
            ''', (fecha_inicio, fecha_fin))
            
            rows = cursor.fetchall()
            
            return [{
                'empleado': row[0],
                'dni': row[1],
                'fecha': row[2],
                'dia_semana': row[3],
                'nombre_horario': row[4],
                'horario_entrada': row[5],
                'horario_salida': row[6],
                'hora_marcacion': row[7],
                'minutos_tarde': row[8],
                'estado': row[9],
                'observacion': row[10]
            } for row in rows]
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            raise Exception(matches.group(1).strip() if matches else 'Error al obtener cumplimiento de horario')
        finally:
            conn.close()

    @staticmethod
    def get_reporte_horas_trabajadas(fecha_inicio=None, fecha_fin=None):
        """
        REPORTE 7: Horas Trabajadas vs Horas Programadas
        Compara las horas efectivamente trabajadas con las programadas
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_ReportesAsistencia] 
                    @TipoReporte = 7,
                    @FechaInicio = ?,
                    @FechaFin = ?
            ''', (fecha_inicio, fecha_fin))
            
            rows = cursor.fetchall()
            
            return [{
                'empleado': row[0],
                'dni': row[1],
                'tipo_horario': row[2],
                'horas_programadas': float(row[3]) if row[3] else 0,
                'horas_trabajadas': float(row[4]) if row[4] else 0,
                'diferencia_horas': float(row[5]) if row[5] else 0,
                'dias_asistidos': row[6],
                'dias_faltados': row[7],
                'porcentaje_cumplimiento': float(row[8]) if row[8] else 0
            } for row in rows]
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            raise Exception(matches.group(1).strip() if matches else 'Error al obtener horas trabajadas')
        finally:
            conn.close()

    @staticmethod
    def get_reporte_empleados_por_turno(fecha=None):
        """
        REPORTE 8: Horarios Rotativos - Empleados por Turno
        Muestra la distribución de empleados por turno en una fecha específica
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_ReportesAsistencia] 
                    @TipoReporte = 8,
                    @Fecha = ?
            ''', (fecha,))
            
            rows = cursor.fetchall()
            
            return [{
                'tipo_horario': row[0],
                'hora_entrada': row[1],
                'hora_salida': row[2],
                'dia_semana': row[3],
                'cantidad_empleados': row[4],
                'empleados': row[5],
                'horas_turno': float(row[6]) if row[6] else 0,
                'tiene_refrigerio': row[7],
                'inicio_refrigerio': row[8],
                'fin_refrigerio': row[9]
            } for row in rows]
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            raise Exception(matches.group(1).strip() if matches else 'Error al obtener empleados por turno')
        finally:
            conn.close()

    @staticmethod
    def get_reporte_control_refrigerio(fecha_inicio=None, fecha_fin=None):
        """
        REPORTE 9: Control de Refrigerio/Break
        Controla el cumplimiento de los tiempos de refrigerio
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_ReportesAsistencia] 
                    @TipoReporte = 9,
                    @FechaInicio = ?,
                    @FechaFin = ?
            ''', (fecha_inicio, fecha_fin))
            
            rows = cursor.fetchall()
            
            return [{
                'empleado': row[0],
                'dni': row[1],
                'fecha': row[2],
                'tipo_horario': row[3],
                'hora_entrada': row[4],
                'salida_refrigerio': row[5],
                'refrigerio_programado': row[6],
                'retorno_refrigerio': row[7],
                'retorno_programado': row[8],
                'minutos_refrigerio': row[9],
                'minutos_programados': row[10],
                'diferencia_minutos': row[11],
                'estado': row[12]
            } for row in rows]
            
        except pyodbc.ProgrammingError as e:
            error_msg = str(e)
            matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
            raise Exception(matches.group(1).strip() if matches else 'Error al obtener control de refrigerio')
        finally:
            conn.close()