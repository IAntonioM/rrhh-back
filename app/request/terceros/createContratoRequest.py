import re

class CreateContratoRequest:
    @staticmethod
    def validate(data):
        field_messages = {
            'id_datos_personales': 'Debe Seleccionar un usuario valido.',
            'idCentroCosto': 'El centro de costo es obligatorio.',
            'fecha_inicio': 'La fecha de Inicio es obligatorio.',
            'fecha_fin': 'La fecha de Fin es obligatorio.',
            'monto': 'El Monto es obligatorio.',
        }
        for field, message in field_messages.items():
            value = data.get(field)
            # El campo está ausente, es None, o es una cadena vacía
            if value is None or (isinstance(value, str) and not value.strip()):
                return False, message
                
        return True, None