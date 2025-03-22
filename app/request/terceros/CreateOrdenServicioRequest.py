class CreateOrdenServicioRequest:
    @staticmethod
    def validate(data):
        # Validar que el 'id_datos_personales' esté presente
        if 'id_datos_personales' not in data or not bool(data['id_datos_personales']):
            return False, "El ID de datos personales es obligatorio."
        
        # Asegurarse de que 'estado' siempre sea '1', si no está presente, se asigna '1' por defecto
        data['estado'] = 1
        
        # Validar 'monto': si es vacío o None, asignar 0 por defecto
        if 'monto' not in data or data['monto'] == "" or data['monto'] is None:
            data['monto'] = 0  # Asignamos 0 por defecto si no se proporciona un monto
        
        # Validar 'id_concepto': es un campo requerido
        # if 'id_concepto' not in data or not bool(data['id_concepto']):
        #     return False, "El ID del concepto es obligatorio."
        
        # Si todo es válido
        return True, None

