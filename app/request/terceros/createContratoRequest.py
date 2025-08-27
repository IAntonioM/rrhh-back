import re

class CreateContratoRequest:
    @staticmethod
    def validate(data):
        field_messages = {
            'id_datos_personales': 'Debe Seleccionar un usuario valido.',
            'idCentroCosto': 'El Area es obligatorio.',
            'mes_anio': 'El Mes / Anio es obligatorio.',
            'flag_padre_madre': 'El campo Si es Padre / Madre es obligatorio.',
            'monto': 'El Monto es obligatorio.',
        }
        for field, message in field_messages.items():
            value = data.get(field)
            # El campo está ausente, es None, o es una cadena vacía
            if value is None or (isinstance(value, str) and not value.strip()):
                return False, message
                
        return True, None