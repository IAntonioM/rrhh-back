
from flask import jsonify
import re
import pyodbc
from functools import wraps

def handle_response(func=None, include_data=False):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except pyodbc.ProgrammingError as e:
                response = {
                    'success': False,
                    'message': handle_sql_error(e)
                }
                if include_data:
                    response['data'] = []
                return jsonify(response), 409
            # except Exception as e:
            #     response = {
            #         'success': False,
            #         'message': 'Error interno del servidor'
            #     }
            #     if include_data:
            #         response['data'] = []
            #     return jsonify(response), 500
        return wrapper

    if func:
        return decorator(func)
    return decorator

def handle_sql_error(e):
    error_msg = str(e)
    matches = re.search(r'\[SQL Server\](.*?)(?:\(|\[|$)', error_msg)
    return matches.group(1).strip() if matches else 'Error en la operación'