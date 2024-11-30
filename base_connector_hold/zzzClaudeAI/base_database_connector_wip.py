# base_database_connector.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from contextlib import contextmanager
import pandas as pd
from pathlib import Path
from getpass import getpass
from dotenv import load_dotenv
import importlib
from prettytable import PrettyTable
from datetime import datetime
import os

from src.db_templates.database_target_engine_modules_enum_contraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
    ChangeDefaultUsernameAndPassword,
)
from src.utils import preload_default_parameters
from src.descriptors import CredentialsDescriptor, ConnectionManager


class DatabaseError(Exception):
    """Base exception for database operations"""

    pass


class DatabaseConnectionError(DatabaseError):
    """Exception raised for database connection failures"""

    pass


class DatabaseCredentialsError(DatabaseError):
    """Exception raised for database credential issues"""

    pass


class BaseDatabaseConnector(ABC):
    """Abstract base class defining common database connection behavior."""

    _credentials = CredentialsDescriptor("credentials")

    def __init__(self):
        self.target_database_engine_name = None
        self.target_database_engine_template_config: Dict[str, Any] = {}
        self._target_database_connection = None
        self._target_database_credentials = {
            "username": None,
            "password": None,
            "is_default": True,
        }
        self._target_database_connection_string: Optional[str] = None
        self._load_database_environment()
        self._finalized_connection_parameters = None
        self.is_database_active = False
        self.database_attached_at = datetime.now()
        self.database_detached_at = None

    def _load_database_environment(self) -> None:
        """Load database environment variables from .env file."""
        database_env_path = Path(".") / ".env"
        if database_env_path.exists():
            load_dotenv(database_env_path)
            if self.target_database_engine_name:  # Add this block only
                self._target_database_credentials = {
                    "username": os.getenv(
                        f"{self.target_database_engine_name}_USERNAME", None
                    ),
                    "password": os.getenv(
                        f"{self.target_database_engine_name}_PASSWORD", None
                    ),
                    "is_default": True,
                }

    @abstractmethod
    def _load_target_database_engine_template_config(self) -> Dict[str, Any]:
        """Load target database engine-specific configuration."""
        pass

    @abstractmethod
    def set_credentials_based_on_connect_option(
        self, show_password: bool = False
    ) -> "BaseDatabaseConnector":
        """Abstract method for changing target database credentials."""
        pass

    @abstractmethod
    def select_database_records(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Abstract method for selecting database records.

        Args:
            table_name (str): Name of the target table
            columns (Optional[List[str]], optional): List of columns to select. Defaults to None.
            where (Optional[Dict[str, Any]], optional): Where clause conditions. Defaults to None.

        Returns:
            List[Dict[str, Any]]: List of records as dictionaries

        Raises:
            DatabaseError: If selection operation fails
        """
        pass

    @contextmanager
    def _database_cursor(self):
        """Context manager for database cursor handling."""
        if not self._target_database_connection:
            raise DatabaseConnectionError("No active database connection")
        database_cursor = self._target_database_connection.cursor()
        try:
            yield database_cursor
        finally:
            database_cursor.close()

    def connect_to_database(self) -> "BaseDatabaseConnector":
        """Establish target database connection."""
        if not self.target_database_engine_template_config:
            raise DatabaseError("Target database engine template config is not loaded")

        try:
            database_module_name = self.target_database_engine_template_config["MODULE"]
            database_module = importlib.import_module(database_module_name)
            self._target_database_connection = database_module.connect(
                self._target_database_connection_string
            )
            return self
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {e}")

    # Core Database Query Methods
    def execute_database_query_to_dataframe(
        self, database_query: str, index_col: Optional[str] = None
    ) -> pd.DataFrame:
        """Execute database query and return results as DataFrame."""
        if not self._target_database_connection:
            raise DatabaseConnectionError("No active database connection")
        try:
            return pd.read_sql(
                database_query, self._target_database_connection, index_col=index_col
            )
        except Exception as e:
            raise DatabaseError(f"Database query execution failed: {e}")

    def execute_database_query_to_prettytable(
        self, database_query: str, is_print: bool = False
    ) -> Optional[PrettyTable]:
        """Execute database query and return/print results as PrettyTable."""
        with self._database_cursor() as cursor:
            try:
                cursor.execute(database_query)
                database_table = PrettyTable()
                database_table.field_names = [col[0] for col in cursor.description]
                database_table.add_rows(cursor.fetchall())

                if is_print:
                    print(database_table)
                    return None
                return database_table
            except Exception as e:
                raise DatabaseError(f"Database query execution failed: {e}")

    # Database CRUD Operations

    # Then modify any methods that access the config to handle the typing properly
    def _get_database_placeholder(self) -> str:
        """Get database placeholder safely with proper type handling."""
        try:
            crud_basic = self.target_database_engine_template_config.get(
                "CRUDBASIC", {}
            )
            return crud_basic.get("PLACEHOLDER", "?")
        except Exception:
            return "?"

    def _has_transaction_support(self) -> bool:
        """Check if database supports transactions."""
        return self._target_database_connection is not None and hasattr(
            self._target_database_connection, "commit"
        )

    def commit(self) -> None:
        """Commit transaction if supported."""
        if self._target_database_connection is not None:
            self._target_database_connection.commit()

    def rollback(self) -> None:
        """Rollback transaction if supported."""
        if self._target_database_connection is not None:
            self._target_database_connection.rollback()

    @abstractmethod
    def insert_database_record(self, table_name: str, data: Dict[str, Any]) -> int:
        """Abstract method for inserting a single database record.

        Args:
            table_name (str): Name of the target table
            data (Dict[str, Any]): Dictionary of column names and values to insert

        Returns:
            int: ID of the inserted record

        Raises:
            DatabaseError: If insert operation fails
        """
        pass

    @abstractmethod
    def bulk_insert_database_records(
        self, table_name: str, records: List[Dict[str, Any]]
    ) -> None:
        """Abstract method for inserting multiple database records.

        Args:
            table_name (str): Name of the target table
            records (List[Dict[str, Any]]): List of records to insert

        Raises:
            DatabaseError: If bulk insert operation fails
        """
        pass

    @abstractmethod
    def update_database_records(
        self, table_name: str, data: Dict[str, Any], where: Dict[str, Any]
    ) -> int:
        """Abstract method for updating database records.

        Args:
            table_name (str): Name of the target table
            data (Dict[str, Any]): Dictionary of column names and values to update
            where (Dict[str, Any]): Where clause conditions

        Returns:
            int: Number of records updated

        Raises:
            DatabaseError: If update operation fails
        """
        pass

    @abstractmethod
    def delete_database_records(self, table_name: str, where: Dict[str, Any]) -> int:
        """Abstract method for deleting database records.

        Args:
            table_name (str): Name of the target table
            where (Dict[str, Any]): Where clause conditions

        Returns:
            int: Number of records deleted

        Raises:
            DatabaseError: If delete operation fails
        """
        pass

    # Database Transaction Management
    @contextmanager
    def database_transaction(self):
        """Context manager for database transaction handling."""
        if self._target_database_connection is None:
            raise DatabaseConnectionError("No active database connection")

        previous_autocommit = False
        if hasattr(self._target_database_connection, "autocommit"):
            previous_autocommit = getattr(
                self._target_database_connection, "autocommit", False
            )
            setattr(self._target_database_connection, "autocommit", False)

        try:
            yield
            if self._target_database_connection is not None:
                self._target_database_connection.commit()
        except Exception as e:
            if self._target_database_connection is not None:
                self._target_database_connection.rollback()
            raise DatabaseError(f"Database transaction failed: {e}")
        finally:
            if self._target_database_connection is not None and hasattr(
                self._target_database_connection, "autocommit"
            ):
                setattr(
                    self._target_database_connection, "autocommit", previous_autocommit
                )

    def begin_database_transaction(self) -> None:
        """Start a new database transaction."""
        if self._target_database_connection is not None:
            if hasattr(self._target_database_connection, "autocommit"):
                setattr(self._target_database_connection, "autocommit", False)

    def commit_database_transaction(self) -> None:
        """Commit current database transaction."""
        if self._target_database_connection is not None:
            self._target_database_connection.commit()

    def rollback_database_transaction(self) -> None:
        """Rollback current database transaction."""
        if self._target_database_connection is not None:
            self._target_database_connection.rollback()

    def create_database_savepoint(self, savepoint_name: str) -> None:
        """Create a database transaction savepoint."""
        with self._database_cursor() as cursor:
            cursor.execute(f"SAVEPOINT {savepoint_name}")

    def rollback_to_database_savepoint(self, savepoint_name: str) -> None:
        """Rollback to specified database savepoint."""
        with self._database_cursor() as cursor:
            cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")

    # Database Stored Procedures
    def execute_database_procedure(
        self, procedure_name: str, procedure_params: Optional[List[Any]] = None
    ) -> Optional[List[Any]]:
        """Execute database stored procedure with optional parameters."""
        with self._database_cursor() as cursor:
            if procedure_params:
                cursor.callproc(procedure_name, procedure_params)
            else:
                cursor.callproc(procedure_name)
            try:
                return cursor.fetchall()
            except:
                return None

    # Database Backup and Restore
    def backup_target_database(self, backup_path: str) -> None:
        """Backup target database to specified path."""
        database_backup_command = self.target_database_engine_template_config.get(
            "BACKUP_COMMAND", ""
        ).format(path=backup_path)

        if not database_backup_command:
            raise DatabaseError(
                f"Backup not supported for {self.target_database_engine_name}"
            )

        with self._database_cursor() as cursor:
            cursor.execute(database_backup_command)

    def restore_target_database(self, restore_path: str) -> None:
        """Restore target database from specified path."""
        database_restore_command = self.target_database_engine_template_config.get(
            "RESTORE_COMMAND", ""
        ).format(path=restore_path)

        if not database_restore_command:
            raise DatabaseError(
                f"Restore not supported for {self.target_database_engine_name}"
            )

        with self._database_cursor() as cursor:
            cursor.execute(database_restore_command)

    # Database Context Manager Support
    def __enter__(self):
        """Database context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Database context manager exit with connection cleanup."""
        if self._target_database_connection:
            try:
                self._target_database_connection.close()
            except Exception:
                pass

    def close_database_connection(self):
        """Explicitly close the target database connection."""
        if self._target_database_connection:
            self._target_database_connection.close()
            self._target_database_connection = None
