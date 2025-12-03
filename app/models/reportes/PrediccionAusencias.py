import pyodbc
import pandas as pd
import os
import pickle
from datetime import datetime
from config import get_db_connection

class PrediccionAusencias:
    
    # Rutas configurables
    ML_MODELS_PATH = os.getenv('ML_MODELS_PATH', 'ml_models/')
    ML_REPORTS_PATH = os.getenv('ML_REPORTS_PATH', 'reports/')
    ML_DATA_PATH = os.getenv('ML_DATA_PATH', 'data/')
    
    @staticmethod
    def obtener_datos_fichajes(fecha_inicio=None, fecha_fin=None):
        """
        Ejecuta el SP para obtener datos de fichajes
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                EXEC [dbo].[sp_Fichajes_ML]
                @fecha_inicio = ?,
                @fecha_fin = ?
            ''', (fecha_inicio, fecha_fin))
            
            columns = [column[0] for column in cursor.description]
            results = cursor.fetchall()
            
            # Convertir a DataFrame
            df = pd.DataFrame.from_records(results, columns=columns)
            
            return {
                'success': True,
                'data': df,
                'total_registros': len(df)
            }
        except Exception as e:
            print(f"Error en obtener_datos_fichajes: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
        finally:
            conn.close()
    
    @staticmethod
    def guardar_csv_temporal(df, nombre_archivo='fichajes.csv'):
        """
        Guarda DataFrame como CSV temporal
        """
        try:
            # Crear carpetas si no existen
            raw_path = os.path.join(PrediccionAusencias.ML_DATA_PATH, 'raw')
            os.makedirs(raw_path, exist_ok=True)
            
            file_path = os.path.join(raw_path, nombre_archivo)
            df.to_csv(file_path, index=False)
            
            return {
                'success': True,
                'file_path': file_path
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    @staticmethod
    def ejecutar_pipeline_ml():
        """
        Ejecuta todo el pipeline de ML:
        1. Obtiene datos del SP
        2. Guarda CSV
        3. Ejecuta preprocess
        4. Ejecuta features
        5. Ejecuta predicciones
        6. Genera reportes
        """
        try:
            print("🚀 Iniciando pipeline de ML...")
            
            # 1. Obtener datos
            print("📊 Obteniendo datos de fichajes...")
            result = PrediccionAusencias.obtener_datos_fichajes()
            
            if not result['success']:
                return {
                    'success': False,
                    'message': 'Error al obtener datos: ' + result['message']
                }
            
            df = result['data']
            print(f"✅ Datos obtenidos: {result['total_registros']} registros")
            
            # 2. Guardar CSV
            print("💾 Guardando CSV temporal...")
            csv_result = PrediccionAusencias.guardar_csv_temporal(df)
            
            if not csv_result['success']:
                return {
                    'success': False,
                    'message': 'Error al guardar CSV: ' + csv_result['message']
                }
            
            csv_path = csv_result['file_path']
            print(f"✅ CSV guardado en: {csv_path}")
            
            # 3. Ejecutar preprocess
            print("🔄 Ejecutando preprocess...")
            from app.ml_src.preprocess import load_and_clean_data
            df_clean = load_and_clean_data(csv_path)
            
            clean_path = os.path.join(PrediccionAusencias.ML_DATA_PATH, 'processed', 'empleados_clean.csv')
            os.makedirs(os.path.dirname(clean_path), exist_ok=True)
            df_clean.to_csv(clean_path, index=False)
            print(f"✅ Preprocess completado: {clean_path}")
            
            # 4. Ejecutar features
            print("🔧 Generando features...")
            from app.ml_src.features import build_features
            df_features = build_features(df_clean)
            
            features_path = os.path.join(PrediccionAusencias.ML_DATA_PATH, 'processed', 'empleados_features.csv')
            df_features.to_csv(features_path, index=False)
            print(f"✅ Features generados: {features_path}")
            
            # 5. Generar reportes
            print("📋 Generando reportes...")
            from app.ml_src.generate_report import generate_html_report
            from app.ml_src.generate_individual_reports import generate_individual_reports
            
            # Crear carpetas de reportes
            os.makedirs(os.path.join(PrediccionAusencias.ML_REPORTS_PATH, 'generales'), exist_ok=True)
            os.makedirs(os.path.join(PrediccionAusencias.ML_REPORTS_PATH, 'individuales'), exist_ok=True)
            
            # Generar reporte general
            generate_html_report(features_path, csv_path)
            
            # Generar reportes individuales
            generate_individual_reports(features_path, csv_path)
            
            # Mover reportes a carpetas organizadas
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            
            # Mover reporte general
            reporte_general_src = os.path.join('reports', 'reporte_ausencias.html')
            reporte_general_dst = os.path.join(
                PrediccionAusencias.ML_REPORTS_PATH, 
                'generales', 
                f'reporte_general_{timestamp}.html'
            )
            
            if os.path.exists(reporte_general_src):
                os.rename(reporte_general_src, reporte_general_dst)
            
            print("✅ Pipeline completado exitosamente!")
            
            return {
                'success': True,
                'message': 'Reportes generados exitosamente',
                'reporte_general': reporte_general_dst,
                'reportes_individuales': os.path.join(PrediccionAusencias.ML_REPORTS_PATH, 'individuales'),
                'timestamp': timestamp,
                'total_registros': result['total_registros']
            }
            
        except Exception as e:
            print(f"❌ Error en pipeline: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Error en pipeline: {str(e)}'
            }
    
    @staticmethod
    def listar_reportes():
        """
        Lista todos los reportes generados
        """
        try:
            reportes = []
            
            # Reportes generales
            generales_path = os.path.join(PrediccionAusencias.ML_REPORTS_PATH, 'generales')
            if os.path.exists(generales_path):
                for filename in os.listdir(generales_path):
                    if filename.endswith('.html'):
                        file_path = os.path.join(generales_path, filename)
                        stat = os.stat(file_path)
                        reportes.append({
                            'tipo': 'general',
                            'nombre': filename,
                            'ruta': file_path,
                            'fecha_creacion': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                            'tamano_kb': round(stat.st_size / 1024, 2)
                        })
            
            # Reportes individuales
            individuales_path = os.path.join(PrediccionAusencias.ML_REPORTS_PATH, 'individuales')
            if os.path.exists(individuales_path):
                for filename in os.listdir(individuales_path):
                    if filename.endswith('.html'):
                        file_path = os.path.join(individuales_path, filename)
                        stat = os.stat(file_path)
                        reportes.append({
                            'tipo': 'individual',
                            'nombre': filename,
                            'ruta': file_path,
                            'fecha_creacion': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                            'tamano_kb': round(stat.st_size / 1024, 2)
                        })
            
            # Ordenar por fecha de creación descendente
            reportes.sort(key=lambda x: x['fecha_creacion'], reverse=True)
            
            return {
                'success': True,
                'data': reportes,
                'total': len(reportes)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    @staticmethod
    def obtener_ultimo_reporte_general():
        """
        Obtiene el último reporte general generado
        """
        try:
            generales_path = os.path.join(PrediccionAusencias.ML_REPORTS_PATH, 'generales')
            
            if not os.path.exists(generales_path):
                return {
                    'success': False,
                    'message': 'No existen reportes generados'
                }
            
            archivos = [f for f in os.listdir(generales_path) if f.endswith('.html')]
            
            if not archivos:
                return {
                    'success': False,
                    'message': 'No hay reportes disponibles'
                }
            
            # Obtener el más reciente
            archivos_con_fecha = []
            for filename in archivos:
                file_path = os.path.join(generales_path, filename)
                stat = os.stat(file_path)
                archivos_con_fecha.append((filename, stat.st_ctime))
            
            ultimo_archivo = max(archivos_con_fecha, key=lambda x: x[1])[0]
            ultimo_path = os.path.join(generales_path, ultimo_archivo)
            
            return {
                'success': True,
                'nombre': ultimo_archivo,
                'ruta': ultimo_path,
                'fecha_creacion': datetime.fromtimestamp(max(archivos_con_fecha, key=lambda x: x[1])[1]).strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    @staticmethod
    def leer_reporte_html(ruta_archivo):
        """
        Lee el contenido de un reporte HTML
        """
        try:
            if not os.path.exists(ruta_archivo):
                return {
                    'success': False,
                    'message': 'Archivo no encontrado'
                }
            
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            return {
                'success': True,
                'contenido': contenido
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }