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
from src.db_templates.database_target_engine_modules_enum_contraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
    ChangeDefaultUsernameAndPassword,
)
from src.utils import preload_default_parameters


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

    def __init__(self):
        self.target_database_engine_name = None
        self.target_database_engine_connect_option = None
        self.target_database_engine_template_config = None
        self._target_database_connection = None
        self._target_database_credentials = {
            "username": None,
            "password": None,
            "is_default": True,
        }
        self._target_database_connection_string = None
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
    def insert_database_record(self, table_name: str, data: Dict[str, Any]) -> int:
        """Insert single database record and return inserted id."""
        database_placeholder = self.target_database_engine_template_config.get(
            "PLACEHOLDER", "?"
        )
        database_columns = ",".join(data.keys())
        database_placeholders = ",".join([database_placeholder] * len(data))
        database_query = f"INSERT INTO {table_name} ({database_columns}) VALUES ({database_placeholders})"

        with self._database_cursor() as cursor:
            cursor.execute(database_query, list(data.values()))
            self._target_database_connection.commit()
            return cursor.lastrowid

    def bulk_insert_database_records(
        self, table_name: str, records: List[Dict[str, Any]]
    ) -> None:
        """Insert multiple database records."""
        if not records:
            return

        database_placeholder = self.target_database_engine_template_config.get(
            "PLACEHOLDER", "?"
        )
        database_columns = ",".join(records[0].keys())
        database_placeholders = ",".join([database_placeholder] * len(records[0]))
        database_query = f"INSERT INTO {table_name} ({database_columns}) VALUES ({database_placeholders})"

        with self._database_cursor() as cursor:
            cursor.executemany(
                database_query, [list(record.values()) for record in records]
            )
            self._target_database_connection.commit()

    def update_database_records(
        self, table_name: str, data: Dict[str, Any], where: Dict[str, Any]
    ) -> int:
        """Update database records matching criteria."""
        database_placeholder = self.target_database_engine_template_config.get(
            "PLACEHOLDER", "?"
        )
        set_clause = ",".join(f"{k}={database_placeholder}" for k in data.keys())
        where_clause = " AND ".join(f"{k}={database_placeholder}" for k in where.keys())
        database_query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

        with self._database_cursor() as cursor:
            cursor.execute(database_query, list(data.values()) + list(where.values()))
            self._target_database_connection.commit()
            return cursor.rowcount

    def delete_database_records(self, table_name: str, where: Dict[str, Any]) -> int:
        """Delete database records matching criteria."""
        database_placeholder = self.target_database_engine_template_config.get(
            "PLACEHOLDER", "?"
        )
        where_clause = " AND ".join(f"{k}={database_placeholder}" for k in where.keys())
        database_query = f"DELETE FROM {table_name} WHERE {where_clause}"

        with self._database_cursor() as cursor:
            cursor.execute(database_query, list(where.values()))
            self._target_database_connection.commit()
            return cursor.rowcount

    def select_database_records(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Select database records with optional column and where clause filters."""
        database_placeholder = self.target_database_engine_template_config.get(
            "PLACEHOLDER", "?"
        )
        database_cols = ",".join(columns) if columns else "*"
        database_query = f"SELECT {database_cols} FROM {table_name}"
        database_params = []

        if where:
            where_clause = " AND ".join(
                f"{k}={database_placeholder}" for k in where.keys()
            )
            database_query += f" WHERE {where_clause}"
            database_params = list(where.values())

        with self._database_cursor() as cursor:
            cursor.execute(database_query, database_params)
            database_columns = [column[0] for column in cursor.description]
            return [dict(zip(database_columns, row)) for row in cursor.fetchall()]

    # Database Transaction Management
    @contextmanager
    def database_transaction(self):
        """Context manager for database transaction handling."""
        if hasattr(self._target_database_connection, "autocommit"):
            previous_autocommit = self._target_database_connection.autocommit
            self._target_database_connection.autocommit = False

        try:
            yield
            self._target_database_connection.commit()
        except Exception as e:
            self._target_database_connection.rollback()
            raise DatabaseError(f"Database transaction failed: {e}")
        finally:
            if hasattr(self._target_database_connection, "autocommit"):
                self._target_database_connection.autocommit = previous_autocommit

    def begin_database_transaction(self) -> None:
        """Start a new database transaction."""
        if hasattr(self._target_database_connection, "autocommit"):
            self._target_database_connection.autocommit = False

    def commit_database_transaction(self) -> None:
        """Commit current database transaction."""
        self._target_database_connection.commit()

    def rollback_database_transaction(self) -> None:
        """Rollback current database transaction."""
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
