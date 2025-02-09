from datetime import datetime
import os
import pytz
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Obtener la zona horaria desde .env (por defecto 'UTC' si no está configurada)
APP_TIMEZONE = os.getenv('APP_TIMEZONE', 'UTC')
timezone = pytz.timezone(APP_TIMEZONE)

class AuditFieldsv2:
    @staticmethod
    def add_audit_fields(data, user_id, remote_addr, include_reg=True):
        """
        Agrega campos de auditoría a un diccionario de datos.
        
        Args:
            data (dict): Datos a actualizar.
            user_id: ID del usuario actual.
            remote_addr: Dirección IP remota.
            include_reg (bool): Si incluir campos de registro.
        """
        # Obtener la fecha y hora actual en la zona horaria configurada
        current_date = datetime.now(timezone)

        # Agregar siempre los campos de modificación
        data.update({
            'operador_modificacion': user_id,
            'estacion_modificacion': remote_addr,
            'fecha_modificacion': current_date.strftime('%Y-%m-%d %H:%M:%S')
        })

        # Agregar los campos de registro si se requiere
        if include_reg:
            data.update({
                'operador_registro': user_id,
                'estacion_registro': remote_addr,
                'fecha_registro': current_date.strftime('%Y-%m-%d %H:%M:%S')
            })

        return data
