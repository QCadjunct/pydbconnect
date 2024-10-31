# pydatabaseconnection/utility/validators.py
from typing import Any, Dict, Optional
from ..exceptions.database_exceptions import ValidationError

def validate_connection_params(params: Dict[str, Any]) -> None:
    """Validate database connection parameters."""
    required_params = ['database', 'server']
    missing_params = [param for param in required_params if param not in params]
    
    if missing_params:
        raise ValidationError(f"Missing required parameters: {', '.join(missing_params)}")
        
    if 'port' in params and not isinstance(params['port'], int):
        raise ValidationError("Port must be an integer")
        
    if 'port' in params and not (1 <= params['port'] <= 65535):
        raise ValidationError("Port must be between 1 and 65535")

def validate_credentials(username: Optional[str], password: Optional[str]) -> None:
    """Validate database credentials."""
    if username is not None and len(username.strip()) == 0:
        raise ValidationError("Username cannot be empty")
        
    if password is not None:
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in password):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in password):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in password):
            raise ValidationError("Password must contain at least one number")
        if not any(not c.isalnum() for c in password):
            raise ValidationError("Password must contain at least one special character")

def validate_query_params(query: str, params: Optional[Dict[str, Any]] = None) -> None:
    """Validate SQL query and parameters."""
    if not query.strip():
        raise ValidationError("Query cannot be empty")
        
    if params:
        if not isinstance(params, dict):
            raise ValidationError("Parameters must be provided as a dictionary")
            
        placeholders = [p for p in query.split('?')[:-1] if p.strip()]
        if len(placeholders) != len(params):
            raise ValidationError(
                f"Number of parameters ({len(params)}) does not match "
                f"placeholders in query ({len(placeholders)})"
            )