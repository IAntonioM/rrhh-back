import re

class UpdateContratoRequest21:
    @staticmethod
    def validate(data):
        field_messages = {
            'id': 'el id contrato es obligatorio es obligatorio.',
    'n_comprobante': 'El número de comprobante es obligatorio.',
    'fecha_comprobante': 'La fecha de comprobante es obligatoria.',
    'flag_recepcion': 'El campo recepción es obligatorio.'
        }
        for field, message in field_messages.items():
            value = data.get(field)
            # El campo está ausente, es None, o es una cadena vacía
            if value is None or (isinstance(value, str) and not value.strip()):
                return False, message
                
        return True, None