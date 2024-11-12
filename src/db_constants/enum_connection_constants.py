from enum import Enum
from typing import Dict, Any, Type
from abc import ABC, abstractmethod
import importlib

class TargetDatabaseEngine(Enum):
    """Database engines supported by pydbconnect."""
    MSSQL = "MSSQL"
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    SQLITE3 = "SQLITE3"
    DUCKDB = "DUCKDB"
    PSYCOPG2 = "PSYCOPG2"

    def __init__(self, value: str):
        """Initialize enum with target database engine name."""
        
        # Initialize target_database_engine_name in __init__
        # Use target_database_engine_name consistently across all methods
        # Maintain the enum's value through _value_    
        
        self._value_ = value
        self.target_database_engine_name = self.name

    @property
    def target_database_engine_name(self) -> str:
        """Get the name of the target database engine."""
        return self.name

    @property
    def requires_authentication(self) -> bool:
        """
        Check if engine requires username/password authentication.
        Gets value from engine configuration.
        """
        from . import templates
        engine_config = getattr(templates, self.target_database_engine_name)
        return engine_config.get('REQUIRES_CREDENTIALS', False)

    @property
    def supports_dsn(self) -> bool:
        """
        Check if engine supports DSN connections.
        Gets value from engine configuration.
        """
        from . import templates
        engine_config = getattr(templates, self.target_database_engine_name)
        return engine_config.get('FORMAT_CONNECTION_STRING', {}).get('IS_DSN_NAME_SUPPORTED', False)

    @property
    def import_module(self) -> str:
        """
        Get the Python module name required for this engine.
        Gets value from engine configuration.
        """
        from . import templates
        engine_config = getattr(templates, self.target_database_engine_name)
        return engine_config.get('CRUDBASIC', {}).get('IMPORT', '')

    def load_engine_config(self) -> Dict[str, Any]:
        """Load complete engine configuration."""
        from . import templates
        return getattr(templates, self.target_database_engine_name)

    def get_placeholder(self) -> str:
        """Get SQL parameter placeholder for this engine."""
        engine_config = self.load_engine_config()
        return engine_config.get('CRUDBASIC', {}).get('PARAMETER_PLACEHOLDER', '?')
        
    def validate_connection_option(self, option: 'TargetDatabaseConnectionStringOption') -> bool:
        """
        Validate if the connection option is compatible with this engine.
        
        Args:
            option: The connection option to validate
            
        Returns:
            bool: True if option is compatible, False otherwise
        """
        # DSN validation
        if option.uses_dsn and not self.supports_dsn:
            return False
            
        # Authentication validation
        if option.changes_credentials and not self.requires_authentication:
            return False
            
        return True
    
    def get_admin_handler(self) -> 'DatabaseAdminTemplate':
        """
        Get appropriate admin handler based on engine configuration.
        """
        try:
            from . import templates
            engine_config = getattr(templates, self.value)
            
            handler_class = engine_config.get('ADMIN_HANDLER')
            if not handler_class:
                raise ValueError(f"No admin handler configured for {self.value}")
                
            return handler_class()
            
        except Exception as e:
            raise ValueError(f"Error creating admin handler for {self.value}: {str(e)}")

class DatabaseAdminTemplate(ABC):
    """Abstract base class for database administration."""
    
    @abstractmethod
    def backup_database(self, path: str) -> None:
        """Backup database to specified path."""
        pass
    
    @abstractmethod
    def restore_database(self, path: str) -> None:
        """Restore database from specified path."""
        pass

class TargetDatabaseConnectionStringOption(Enum):
    """Connection string options for database connections."""
    
    # Standard connection strings
    DefaultFormatAndDefaultUserPwd = 1
    DefaultFormatAndChangeUserPwd = 2
    CustomizeFormatAndDefaultUserPwd = 3
    CustomizeFormatAndChangeUserPwd = 4
    
    # DSN connection strings
    Default_DSN_AndDefaultUserPwd = 5
    Default_DSN_AndChangeUserPwd = 6
    Customize_DSN_AndDefaultUserPwd = 7
    Customize_DSN_AndChangeUserPwd = 8

    @property
    def uses_dsn(self) -> bool:
        """Check if this option uses DSN connection."""
        return self.value >= 5
    
    @property
    def changes_credentials(self) -> bool:
        """Check if this option requires credential changes."""
        return self.value in [2, 4, 6, 8]
    
    @property
    def uses_custom_format(self) -> bool:
        """Check if this option uses custom connection string format."""
        return self.value in [3, 4, 7, 8]

    def validate_for_engine(self, engine: TargetDatabaseEngine) -> bool:
        """
        Validate if this option is compatible with given database engine.
        
        Args:
            engine: The database engine to validate against
            
        Returns:
            bool: True if compatible, False otherwise
        """
        return engine.validate_connection_option(self)

class DatabaseConnectionError(Exception):
    """Base exception for database connection errors."""
    pass

class InvalidConnectionOptionError(DatabaseConnectionError):
    """Raised when connection option is incompatible with database engine."""
    
    def __init__(self, engine: TargetDatabaseEngine, option: TargetDatabaseConnectionStringOption):
        self.engine = engine
        self.option = option
        message = f"Connection option {option.name} is not compatible with {engine.name}"
        super().__init__(message)