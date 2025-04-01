import re

class UpdateContratoRequest2:
    @staticmethod
    def validate(data):
        field_messages = {
            'id': 'el id contrato es obligatorio es obligatorio.',
            'nro_orden_servicio': 'El Nro O/S es obligatorio.',
            'id_concepto': 'El concepto es obligatorio.',
            'fecha_orden': 'La fecha de Orden es obligatorio.',
            'nro_siaf': 'El Nro de Siaf es obligatorio.',
        }
        for field, message in field_messages.items():
            value = data.get(field)
            # El campo está ausente, es None, o es una cadena vacía
            if value is None or (isinstance(value, str) and not value.strip()):
                return False, message
                
        return True, None