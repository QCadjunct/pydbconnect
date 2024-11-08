from typing import Dict, Any, Optional, Union, List, Set
from ..types.exceptions import ValidationError
from ..types.connection_types import ConnectionConfig, Credentials
import re
import ipaddress

class ValidationRules:
    """Contains validation rules and constraints for database parameters"""
    
    PORT_RANGE = (1, 65535)
    MAX_USERNAME_LENGTH = 128
    MAX_PASSWORD_LENGTH = 256
    VALID_HOSTNAME_REGEX = r'^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    RESERVED_WORDS = {'select', 'drop', 'delete', 'update', 'insert', 'alter', 'truncate'}
    
    @classmethod
    def is_valid_port(cls, port: int) -> bool:
        """Check if port number is valid"""
        return isinstance(port, int) and cls.PORT_RANGE[0] <= port <= cls.PORT_RANGE[1]
    
    @classmethod
    def is_valid_hostname(cls, hostname: str) -> bool:
        """Check if hostname/server name is valid"""
        if not hostname:
            return False
        return bool(re.match(cls.VALID_HOSTNAME_REGEX, hostname))
    
    @classmethod
    def is_valid_ip(cls, ip: str) -> bool:
        """Check if IP address is valid"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @classmethod
    def is_valid_database_name(cls, name: str) -> bool:
        """Check if database name is valid"""
        if not name or not isinstance(name, str):
            return False
        name_lower = name.lower()
        return all(word not in name_lower for word in cls.RESERVED_WORDS)

class ConnectionValidator:
    """Validates database connection parameters and credentials"""
    
    @staticmethod
    def validate_connection_params(params: Dict[str, Any], required_params: Set[str]) -> None:
        """
        Validate connection parameters against required parameters and rules.
        
        Args:
            params: Dictionary of connection parameters
            required_params: Set of required parameter names
            
        Raises:
            ValidationError: If validation fails
        """
        # Check for missing required parameters
        missing_params = required_params - set(params.keys())
        if missing_params:
            raise ValidationError(f"Missing required parameters: {missing_params}")
        
        # Validate port if present
        if 'PORT_NUMBER' in params:
            if not ValidationRules.is_valid_port(params['PORT_NUMBER']):
                raise ValidationError(f"Invalid port number: {params['PORT_NUMBER']}")
        
        # Validate server/host if present
        if 'SERVER' in params:
            server = params['SERVER']
            if not (ValidationRules.is_valid_hostname(server) or 
                   ValidationRules.is_valid_ip(server)):
                raise ValidationError(f"Invalid server/host: {server}")
        
        # Validate database name if present
        if 'DATABASE_NAME' in params:
            if not ValidationRules.is_valid_database_name(params['DATABASE_NAME']):
                raise ValidationError(f"Invalid database name: {params['DATABASE_NAME']}")

    @staticmethod
    def validate_credentials(
        username: Optional[str], 
        password: Optional[str], 
        required: bool = True
    ) -> None:
        """
        Validate database credentials.
        
        Args:
            username: Username to validate
            password: Password to validate
            required: Whether credentials are required
            
        Raises:
            ValidationError: If validation fails
        """
        if required:
            if not username or not password:
                raise ValidationError("Username and password are required")
                
        if username and len(username) > ValidationRules.MAX_USERNAME_LENGTH:
            raise ValidationError(f"Username exceeds maximum length of {ValidationRules.MAX_USERNAME_LENGTH}")
            
        if password and len(password) > ValidationRules.MAX_PASSWORD_LENGTH:
            raise ValidationError(f"Password exceeds maximum length of {ValidationRules.MAX_PASSWORD_LENGTH}")

class QueryValidator:
    """Validates SQL queries and parameters"""
    
    DANGEROUS_PATTERNS = [
        r'--',           # SQL comments
        r'/\*.*?\*/',    # Multi-line comments
        r';.*?;',        # Multiple statements
        r'xp_cmdshell',  # Command execution
        r'EXEC\s+\w+',   # Dynamic execution
    ]
    
    @classmethod
    def validate_query(cls, query: str) -> None:
        """
        Validate SQL query for potential security issues.
        
        Args:
            query: SQL query to validate
            
        Raises:
            ValidationError: If validation fails
        """
        query_lower = query.lower()
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                raise ValidationError(f"Query contains potentially dangerous pattern: {pattern}")
        
        # Check for multiple statements
        if query_lower.count(';') > 1:
            raise ValidationError("Multiple SQL statements are not allowed")
        
        # Check for common SQL injection patterns
        if "'" in query_lower or '"' in query_lower:
            raise ValidationError("Use parameterized queries instead of string concatenation")

    @staticmethod
    def validate_parameters(
        params: Union[tuple, list, dict, None],
        expected_count: int
    ) -> None:
        """
        Validate query parameters.
        
        Args:
            params: Query parameters to validate
            expected_count: Expected number of parameters
            
        Raises:
            ValidationError: If validation fails
        """
        if params is None:
            if expected_count > 0:
                raise ValidationError(f"Expected {expected_count} parameters, got none")
            return
            
        if isinstance(params, (list, tuple)):
            if len(params) != expected_count:
                raise ValidationError(
                    f"Parameter count mismatch. Expected {expected_count}, got {len(params)}"
                )
        elif isinstance(params, dict):
            # For named parameters
            missing_params = {f"param{i}" for i in range(expected_count)} - set(params.keys())
            if missing_params:
                raise ValidationError(f"Missing named parameters: {missing_params}")

class DataFrameValidator:
    """Validates DataFrame operations and transformations"""
    
    @staticmethod
    def validate_dataframe_operation(
        df: Any,
        required_columns: Optional[List[str]] = None,
        min_rows: int = 0
    ) -> None:
        """
        Validate DataFrame for operations.
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
            min_rows: Minimum number of rows required
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            import pandas as pd
            if not isinstance(df, pd.DataFrame):
                raise ValidationError("Input must be a pandas DataFrame")
                
            if required_columns:
                missing_columns = set(required_columns) - set(df.columns)
                if missing_columns:
                    raise ValidationError(f"Missing required columns: {missing_columns}")
                    
            if len(df) < min_rows:
                raise ValidationError(f"DataFrame must have at least {min_rows} rows")
                
        except ImportError:
            raise ValidationError("pandas is required for DataFrame operations")

    @staticmethod
    def validate_transform_operation(
        transform: Union[str, callable],
        allowed_transforms: Set[str]
    ) -> None:
        """
        Validate DataFrame transformation operation.
        
        Args:
            transform: Transformation to validate
            allowed_transforms: Set of allowed transformation names
            
        Raises:
            ValidationError: If validation fails
        """
        if isinstance(transform, str):
            if transform not in allowed_transforms:
                raise ValidationError(f"Invalid transformation: {transform}. "
                                   f"Allowed transforms: {allowed_transforms}")
        elif not callable(transform):
            raise ValidationError("Transform must be either a string or callable")