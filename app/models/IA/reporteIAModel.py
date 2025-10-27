import pyodbc
import pandas as pd
import pickle
import os
from datetime import datetime
from config import get_db_connection
import sys

# Agregar la ruta de ml al path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../ml'))

from preprocess import load_and_clean_data
from features import build_features

class ReporteIAModel:
    
    MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../ml/models/random_forest.pkl')
    DATA_PATH = os.path.join(os.path.dirname(__file__), '../../ml/data')
    
    @staticmethod
    def get_datos_asistencias(fecha_inicio=None, fecha_fin=None):
        """
        Obtiene datos de asistencias desde la BD para análisis
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Query para obtener datos de asistencias
            query = '''
                SELECT 
                    e.nombre_empleado,
                    a.fecha,
                    a.hora_entrada_teorica,
                    a.hora_entrada_real,
                    a.hora_salida_teorica,
                    a.hora_salida_real,
                    a.tardanza_min,
                    a.ausencia,
                    e.idEmpleado,
                    e.idCargo,
                    e.idSede,
                    e.idCentroCosto
                FROM asistencias a
                INNER JOIN empleados e ON a.idEmpleado = e.idEmpleado
                WHERE 1=1
            '''
            
            params = []
            if fecha_inicio:
                query += ' AND a.fecha >= ?'
                params.append(fecha_inicio)
            if fecha_fin:
                query += ' AND a.fecha <= ?'
                params.append(fecha_fin)
                
            query += ' ORDER BY a.fecha DESC'
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            columns = [column[0] for column in cursor.description]
            data = cursor.fetchall()
            
            # Convertir a DataFrame
            df = pd.DataFrame.from_records(data, columns=columns)
            
            return df
            
        except Exception as e:
            print(f"Error al obtener datos: {str(e)}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def generar_reporte_prediccion(tipo_reporte, fecha_inicio=None, fecha_fin=None):
        """
        Genera reportes basados en predicciones de ML
        
        Tipos de reporte:
        - 'prediccion_ausencias': Predice ausencias futuras
        - 'analisis_patrones': Analiza patrones de ausencias
        - 'empleados_riesgo': Identifica empleados con alto riesgo de ausencia
        - 'estadisticas_general': Estadísticas generales del modelo
        """
        try:
            # Verificar si existe el modelo
            if not os.path.exists(ReporteIAModel.MODEL_PATH):
                return {
                    'success': False,
                    'message': 'Modelo de ML no encontrado. Debe entrenar el modelo primero.'
                }
            
            # Cargar el modelo
            with open(ReporteIAModel.MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
            
            # Obtener datos de la BD
            df = ReporteIAModel.get_datos_asistencias(fecha_inicio, fecha_fin)
            
            if df is None or df.empty:
                return {
                    'success': False,
                    'message': 'No se encontraron datos para analizar'
                }
            
            # Procesar datos según el tipo de reporte
            if tipo_reporte == 'prediccion_ausencias':
                resultado = ReporteIAModel._reporte_prediccion_ausencias(model, df)
            elif tipo_reporte == 'analisis_patrones':
                resultado = ReporteIAModel._reporte_analisis_patrones(model, df)
            elif tipo_reporte == 'empleados_riesgo':
                resultado = ReporteIAModel._reporte_empleados_riesgo(model, df)
            elif tipo_reporte == 'estadisticas_general':
                resultado = ReporteIAModel._reporte_estadisticas_general(model, df)
            else:
                return {
                    'success': False,
                    'message': 'Tipo de reporte no válido'
                }
            
            # Guardar el reporte en archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'reporte_{tipo_reporte}_{timestamp}.json'
            filepath = os.path.join(ReporteIAModel.DATA_PATH, 'processed', filename)
            
            # Asegurar que existe el directorio
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2, default=str)
            
            return {
                'success': True,
                'message': 'Reporte generado exitosamente',
                'data': resultado,
                'archivo': filename
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al generar reporte: {str(e)}'
            }
    
    @staticmethod
    def _reporte_prediccion_ausencias(model, df):
        """Genera predicciones de ausencias"""
        # Preprocesar datos
        df_clean = load_and_clean_data_from_df(df)
        df_features = build_features(df_clean)
        
        # Remover columna objetivo si existe
        if 'ausencia' in df_features.columns:
            X = df_features.drop(columns=['ausencia'])
            y_real = df_features['ausencia']
        else:
            X = df_features
            y_real = None
        
        # Hacer predicciones
        predicciones = model.predict(X)
        probabilidades = model.predict_proba(X)
        
        # Mapeo de clases
        clases = {0: 'Presente', 1: 'Ausente', 2: 'Tardanza'}
        
        # Construir resultado
        resultado = {
            'total_registros': len(predicciones),
            'predicciones': {
                'Presente': int((predicciones == 0).sum()),
                'Ausente': int((predicciones == 1).sum()),
                'Tardanza': int((predicciones == 2).sum())
            },
            'porcentajes': {
                'Presente': float((predicciones == 0).sum() / len(predicciones) * 100),
                'Ausente': float((predicciones == 1).sum() / len(predicciones) * 100),
                'Tardanza': float((predicciones == 2).sum() / len(predicciones) * 100)
            },
            'detalle': []
        }
        
        # Agregar detalle por empleado
        if 'nombre_empleado' in df.columns:
            for idx, row in df.iterrows():
                if idx < len(predicciones):
                    resultado['detalle'].append({
                        'empleado': row['nombre_empleado'],
                        'fecha': str(row.get('fecha', '')),
                        'prediccion': clases[predicciones[idx]],
                        'probabilidad_ausente': float(probabilidades[idx][1]),
                        'probabilidad_tardanza': float(probabilidades[idx][2])
                    })
        
        return resultado
    
    @staticmethod
    def _reporte_analisis_patrones(model, df):
        """Analiza patrones de ausencias"""
        df_clean = load_and_clean_data_from_df(df)
        
        # Análisis temporal
        df_clean['dia_semana'] = pd.to_datetime(df_clean['fecha']).dt.dayofweek
        dias_semana = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
        
        patrones = {
            'ausencias_por_dia': {},
            'tardanzas_por_dia': {},
            'mes_mas_ausencias': {},
            'tendencia_mensual': []
        }
        
        # Ausencias por día de la semana
        for dia in range(7):
            dia_data = df_clean[df_clean['dia_semana'] == dia]
            ausencias = (dia_data['ausencia'] == 1).sum()
            tardanzas = (dia_data['ausencia'] == 2).sum()
            
            patrones['ausencias_por_dia'][dias_semana[dia]] = int(ausencias)
            patrones['tardanzas_por_dia'][dias_semana[dia]] = int(tardanzas)
        
        # Análisis mensual
        df_clean['mes'] = pd.to_datetime(df_clean['fecha']).dt.month
        for mes in df_clean['mes'].unique():
            mes_data = df_clean[df_clean['mes'] == mes]
            ausencias = (mes_data['ausencia'] == 1).sum()
            patrones['mes_mas_ausencias'][int(mes)] = int(ausencias)
        
        return patrones
    
    @staticmethod
    def _reporte_empleados_riesgo(model, df):
        """Identifica empleados con alto riesgo de ausencia"""
        df_clean = load_and_clean_data_from_df(df)
        df_features = build_features(df_clean)
        
        if 'ausencia' in df_features.columns:
            X = df_features.drop(columns=['ausencia'])
        else:
            X = df_features
        
        # Predicciones
        probabilidades = model.predict_proba(X)
        
        # Agrupar por empleado
        empleados_riesgo = []
        
        if 'nombre_empleado' in df.columns:
            for empleado in df['nombre_empleado'].unique():
                mask = df['nombre_empleado'] == empleado
                probs_empleado = probabilidades[mask]
                
                # Calcular riesgo promedio
                riesgo_ausencia = probs_empleado[:, 1].mean()
                riesgo_tardanza = probs_empleado[:, 2].mean()
                riesgo_total = riesgo_ausencia + riesgo_tardanza
                
                empleados_riesgo.append({
                    'empleado': empleado,
                    'riesgo_ausencia': float(riesgo_ausencia * 100),
                    'riesgo_tardanza': float(riesgo_tardanza * 100),
                    'riesgo_total': float(riesgo_total * 100),
                    'nivel_riesgo': 'Alto' if riesgo_total > 0.3 else 'Medio' if riesgo_total > 0.15 else 'Bajo'
                })
        
        # Ordenar por riesgo total
        empleados_riesgo.sort(key=lambda x: x['riesgo_total'], reverse=True)
        
        return {
            'total_empleados': len(empleados_riesgo),
            'empleados_alto_riesgo': [e for e in empleados_riesgo if e['nivel_riesgo'] == 'Alto'],
            'empleados_medio_riesgo': [e for e in empleados_riesgo if e['nivel_riesgo'] == 'Medio'],
            'empleados_bajo_riesgo': [e for e in empleados_riesgo if e['nivel_riesgo'] == 'Bajo'],
            'top_10_riesgo': empleados_riesgo[:10]
        }
    
    @staticmethod
    def _reporte_estadisticas_general(model, df):
        """Genera estadísticas generales del modelo"""
        df_clean = load_and_clean_data_from_df(df)
        df_features = build_features(df_clean)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': df_features.drop(columns=['ausencia'], errors='ignore').columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        estadisticas = {
            'total_registros_analizados': len(df),
            'periodo_analisis': {
                'fecha_inicio': str(df['fecha'].min()) if 'fecha' in df.columns else None,
                'fecha_fin': str(df['fecha'].max()) if 'fecha' in df.columns else None
            },
            'distribucion_real': {
                'Presente': int((df_clean['ausencia'] == 0).sum()),
                'Ausente': int((df_clean['ausencia'] == 1).sum()),
                'Tardanza': int((df_clean['ausencia'] == 2).sum())
            },
            'top_10_features': [
                {
                    'feature': row['feature'],
                    'importancia': float(row['importance'])
                }
                for _, row in feature_importance.head(10).iterrows()
            ],
            'metricas_modelo': {
                'numero_arboles': model.n_estimators,
                'profundidad_maxima': str(model.max_depth),
                'features_utilizados': len(model.feature_importances_)
            }
        }
        
        return estadisticas


def load_and_clean_data_from_df(df):
    """Versión modificada de load_and_clean_data que trabaja con DataFrame"""
    # Normalizar nombres de columnas
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Convertir fecha a datetime
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    
    # Crear columnas derivadas
    df['dia_semana'] = df['fecha'].dt.dayofweek
    
    # Clasificar ausencia
    df['ausencia'] = df['ausencia'].fillna('Presente')
    df['ausencia'] = df['ausencia'].astype(str).str.strip().str.lower()
    
    def clasificar_ausencia(valor):
        if 'ausente' in valor:
            return 1
        elif 'tardanza' in valor or 'tarde' in valor:
            return 2
        else:
            return 0
    
    df['ausencia'] = df['ausencia'].apply(clasificar_ausencia)
    
    # Rellenar nulos
    df = df.fillna(0)
    
    # Quitar columnas no útiles
    df = df.drop(columns=['nombre_empleado'], errors='ignore')
    
    return df