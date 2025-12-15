#generate_individual_reports
import pandas as pd
import pickle
from datetime import datetime
import os
import re

def sanitizar_nombre_archivo(nombre: str) -> str:
    """
    Limpia un nombre para usarlo como nombre de archivo.
    Elimina o reemplaza caracteres no válidos en Windows.
    """
    # Caracteres no permitidos en Windows: < > : " / \ | ? *
    # También eliminamos puntos consecutivos y espacios al inicio/final
    nombre = re.sub(r'[<>:"/\\|?*]', '', nombre)  # Eliminar caracteres inválidos
    nombre = re.sub(r'\.+', '_', nombre)  # Reemplazar puntos por guión bajo
    nombre = nombre.strip()  # Eliminar espacios al inicio/final
    nombre = re.sub(r'\s+', '_', nombre)  # Reemplazar espacios por guión bajo
    nombre = re.sub(r'_+', '_', nombre)  # Evitar guiones bajos múltiples
    
    # Limitar longitud (Windows tiene límite de 255 caracteres para nombres)
    if len(nombre) > 100:
        nombre = nombre[:100]
    
    # Si después de sanitizar queda vacío, usar un nombre por defecto
    if not nombre:
        nombre = "sin_nombre"
    
    return nombre


def generate_individual_reports(input_path: str, original_csv_path: str = "data/raw/fichajes.csv"):
    print("📊 Iniciando generación de reportes individuales...")
    
    # Cargar modelo y datos (similar a generate_report.py)
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "random_forest.pkl")
    
    print(f"   Ruta del modelo: {MODEL_PATH}")
    
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Modelo no encontrado en: {MODEL_PATH}")
    
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    df_original = pd.read_csv(original_csv_path)
    df_original.columns = [c.strip().lower() for c in df_original.columns]
    df_original['fecha'] = pd.to_datetime(df_original['fecha'], errors='coerce', dayfirst=True)
    
    df = pd.read_csv(input_path)
    X = df.drop(columns=["ausencia"]) if "ausencia" in df.columns else df
    
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    
    # Crear DataFrame con resultados
    dias_map = {0: 'Lun', 1: 'Mar', 2: 'Mié', 3: 'Jue', 4: 'Vie', 5: 'Sáb', 6: 'Dom'}
    meses_map = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
                 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
    
    # Extraer mes y año de la columna fecha en df_original
    reporte = pd.DataFrame({
        'empleado_id': df_original['empleado_id'].fillna('Sin ID').astype(str),
        'nombre_empleado': df_original['nombre_empleado'].fillna('Sin nombre'),
        'fecha': df_original['fecha'],
        'fecha_str': df_original['fecha'].dt.strftime('%d/%m/%Y'),
        'dia_semana': df['dia_semana'].fillna(0).astype(int).map(dias_map),
        'mes': df_original['fecha'].dt.month.fillna(1).astype(int),  # 1 en lugar de 0
        'mes_nombre': df_original['fecha'].dt.month.fillna(1).astype(int).map(meses_map),
        'anio': df_original['fecha'].dt.year.fillna(2025).astype(int),  # Año actual en lugar de 0
        'tardanza_min': df['tardanza_min'].fillna(0),
        'prediccion': predictions,
        'prob_presente': probabilities[:, 0],
        'prob_tardanza': probabilities[:, 1]
    })
    
    # Crear carpeta para reportes individuales
    os.makedirs("reports/individuales", exist_ok=True)
    
    # Agrupar por empleado
    empleados_unicos = reporte.groupby(['empleado_id', 'nombre_empleado'])
    total_empleados = len(empleados_unicos)
    
    print(f"   Generando reportes para {total_empleados} empleados...")
    print(f"   Total de registros en reporte: {len(reporte)}")
    
    for i, ((empleado_id, nombre), datos_empleado) in enumerate(empleados_unicos, 1):
        num_registros = len(datos_empleado)
        print(f"   [{i}/{total_empleados}] Generando reporte para: {nombre} ({num_registros} registros)")
        generar_reporte_html_empleado(empleado_id, nombre, datos_empleado)
    
    print(f"\n✅ {total_empleados} reportes individuales generados en: reports/individuales/")
    print("   Formato: reports/individuales/reporte_[nombre_empleado].html")


def generar_reporte_html_empleado(empleado_id: str, nombre: str, datos: pd.DataFrame):
    # ✅ DEBUG: Ver qué valores tiene prediccion
    print(f"\n🔍 DEBUG - Empleado: {nombre}")
    print(f"   Valores únicos en 'prediccion': {datos['prediccion'].unique()}")
    print(f"   Conteo por predicción:")
    print(datos['prediccion'].value_counts().sort_index())
    
    # ✅ CORRECCIÓN: Tardanza es prediccion == 2, no == 1
    total_dias = datos['fecha'].nunique()
    dias_presente = (datos['prediccion'] == 0).sum()
    dias_ausente = (datos['prediccion'] == 1).sum()  # ✅ Ausente
    dias_tardanza = (datos['prediccion'] == 2).sum()  # ✅ Tardanza (era == 1)
    
    prob_tardanza_promedio = datos['prob_tardanza'].mean() * 100
    prob_presente_promedio = datos['prob_presente'].mean() * 100
    
    # ✅ Filtrar días con TARDANZA (prediccion == 2)
    dias_con_tardanza = datos[datos['prediccion'] == 2]
    tardanza_promedio = dias_con_tardanza['tardanza_min'].mean() if len(dias_con_tardanza) > 0 else 0
    
    print(f"   📊 Estadísticas:")
    print(f"      - Total días: {total_dias}")
    print(f"      - Presente: {dias_presente}")
    print(f"      - Ausente: {dias_ausente}")
    print(f"      - Tardanza: {dias_tardanza}")
    print(f"      - Tardanza promedio: {tardanza_promedio:.1f} min")
    
    # Estadísticas mensuales
    stats_mensuales = datos.groupby(['mes', 'mes_nombre', 'anio']).agg({
        'fecha': 'nunique',
        'prediccion': lambda x: (x == 2).sum(),  # ✅ Tardanza == 2
        'prob_tardanza': 'mean'
    }).reset_index()

    stats_mensuales.columns = ['mes', 'mes_nombre', 'anio', 'total_dias', 'dias_tardanza', 'prob_tardanza_pct']

    # Calcular tardanza promedio SOLO de días con prediccion == 2
    tardanza_por_mes = datos[datos['prediccion'] == 2].groupby(['mes', 'anio'])['tardanza_min'].mean().reset_index()
    tardanza_por_mes.columns = ['mes', 'anio', 'tardanza_promedio']

    # Hacer merge
    stats_mensuales = stats_mensuales.merge(tardanza_por_mes, on=['mes', 'anio'], how='left')
    stats_mensuales['tardanza_promedio'] = stats_mensuales['tardanza_promedio'].fillna(0)
    stats_mensuales['prob_tardanza_pct'] *= 100
    
    # Ordenar datos por fecha descendente
    datos_ordenados = datos.sort_values('fecha', ascending=False)
    
    # Generar HTML (el resto sigue igual hasta el loop de la tabla detallada)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Reporte Individual - {nombre}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                min-height: 100vh;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }}
            .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
            .header h2 {{ font-size: 24px; opacity: 0.9; margin-bottom: 5px; }}
            .header p {{ opacity: 0.7; font-size: 14px; }}
            .summary {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 20px;
                padding: 30px;
                background: #f8f9fa;
            }}
            .card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .card h3 {{
                font-size: 12px;
                color: #7f8c8d;
                margin-bottom: 10px;
                text-transform: uppercase;
            }}
            .card .value {{
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .card .percentage {{ font-size: 14px; color: #95a5a6; }}
            .content {{ padding: 30px; }}
            h2 {{
                color: white;
                margin: 30px 0 20px 0;
                padding-bottom: 10px;
                border-bottom: 3px solid #3498db;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-radius: 8px;
                overflow: hidden;
            }}
            th {{
                background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 11px;
            }}
            td {{ padding: 10px 12px; border-bottom: 1px solid #ecf0f1; }}
            tr:hover {{ background-color: #f8f9fa; }}
            .badge {{
                padding: 5px 10px;
                border-radius: 15px;
                font-weight: bold;
                font-size: 10px;
                text-transform: uppercase;
            }}
            .badge-presente {{ background: #d4edda; color: #155724; }}
            .badge-ausente {{ background: #f8d7da; color: #721c24; }}
            .badge-tardanza {{ background: #fff3cd; color: #856404; }}
            .prob-bar {{
                height: 6px;
                background: #ecf0f1;
                border-radius: 3px;
                overflow: hidden;
                margin-top: 5px;
            }}
            .prob-fill {{ height: 100%; }}
            .prob-fill-yellow {{ background: linear-gradient(90deg, #f39c12, #e67e22); }}
            .prob-fill-green {{ background: linear-gradient(90deg, #2ecc71, #27ae60); }}
            .high-risk {{ background-color: #fff5f5 !important; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Reporte Individual de Asistencia</h1>
                <h2>{nombre}</h2>
                <p>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            </div>

            <div class="summary">
                <div class="card">
                    <h3>Total Días</h3>
                    <div class="value" style="color: #3498db;">{total_dias}</div>
                </div>
                <div class="card">
                    <h3>🟢 Días Presente</h3>
                    <div class="value" style="color: #27ae60;">{dias_presente}</div>
                    <div class="percentage">{dias_presente/total_dias*100:.1f}%</div>
                </div>
                <div class="card">
                    <h3>🟡 Días Tardanza</h3>
                    <div class="value" style="color: #f39c12;">{dias_tardanza}</div>
                    <div class="percentage">{dias_tardanza/total_dias*100:.1f}%</div>
                </div>
                <div class="card">
                    <h3>⏱️ Tardanza Promedio</h3>
                    <div class="value" style="color: #e74c3c;">{tardanza_promedio:.0f}</div>
                    <div class="percentage">minutos</div>
                </div>
            </div>

            <div class="content">
                <h2>📅 Estadísticas Mensuales</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Mes</th>
                            <th>Año</th>
                            <th>Días Laborados</th>
                            <th>Tardanzas</th>
                            <th>Prob. Tardanza</th>
                            <th>Tardanza Promedio</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for _, row in stats_mensuales.iterrows():
        row_class = "high-risk" if row['prob_tardanza_pct'] >= 50 else ""
        tardanza_display = f"{row['tardanza_promedio']:.0f} min" if row['dias_tardanza'] > 0 else "N/A"
        html += f"""
                        <tr class="{row_class}">
                            <td><strong>{row['mes_nombre']}</strong></td>
                            <td>{int(row['anio'])}</td>
                            <td>{int(row['total_dias'])} días</td>
                            <td><strong style="color: #f39c12;">{int(row['dias_tardanza'])}</strong> días</td>
                            <td>
                                <strong>{row['prob_tardanza_pct']:.1f}%</strong>
                                <div class="prob-bar">
                                    <div class="prob-fill prob-fill-yellow" style="width: {min(row['prob_tardanza_pct'], 100)}%"></div>
                                </div>
                            </td>
                            <td>{tardanza_display}</td>
                        </tr>
        """
    
    html += f"""
                    </tbody>
                </table>

                <h2>📋 Historial Detallado (Últimos 100 días)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Fecha</th>
                            <th>Día</th>
                            <th>Mes</th>
                            <th>Predicción</th>
                            <th>Prob. Tardanza</th>
                            <th>Tardanza (min)</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for _, row in datos_ordenados.head(100).iterrows():
        pred = int(row['prediccion'])
        # ✅ CORRECCIÓN: Mapeo correcto de predicciones
        if pred == 0:
            badge_class = 'badge-presente'
            badge_text = 'PRESENTE'
        elif pred == 1:
            badge_class = 'badge-ausente'
            badge_text = 'AUSENTE'
        else:  # pred == 2
            badge_class = 'badge-tardanza'
            badge_text = 'TARDANZA'
        
        prob_pct = row['prob_tardanza'] * 100
        
        html += f"""
                        <tr>
                            <td><strong>{row['fecha_str']}</strong></td>
                            <td>{row['dia_semana']}</td>
                            <td>{row['mes_nombre']}</td>
                            <td><span class="badge {badge_class}">{badge_text}</span></td>
                            <td>
                                <strong>{prob_pct:.1f}%</strong>
                                <div class="prob-bar">
                                    <div class="prob-fill prob-fill-yellow" style="width: {prob_pct}%"></div>
                                </div>
                            </td>
                            <td><strong>{row['tardanza_min']:.0f}</strong> min</td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Sanitizar nombre del empleado para el archivo
    nombre_archivo = sanitizar_nombre_archivo(nombre)
    ruta_archivo = f"reports/individuales/reporte_{nombre_archivo}.html"
    
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    generate_individual_reports("data/processed/empleados_features.csv", "data/raw/fichajes.csv")