from enum import Enum
from typing import Dict, Any, Type
from abc import ABC, abstractmethod

class TargetDatabaseEngine(Enum):
    """Database engines supported by pydbconnect."""
    MSSQL = "MSSQL"
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    SQLITE3 = "SQLITE3"
    DUCKDB = "DUCKDB"
    PSYCOPG2 = "PSYCOPG2"

    @property
    def requires_authentication(self) -> bool:
        """Check if engine requires username/password authentication."""
        return self in (self.MSSQL, self.MYSQL, self.POSTGRESQL, self.PSYCOPG2)
    
    @property
    def supports_dsn(self) -> bool:
        """Check if engine supports DSN connections."""
        return self in (self.MSSQL, self.MYSQL, self.POSTGRESQL)
    
    @property
    def import_module(self) -> str:
        """Get the Python module name required for this engine."""
        module_map = {
            self.MSSQL: "pyodbc",
            self.MYSQL: "pyodbc",
            self.POSTGRESQL: "pyodbc",
            self.SQLITE3: "pyodbc",
            self.DUCKDB: "duckdb",
            self.PSYCOPG2: "psycopg2"
        }
        return module_map[self]

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