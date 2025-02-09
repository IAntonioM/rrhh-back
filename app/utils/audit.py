import os
from datetime import datetime
from dotenv import load_dotenv
import pytz

# Cargar variables desde el archivo .env
load_dotenv()

# Obtener la zona horaria desde .env (por defecto America/Lima)
TIMEZONE = os.getenv('APP_TIMEZONE', 'America/Lima')
tz = pytz.timezone(TIMEZONE)


class AuditFields:
    @staticmethod
    def add_audit_fields(data, user_id, remote_addr, include_reg=True):
        """
        Add audit fields to data dictionary
        
        Args:
            data (dict): Data to update
            user_id: Current user ID
            remote_addr: Remote IP address
            include_reg (bool): Include registration fields
        """
        current_date = datetime.now(tz)  # Usar la zona horaria configurada
        
        # Always add update fields
        data.update({
            'operador_act': user_id,
            'estacion_act': remote_addr,
            'fecha_act': current_date.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Add registration fields if needed
        if include_reg:
            data.update({
                'operador_reg': user_id,
                'estacion_reg': remote_addr,
                'fecha_reg': current_date.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return data