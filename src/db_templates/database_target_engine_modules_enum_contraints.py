from enum import Enum
from typing import Dict, Any, Type
from abc import ABC, abstractmethod
import importlib
import src.db_templates.database_target_engine_template_modules as templates

class  ChangeDefaultUsernameAndPassword(Enum):
    """Connection string options for database connections."""
    # Standard connection strings
    DoNotChangeUserAndPwd= 1
    ChangeUserAndPwd = 2
    ChangeUserAndPwdPlusShow = 3
    
    @property
    def change_default_username_and_password(self) -> str:
        """Get the name of the ChangeDefaultUsernameAndPassword."""
        return self.value
class TargetDatabaseEngine(Enum):
    """Database engines supported by pydbconnect."""
    MSSQL = "MSSQL"
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    SQLITE3 = "SQLITE3"
    DUCKDB = "DUCKDB"
    PSYCOPG2 = "PSYCOPG2"

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

        return self.engine_config.get('CREATE_DATABASE_CONNECTION', False).get('REQUIRES_CREDENTIALS', False)

    @property
    def engine_config(self) -> dict:
        """Get the configuration for this engine."""
        return getattr(templates, self.target_database_engine_name)
    
    @property
    def supports_dsn(self) -> bool:
        """
        Check if engine supports DSN connections.
        Gets value from engine configuration.
        """
        return self.engine_config.get('DEFAULT_PARAMETERS',{}).get('FORMAT_CONNECTION_STRING', {}).get('IS_DSN_NAME_SUPPORTED', False)

    @property
    def no_dsn_supports(self) -> int:
        """
        Check if engine does not support DSN connections.
        Gets value from engine configuration.
        """
        return 1 if not self.engine_config.get('DEFAULT_PARAMETERS',{}).get('FORMAT_CONNECTION_STRING', {}).get('IS_DSN_NAME_SUPPORTED', False) else 2
    
    @property
    def import_module(self) -> str:
        """
        Get the Python module name required for this engine.
        Gets value from engine configuration.
        """
        return self.engine_config.get('CRUDBASIC', {}).get('IMPORT', '')

    def load_engine_config(self) -> Dict[str, Any]:
        """Load complete engine configuration."""

        return getattr(templates, self.target_database_engine_name)

    def get_placeholder(self) -> str:
        """Get SQL parameter placeholder for this engine."""
        return self.engine_config.get('CRUDBASIC', {}).get('PARAMETER_PLACEHOLDER', '?')
        
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
            engine_config = getattr(templates, self.target_database_engine_name)
            
            handler_class = engine_config.get('ADMIN_HANDLER')
            if not handler_class:
                raise ValueError(f"No admin handler configured for {self.target_database_engine_name}")
                
            return handler_class()
            
        except Exception as e:
            raise ValueError(f"Error creating admin handler for {self.target_database_engine_name}: {str(e)}")

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
    def target_database_connection_string_option(self) -> str:
        """Get the name of the TargetDatabaseConnectionStringOption."""
        return self.name

    @property
    def uses_dsn(self) -> bool:
        """Check if this option uses DSN connection."""
        # if self.target_database_connection_string_option in [5, 6, 7, 8] use DSN connection
    
        uses_dsn_connection = (5, 6, 7, 8)
        return self.target_database_connection_string_option in uses_dsn_connection
    
    @property
    def changes_credentials(self) -> 'ChangeDefaultUsernameAndPassword':
        """Check if this option requires credential changes."""
        return ChangeDefaultUsernameAndPassword.ChangeUserAndPwd  if not (self.value % 2 == 0) else ChangeDefaultUsernameAndPassword.DoNotChangeUserAndPwd

    @property
    def allow_credential_changes(self) -> int:
        """ Check if this option allows credential changes."""
        
        #    class  ChangeDefaultUsernameAndPassword(Enum)
        #    DoNotChangeUserAndPwd= 1 
        #    ChangeUserAndPwd = 2
        #
        #   change_username_password if self.target_database_connection_string_option in [2, 4, 6, 8] else do_not_change_username_passord
        #
        do_not_change_username_passord =1
        change_username_password = 2
        return change_username_password if self.target_database_connection_string_option in (2, 4, 6, 8) else do_not_change_username_passord
    
    @property
    def uses_custom_format(self) -> bool:
        """Check if this option uses custom connection string format."""
        return True if self.target_database_connection_string_option in (3, 4, 7, 8) else False

    @property
    def changes_default_credentials(self) -> bool:
        """Check if this option requires credential changes."""
        return self.change_default_username_and_password in (2, 3)

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
    
    def __init__(self, target_database_engine: TargetDatabaseEngine, target_atabase_connection_option: TargetDatabaseConnectionStringOption):
        ''' f"Connection option {target_atabase_connection_option.name} is not compatible with {target_database_engine.name}" '''
        
        message = f"Connection option {target_atabase_connection_option.name} is not compatible with {target_database_engine.name}"
        super().__init__(message)
   
def test_enums():
    # Test accessing enum values
    print("\nTesting basic enum access:")
    print(f"Value of DefaultFormatAndDefaultUserPwd: {TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd.value}")
    print(f"Name of DefaultFormatAndDefaultUserPwd: {TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd.name}")
    
    # Test properties
    option = TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd
    print("\nTesting properties for DefaultFormatAndChangeUserPwd:")
    print(f"Uses DSN: {option.uses_dsn}")
    print(f"Changes credentials: {option.changes_credentials}")
    print(f"Allow credential changes: {option.allow_credential_changes}")
    print(f"Uses custom format: {option.uses_custom_format}")
    
    # Test DSN option
    dsn_option = TargetDatabaseConnectionStringOption.Default_DSN_AndDefaultUserPwd
    print("\nTesting DSN option:")
    print(f"Uses DSN: {dsn_option.uses_dsn}")
    print(f"Changes credentials: {dsn_option.changes_credentials}")

if __name__ == "__main__":
    test_enums()  