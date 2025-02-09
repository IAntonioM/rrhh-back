from datetime import datetime

class AuditFieldsv2:
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
        current_date = datetime.utcnow()
        
        # Always add update fields
        data.update({
            'operador_modificacion': user_id,
            'estacion_modificacion': remote_addr,
            'fecha_modificacion': current_date
        })
        
        # Add registration fields if needed
        if include_reg:
            data.update({
            'operador_registro': user_id,
            'estacion_registro': remote_addr,
            'fecha_registro': current_date
            })
        
        return data