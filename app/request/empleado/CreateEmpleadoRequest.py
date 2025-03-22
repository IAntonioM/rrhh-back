import re

class CreateEmpleadoRequest:
    @staticmethod
    def validate(data):
        # Definir campos requeridos con mensajes de error específicos
        field_messages = {
            'idCondicionLaboral': 'La condición laboral es obligatoria.',
            'apellido_paterno': 'El apellido paterno es obligatorio.',
            'apellido_materno': 'El apellido materno es obligatorio.',
            'nombres': 'Los nombres son obligatorios.',
            'idSexo': 'Debe seleccionar el sexo.',
            'dni': 'El DNI es obligatorio.',
            'idDistrito': 'El distrito es obligatorio.'
        }
         # Agregar flag_tercero con valor fijo de 0
        data['flag_terceros'] = 0
        # Validar que los campos requeridos no sean null, undefined o cadenas vacías
        for field, message in field_messages.items():
            value = data.get(field)
            # El campo está ausente, es None, o es una cadena vacía
            if value is None or (isinstance(value, str) and not value.strip()):
                return False, message
        
        # Validar formato de DNI
        if not re.match(r'^\d{8}$', data['dni']):
            return False, "El DNI debe tener 8 dígitos."
        
        # Validar email (solo si está presente y no es cadena vacía)
        if email := data.get('email'):
            if isinstance(email, str) and email.strip() and not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
                return False, "Ingrese un email válido."
                
        return True, None