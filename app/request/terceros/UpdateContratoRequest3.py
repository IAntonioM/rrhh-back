import re

class UpdateContratoRequest3:
    @staticmethod
    def validate(data):
        field_messages = {
            'id': 'el id contrato es obligatorio es obligatorio.',
            'devengar': 'El campo Devengar es obligatorio.',
            'campo1': 'El Campo1 es obligatorio.'
        }
        for field, message in field_messages.items():
            value = data.get(field)
            # El campo está ausente, es None, o es una cadena vacía
            if value is None or (isinstance(value, str) and not value.strip()):
                return False, message
                
        return True, None