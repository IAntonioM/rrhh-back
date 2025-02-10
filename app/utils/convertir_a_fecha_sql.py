from datetime import datetime
import os
import pytz
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Obtener la zona horaria desde .env (por defecto 'UTC' si no está configurada)
APP_TIMEZONE = os.getenv('APP_TIMEZONE', 'AMERICA/LATINA')
timezone = pytz.timezone(APP_TIMEZONE)

# Función para convertir una fecha a la zona horaria de Perú
def convertir_a_fecha_sql(fecha_str):
    if fecha_str is None:
        return None

    # Intentar convertir el formato ISO 8601
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M:%S.%fZ')  # Para formato '2025-02-08T05:00:00.000Z'
    except ValueError:
        try:
            fecha = datetime.strptime(fecha_str, '%a, %d %b %Y %H:%M:%S GMT')  # Para formato 'Mon, 10 Feb 2025 00:00:00 GMT'
        except ValueError:
            return None

    # Localizar la fecha como UTC
    fecha = pytz.utc.localize(fecha)
    
    # Convertir a la zona horaria de Perú
    tz = pytz.timezone('America/Lima')
    fecha_peru = fecha.astimezone(tz)
    
    # Devolver la fecha en formato adecuado para SQL
    return fecha_peru.strftime('%Y-%m-%d %H:%M:%S')
