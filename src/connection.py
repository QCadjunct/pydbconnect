import os
import logging
from typing import Any, Dict, Optional, Union
import importlib
import pandas as pd
from pandas import DataFrame
import pyodbc
from prettytable import PrettyTable
from pathlib import Path
from dotenv import load_dotenv

from .enums import TargetDatabaseEngine, TargetDatabaseConnectionStringOption

class DatabaseError(Exception):
    """Base exception for database operations"""
    pass

class ConnectionError(DatabaseError):
    """Exception raised for connection failures"""
    pass

class CredentialsError(DatabaseError):
    """Exception raised for credential issues"""
    pass

class DatabaseConnection:
    """
    A fluent interface for database connections supporting multiple engines.
    Uses method chaining for configuration and execution.
    """
    
    def __init__(self, engine_type: TargetDatabaseEngine, 
                 connect_option: TargetDatabaseConnectionStringOption):
        """Initialize database connection with specified engine and options."""
        self.engine_type = engine_type
        self.connect_option = connect_option
        
        # Load configuration
        self.engine_config = self._load_engine_config()
        
        # Initialize connection state
        self._connection = None
        self._credentials = {
            'username': None,
            'password': None,
            'is_default': True
        }
        
        # Load environment variables
        self._load_env()

    def _load_engine_config(self) -> Dict[str, Any]:
        """Load engine-specific configuration."""
        try:
            from . import templates
            return getattr(templates, self.engine_type.value)
        except AttributeError as e:
            raise DatabaseError(f"Unsupported database engine: {self.engine_type.value}") from e

    def _load_env(self) -> None:
        """Load environment variables from .env file."""
        env_path = Path('.') / '.env'
        if env_path.exists():
            load_dotenv(env_path)

    def change_default_username_and_password(self, show_password: bool = False) -> 'DatabaseConnection':
        """Change database credentials."""
        if self.connect_option.changes_credentials:
            username = input("Enter username: ")
            password = input("Enter password: ") if show_password else getpass("Enter password: ")
            
            self._credentials.update({
                'username': username,
                'password': password,
                'is_default': False
            })
            
        return self

    def finalization_of_connection_parameters(self, **params) -> 'DatabaseConnection':
        """Finalize connection parameters with custom values."""
        try:
            # Get default parameters from engine config
            default_params = self.engine_config['DEFAULT_PARAMETERS'].copy()
            
            # Update with custom parameters
            default_params.update(params)
            
            # Add credentials if required
            if self.engine_config['REQUIRES_CREDENTIALS']:
                if not all([self._credentials['username'], self._credentials['password']]):
                    raise CredentialsError("Username and password required but not provided")
                default_params.update({
                    'USERNAME': self._credentials['username'],
                    'PASSWORD': self._credentials['password']
                })
            
            # Build connection string
            self._connection_string = self._build_connection_string(default_params)
            
            return self
        except KeyError as e:
            raise DatabaseError(f"Missing required parameter: {e}")

    def _build_connection_string(self, params: Dict[str, Any]) -> str:
        """Build connection string from parameters."""
        try:
            if self.connect_option.uses_dsn:
                template = self.engine_config['DSN_TEMPLATE']
            else:
                template = self.engine_config['CONNECTION_TEMPLATE']
            return template.format(**params)
        except KeyError as e:
            raise DatabaseError(f"Invalid connection template parameter: {e}")

    def connect_to_database(self) -> 'DatabaseConnection':
        """Establish database connection."""
        try:
            module_name = self.engine_config['MODULE']
            module = importlib.import_module(module_name)
            self._connection = module.connect(self._connection_string)
            return self
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}")

    def execute_sql_to_dataframe(self, sql: str, index_col: Optional[str] = None) -> DataFrame:
        """Execute SQL and return results as DataFrame."""
        if not self._connection:
            raise ConnectionError("No active database connection")
        try:
            return pd.read_sql(sql, self._connection, index_col=index_col)
        except Exception as e:
            raise DatabaseError(f"Query execution failed: {e}")

    def execute_sql_to_prettytable(self, sql: str, is_print: bool = False) -> Optional[PrettyTable]:
        """Execute SQL and return/print results as PrettyTable."""
        if not self._connection:
            raise ConnectionError("No active database connection")
            
        try:
            cursor = self._connection.cursor()
            cursor.execute(sql)
            
            # Create PrettyTable
            table = PrettyTable()
            table.field_names = [col[0] for col in cursor.description]
            table.add_rows(cursor.fetchall())
            
            if is_print:
                print(table)
                return None
            return table
            
        except Exception as e:
            raise DatabaseError(f"Query execution failed: {e}")
        finally:
            cursor.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with connection cleanup."""
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass  # Silently handle closure errors
            