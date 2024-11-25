""" Database Connector Module """
from getpass import getpass
import logging
from typing import Any, Dict, Optional, Union, List
from contextlib import contextmanager
import importlib
import pandas as pd
from pandas import DataFrame
from prettytable import PrettyTable
from pathlib import Path
from dotenv import load_dotenv
# from ..src.db_templates.database_target_engine_template_modules import MSSQL, MYSQL, POSTGRESQL,SQLITE3,DUCKDB,PSYCOPG2 as template
# from ..src.db_templates.database_target_engine_modules_enum_contraints import DatabaseConnectionError, TargetDatabaseEngine, TargetDatabaseConnectionStringOption, ChangeDefaultUsernameAndPassword
# from ..src.exceptions import DatabaseError, ChangeDefaultUsernameAndPassword,DSNUnsupportedByTragetEngineError 
# from ..src.utils import preload_default_parameters
#from .base_database_connector_wip import BaseDatabaseConnector, DatabaseError, DatabaseCredentialsError, DatabaseConnectionError

from pydbconnect.src.db_templates.database_target_engine_template_modules import MSSQL, MYSQL, POSTGRESQL, SQLITE3, DUCKDB, PSYCOPG2 as template
from pydbconnect.src.db_templates.database_target_engine_modules_enum_contraints import DatabaseConnectionError, TargetDatabaseEngine, TargetDatabaseConnectionStringOption, ChangeDefaultUsernameAndPassword
from pydbconnect.src.exceptions import DatabaseError, ChangeDefaultUsernameAndPassword, DSNUnsupportedByTragetEngineError
from pydbconnect.src.utils import preload_default_parameters
from pydbconnect.base_database_connector_wip import BaseDatabaseConnector, DatabaseError, DatabaseCredentialsError, DatabaseConnectionError


class DatabaseConnector(BaseDatabaseConnector):
    """Single target database connector implementation."""
   
    def __init__(self, 
                target_database_engine_type: TargetDatabaseEngine,
                target_database_engine_connect_option: TargetDatabaseConnectionStringOption):
        """Initialize target database connection with specified engine and options."""
        super().__init__()
        self.target_database_engine_type = target_database_engine_type
        self.target_database_engine_name = self.target_database_engine_type.name
        self.target_database_engine_connect_option = self.check_if_dsn_is_supported()
        self.target_database_engine_template_config = self._load_target_database_engine_template_config()
        self.change_database_usr_and_pwd_option = target_database_engine_connect_option.changes_credentials

    def check_if_dsn_is_supported(self) -> 'TargetDatabaseConnectionStringOption':
        """Check if DSN is supported by target database engine."""

        if not self.target_database_engine_type.supports_dsn and self.target_database_engine_connect_option.uses_dsn:
            raise DSNUnsupportedByTragetEngineError(
                f"DSN connections are not supported by {self.target_database_engine_name}"
            )
        return self.target_database_engine_connect_option

    def _load_target_database_engine_template_config(self) -> Dict[str, Any]:
       """Load target database engine-specific configuration."""
       try:
           return getattr(template, self.target_database_engine_name)
       except AttributeError as e:
           raise DatabaseError(
               f"Unsupported target database engine: {self.target_database_engine_name}"
           ) from e

    def set_credentials_based_on_connect_option(
       self, 
       show_password: bool = False   ) -> 'BaseDatabaseConnector':
       """Change target database credentials."""
       
       if ChangeDefaultUsernameAndPassword.changes_default_credentials(self.change_database_usr_and_pwd_option):
           database_username = input("Enter database username: ")
           database_password = (
               input("Enter database password: ") 
               if ChangeDefaultUsernameAndPassword.show_password(show_password) 
               else getpass("Enter database password: ")
           )
           
           self._target_database_credentials.update({
               'username': database_username,
               'password': database_password,
               'is_default': False
           })
       
       return self

    def _build_database_connection_string(self, params: Dict[str, Any]=None) -> str:
       """Build target database connection string from parameters."""
       try:

        if params is None:
            return {}  # Return empty dict when called without params for default parameters
        database_template = (
            self.target_database_engine_template_config['DSN_TEMPLATE'] 
            if self.target_database_engine_connect_option.uses_dsn 
            else self.target_database_engine_template_config['CONNECTION_TEMPLATE']
           )
        return database_template.format(**params)
    
       except KeyError as e:
           raise DatabaseError(f"Invalid database connection template parameter: {e}")

    @preload_default_parameters(preloaded_params_method=_build_database_connection_string)
    def finalization_of_database_connection_parameters(self, **params) -> 'DatabaseConnector':
        """Finalize target database connection parameters with custom values."""
        try:
            database_default_params = self.target_database_engine_template_config['DEFAULT_PARAMETERS'].copy()
            database_default_params.update(params)
            
            if self.target_database_engine_template_config['REQUIRES_CREDENTIALS']:
                if not all([
                    self._target_database_credentials['username'], 
                    self._target_database_credentials['password']
                ]):
                    raise DatabaseCredentialsError("Database username and password required but not provided")
                    
                database_default_params.update({
                    'USERNAME': self._target_database_credentials['username'],
                    'PASSWORD': self._target_database_credentials['password']
                })
            
            self._target_database_connection_string = self._build_database_connection_string(
                database_default_params
            )
            return self
        except KeyError as e:
            raise DatabaseError(f"Missing required database parameter: {e}")

    def connect_to_database(self) -> 'DatabaseConnector':
       """Establish target database connection."""
       try:
           target_database_module_name = self.target_database_engine_template_config['MODULE']
           target_database_module = importlib.import_module(target_database_module_name)
           self._target_database_connection = target_database_module.connect(
               self._target_database_connection_string
           )
           return self
       except Exception as e:
           raise DatabaseConnectionError(f"Failed to connect to target database: {e}")

   # Database Query Methods
    def execute_database_query_to_dataframe(
       self, 
       database_query: str, 
       index_col: Optional[str] = None
   ) -> pd.DataFrame:
       """Execute target database query and return results as DataFrame."""
       return super().execute_database_query_to_dataframe(database_query, index_col)

    def execute_database_query_to_prettytable(
       self, 
       database_query: str, 
       is_print: bool = False
   ) -> Optional[PrettyTable]:
       """Execute target database query and return/print results as PrettyTable."""
       return super().execute_database_query_to_prettytable(database_query, is_print)

   # Database CRUD Operations
    def insert_database_record(
       self, 
       table_name: str, 
       data: Dict[str, Any]
   ) -> int:
       """Insert single target database record and return inserted id."""
       return super().insert_database_record(table_name, data)

    def bulk_insert_database_records(
       self, 
       table_name: str, 
       records: List[Dict[str, Any]]
   ) -> None:
       """Insert multiple target database records."""
       super().bulk_insert_database_records(table_name, records)

    def update_database_records(
       self, 
       table_name: str, 
       data: Dict[str, Any], 
       where: Dict[str, Any]
   ) -> int:
       """Update target database records matching criteria."""
       return super().update_database_records(table_name, data, where)

    def delete_database_records(
       self, 
       table_name: str, 
       where: Dict[str, Any]
   ) -> int:
       """Delete target database records matching criteria."""
       return super().delete_database_records(table_name, where)

    def select_database_records(
       self, 
       table_name: str, 
       columns: Optional[List[str]] = None, 
       where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
       """Select target database records with optional filters."""
       return super().select_database_records(table_name, columns, where)

   # Database Transaction Management
    @contextmanager
    def database_transaction(self):
       """Context manager for target database transaction handling."""
       with super().database_transaction():
           yield

    def begin_database_transaction(self) -> None:
       """Start a new target database transaction."""
       super().begin_database_transaction()

    def commit_database_transaction(self) -> None:
       """Commit current target database transaction."""
       super().commit_database_transaction()

    def rollback_database_transaction(self) -> None:
       """Rollback current target database transaction."""
       super().rollback_database_transaction()

    def create_database_savepoint(self, savepoint_name: str) -> None:
       """Create a target database transaction savepoint."""
       super().create_database_savepoint(savepoint_name)

    def rollback_to_database_savepoint(self, savepoint_name: str) -> None:
       """Rollback to specified target database savepoint."""
       super().rollback_to_database_savepoint(savepoint_name)

   # Database Stored Procedures
    def execute_database_procedure(
       self, 
       procedure_name: str, 
       procedure_params: Optional[List[Any]] = None
    ) -> Optional[List[Any]]:
       """Execute target database stored procedure with optional parameters."""
       return super().execute_database_procedure(procedure_name, procedure_params)

   # Database Backup and Restore
    def backup_target_database(self, backup_path: str) -> None:
       """Backup target database to specified path."""
       super().backup_target_database(backup_path)

    def restore_target_database(self, restore_path: str) -> None:
       """Restore target database from specified path."""
       super().restore_target_database(restore_path)

   # Database Custom Methods
    def set_credentials_based_on_connect_option(
       self, 
       show_password: bool = False   ) -> 'DatabaseConnector':
       """Change target database credentials."""
       
       if ChangeDefaultUsernameAndPassword.changes_default_credentials(self.change_database_usr_and_pwd_option):
           database_username = input("Enter database username: ")
           database_password = (
               input("Enter database password: ") 
               if ChangeDefaultUsernameAndPassword.show_password(show_password) 
               else getpass("Enter database password: ")
           )
           
           self._target_database_credentials.update({
               'username': database_username,
               'password': database_password,
               'is_default': False
           })
       
       return self


   # Database Context Manager
    def __enter__(self) -> 'DatabaseConnector':
       """Target database context manager entry."""
       return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
       """Target database context manager exit with cleanup."""
       super().__exit__(exc_type, exc_val, exc_tb)

    def close_database_connection(self) -> None:
       """Close target database connection."""
       super().close_database_connection()

# test_module.py - For testing the dunder methods
def main():
    # Create instance
    db = DatabaseConnector(TargetDatabaseEngine.MSSQL, TargetDatabaseConnectionStringOption.Customize_DSN_AndChangeUserPwd) \
        .set_credentials_based_on_connect_option(show_password=True) \
        .finalize_database_connection_parameters(
            host="localhost",
            port=13001,
            database="Northwinds2024Student"
        )  \
        .connect_to_database()

# if __name__ == "__main__":
main()    