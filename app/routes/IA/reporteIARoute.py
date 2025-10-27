from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.IA.reporteIAModel import ReporteIAModel
from ...utils.error_handlers import handle_response

reporte_ia_bp = Blueprint('reporte_ia', __name__)

@reporte_ia_bp.route('/generar', methods=['POST'])
@jwt_required()
@handle_response
def generar_reporte_ia():
    """
    Genera un reporte basado en Machine Learning
    
    Body esperado:
    {
        "tipo_reporte": "prediccion_ausencias" | "analisis_patrones" | "empleados_riesgo" | "estadisticas_general",
        "fecha_inicio": "2024-01-01" (opcional),
        "fecha_fin": "2024-12-31" (opcional)
    }
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Validar tipo de reporte
    tipo_reporte = data.get('tipo_reporte')
    if not tipo_reporte:
        return jsonify({
            'success': False,
            'message': 'Debe especificar el tipo de reporte'
        }), 400
    
    tipos_validos = ['prediccion_ausencias', 'analisis_patrones', 'empleados_riesgo', 'estadisticas_general']
    if tipo_reporte not in tipos_validos:
        return jsonify({
            'success': False,
            'message': f'Tipo de reporte inválido. Opciones: {", ".join(tipos_validos)}'
        }), 400
    
    # Obtener fechas opcionales
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    
    # Generar reporte
    resultado = ReporteIAModel.generar_reporte_prediccion(
        tipo_reporte=tipo_reporte,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )
    
    if resultado['success']:
        return jsonify(resultado), 200
    else:
        return jsonify(resultado), 400


@reporte_ia_bp.route('/tipos', methods=['GET'])
@jwt_required()
@handle_response
def get_tipos_reporte():
    """
    Retorna los tipos de reportes disponibles
    """
    tipos = [
        {
            'id': 'prediccion_ausencias',
            'nombre': 'Predicción de Ausencias',
            'descripcion': 'Predice futuras ausencias basándose en patrones históricos'
        },
        {
            'id': 'analisis_patrones',
            'nombre': 'Análisis de Patrones',
            'descripcion': 'Analiza patrones de ausencias por día, mes y tendencias'
        },
        {
            'id': 'empleados_riesgo',
            'nombre': 'Empleados en Riesgo',
            'descripcion': 'Identifica empleados con alto riesgo de ausencia o tardanza'
        },
        {
            'id': 'estadisticas_general',
            'nombre': 'Estadísticas Generales',
            'descripcion': 'Muestra estadísticas del modelo y características más importantes'
        }
    ]
    
    return jsonify({
        'success': True,
        'data': tipos
    }), 200


@reporte_ia_bp.route('/entrenar', methods=['POST'])
@jwt_required()
@handle_response
def entrenar_modelo():
    """
    Entrena o re-entrena el modelo de ML
    Requiere permisos de administrador
    """
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    
    try:
        # Aquí podrías agregar validación de permisos de admin
        # if not user_is_admin(current_user):
        #     return jsonify({'success': False, 'message': 'Permisos insuficientes'}), 403
        
        # Importar y ejecutar el entrenamiento
        import sys
        import os
        ml_path = os.path.join(os.path.dirname(__file__), '../../ml')
        sys.path.append(ml_path)
        
        from train import train_model
        
        # Obtener datos y entrenar
        df = ReporteIAModel.get_datos_asistencias()
        
        if df is None or df.empty:
            return jsonify({
                'success': False,
                'message': 'No hay datos suficientes para entrenar el modelo'
            }), 400
        
        # Guardar datos temporales
        temp_path = os.path.join(ml_path, 'data/raw/fichajes.csv')
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        df.to_csv(temp_path, index=False)
        
        # Ejecutar pipeline de entrenamiento
        from preprocess import load_and_clean_data
        from features import build_features
        
        # Preprocesar
        df_clean = load_and_clean_data(temp_path)
        df_clean.to_csv(os.path.join(ml_path, 'data/processed/empleados_clean.csv'), index=False)
        
        # Features
        df_features = build_features(df_clean)
        df_features.to_csv(os.path.join(ml_path, 'data/processed/empleados_features.csv'), index=False)
        
        # Entrenar
        train_model(os.path.join(ml_path, 'data/processed/empleados_features.csv'))
        
        return jsonify({
            'success': True,
            'message': 'Modelo entrenado exitosamente',
            'registros_entrenamiento': len(df)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al entrenar modelo: {str(e)}'
        }), 500


@reporte_ia_bp.route('/estado', methods=['GET'])
@jwt_required()
@handle_response
def estado_modelo():
    """
    Verifica el estado del modelo de ML
    """
    import os
    
    model_path = os.path.join(os.path.dirname(__file__), '../../ml/models/random_forest.pkl')
    model_exists = os.path.exists(model_path)
    
    estado = {
        'modelo_disponible': model_exists,
        'ruta_modelo': model_path
    }
    
    if model_exists:
        # Obtener información del modelo
        import pickle
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        estado['modelo_info'] = {
            'tipo': str(type(model).__name__),
            'numero_arboles': model.n_estimators if hasattr(model, 'n_estimators') else None,
            'profundidad_maxima': model.max_depth if hasattr(model, 'max_depth') else None,
            'fecha_modificacion': os.path.getmtime(model_path)
        }
    
    return jsonify({
        'success': True,
        'data': estado
    }), 200