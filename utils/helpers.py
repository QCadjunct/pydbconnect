# Description: Helper functions for configuration and file operations.
from typing import Dict, Any, Union, Optional
import json
from pathlib import Path
import re
from datetime import datetime
import os
import logging
from ..types.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

def load_json_config(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        path: Path to JSON configuration file

    Returns:
        Dictionary containing configuration data

    Raises:
        ConfigurationError: If file cannot be read or contains invalid JSON
    """
    try:
        path = Path(path)
        with path.open('r') as f:
            return json.load(f)
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration from {path}: {str(e)}")

def parse_connection_string(conn_string: str) -> Dict[str, str]:
    """
    Parse database connection string into components.
    
    Args:
        conn_string: Database connection string

    Returns:
        Dictionary of connection parameters
    """
    params = {}
    
    # Handle different connection string formats
    if ';' in conn_string:
        # ODBC style: key=value;key=value
        for param in conn_string.split(';'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key.strip()] = value.strip()
    else:
        # PostgreSQL style: key=value key=value
        for param in conn_string.split():
            if '=' in param:
                key, value = param.split('=', 1)
                params[key.strip()] = value.strip()
    
    return params

def mask_credentials(data: Union[str, Dict[str, Any]]) -> Union[str, Dict[str, Any]]:
    """
    Mask sensitive information in connection strings or dictionaries.
    
    Args:
        data: Connection string or dictionary containing credentials

    Returns:
        Data with masked sensitive information
    """
    sensitive_keys = [
        'password', 'pwd', 'secret', 'key', 'token',
        'apikey', 'api_key', 'auth', 'credential'
    ]
    
    if isinstance(data, str):
        # Handle connection strings
        masked = data
        for key in sensitive_keys:
            pattern = f"({key}=)[^;\\s]+"
            masked = re.sub(pattern, r"\1****", masked, flags=re.IGNORECASE)
        return masked
    elif isinstance(data, dict):
        # Handle dictionaries
        masked = data.copy()
        for key in masked:
            if any(s in key.lower() for s in sensitive_keys):
                masked[key] = "****"
        return masked
    return data

def create_backup_filename(base_name: str, timestamp: bool = True) -> str:
    """
    Create a backup filename with optional timestamp.
    
    Args:
        base_name: Base name for the backup file
        timestamp: Whether to include timestamp

    Returns:
        Backup filename
    """
    if timestamp:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp_str}.bak"
    return f"{base_name}.bak"

def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        path: Directory path

    Returns:
        Path object for the directory

    Raises:
        ConfigurationError: If directory cannot be created
    """
    path = Path(path)
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except Exception as e:
        raise ConfigurationError(f"Failed to create directory {path}: {str(e)}")

def validate_file_path(
    path: Union[str, Path],
    create_parents: bool = False
) -> Path:
    """
    Validate and normalize file path.
    
    Args:
        path: File path to validate
        create_parents: Whether to create parent directories

    Returns:
        Validated Path object

    Raises:
        ConfigurationError: If path is invalid or parent creation fails
    """
    try:
        path = Path(path).resolve()
        if create_parents:
            path.parent.mkdir(parents=True, exist_ok=True)
        return path
    except Exception as e:
        raise ConfigurationError(f"Invalid file path {path}: {str(e)}")

def load_environment_variables(prefix: str) -> Dict[str, str]:
    """
    Load environment variables with specified prefix.
    
    Args:
        prefix: Prefix for environment variables

    Returns:
        Dictionary of environment variables
    """
    return {
        key[len(prefix):]: value
        for key, value in os.environ.items()
        if key.startswith(prefix)
    }

def parse_size_string(size: str) -> int:
    """
    Parse size string (e.g., "1GB", "500MB") to bytes.
    
    Args:
        size: Size string to parse

    Returns:
        Size in bytes

    Raises:
        ValueError: If size string is invalid
    """
    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4
    }
    
    match = re.match(r'^(\d+)\s*([KMGT]?B)$', size.upper())
    if not match:
        raise ValueError(f"Invalid size string: {size}")
    
    value, unit = match.groups()
    return int(value) * units[unit]

def generate_connection_string(
    template: str,
    params: Dict[str, Any],
    mask: bool = True
) -> str:
    """
    Generate connection string from template and parameters.
    
    Args:
        template: Connection string template
        params: Parameters to substitute
        mask: Whether to mask sensitive information

    Returns:
        Formatted connection string
    """
    try:
        conn_string = template.format(**params)
        return mask_credentials(conn_string) if mask else conn_string
    except KeyError as e:
        raise ConfigurationError(f"Missing required parameter: {e}")