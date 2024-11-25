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

import src.db_templates.database_target_engine_template_modules as template

# Then you can access each template like:
# template.MSSQL
# template.MYSQL
# template.POSTGRESQL
# template.SQLITE3
# template.DUCKDB
# template.PSYCOPG2

from src.db_templates.database_target_engine_modules_enum_contraints import (
    DatabaseConnectionError,
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
    ChangeDefaultUsernameAndPassword,
)
from src.exceptions import DatabaseError, DSNUnsupportedByTragetEngineError
from src.utils import preload_default_parameters
from zzzClaudeAI.base_database_connector_wip import (
    BaseDatabaseConnector,
    DatabaseError,
    DatabaseCredentialsError,
    DatabaseConnectionError,
)


class DatabaseConnector(BaseDatabaseConnector):
    """Single target database connector implementation."""

    def _load_target_database_engine_template_config(self) -> Dict[str, Any]:
        """Load target database engine-specific configuration."""
        try:
            return getattr(template, self.target_database_engine_name)
        except AttributeError as e:
            raise DatabaseError(
                f"Unsupported target database engine: {self.target_database_engine_name}"
            ) from e

    def set_credentials_based_on_connect_option(
        self, show_password: bool = False
    ) -> "BaseDatabaseConnector":  # Note: Matches base class return type
        """Change target database credentials."""
        if self.change_database_usr_and_pwd_option.changes_default_credentials:
            database_username = input("Enter database username: ")
            database_password = (
                input("Enter database password: ")
                if show_password
                else getpass("Enter database password: ")
            )
            self._target_database_credentials.update(
                {
                    "username": database_username,
                    "password": database_password,
                    "is_default": False,
                }
            )
        return self

    def __init__(
        self,
        target_database_engine_type: TargetDatabaseEngine,
        target_database_engine_connect_option: TargetDatabaseConnectionStringOption,
    ):
        """Initialize target database connection with specified engine and options."""
        super().__init__()
        self.target_database_engine_type = target_database_engine_type
        self.target_database_engine_name = self.target_database_engine_type.name
        # Set connect option first
        self.target_database_engine_connect_option = (
            target_database_engine_connect_option
        )
        # Load config before DSN check
        self.target_database_engine_template_config = (
            self._load_target_database_engine_template_config()
        )
        # Validate DSN support
        self.check_if_dsn_is_supported()
        # Set credentials option
        self.change_database_usr_and_pwd_option = (
            target_database_engine_connect_option.changes_credentials
        )

    def check_if_dsn_is_supported(self) -> None:
        """Validate if DSN is supported by target database engine."""
        if (
            not self.target_database_engine_type.supports_dsn
            and self.target_database_engine_connect_option.uses_dsn
        ):
            raise DSNUnsupportedByTragetEngineError(
                f"DSN connections are not supported by {self.target_database_engine_name}"
            )

    def _build_database_connection_string(
        self, params: Dict[str, Any] | None = None  # Use Union type to allow None
    ) -> str:
        """Build target database connection string from parameters."""
        try:
            params = params or {}  # Convert None to empty dict

            database_template = (
                self.target_database_engine_template_config["DSN_TEMPLATE"]
                if self.target_database_engine_connect_option.uses_dsn
                else self.target_database_engine_template_config["CONNECTION_TEMPLATE"]
            )
            return database_template.format(**params)

        except KeyError as e:
            raise DatabaseError(f"Invalid database connection template parameter: {e}")

    @preload_default_parameters(
        preloaded_params_method=_build_database_connection_string
    )
    def finalization_of_database_connection_parameters(
        self, **params
    ) -> "BaseDatabaseConnector":
        """Finalize target database connection parameters with custom values."""
        try:
            database_default_params = self.target_database_engine_template_config[
                "DEFAULT_PARAMETERS"
            ].copy()
            database_default_params.update(params)

            if self.target_database_engine_template_config["REQUIRES_CREDENTIALS"]:
                if not all(
                    [
                        self._target_database_credentials["username"],
                        self._target_database_credentials["password"],
                    ]
                ):
                    raise DatabaseCredentialsError(
                        "Database username and password required but not provided"
                    )

                database_default_params.update(
                    {
                        "USERNAME": self._target_database_credentials["username"],
                        "PASSWORD": self._target_database_credentials["password"],
                    }
                )

            self._target_database_connection_string = (
                self._build_database_connection_string(database_default_params)
            )
            return self
        except KeyError as e:
            raise DatabaseError(f"Missing required database parameter: {e}")

    def connect_to_database(self) -> "DatabaseConnector":
        """Establish target database connection."""
        try:
            target_database_module_name = self.target_database_engine_template_config[
                "MODULE"
            ]
            target_database_module = importlib.import_module(
                target_database_module_name
            )
            self._target_database_connection = target_database_module.connect(
                self._target_database_connection_string
            )
            return self
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to connect to target database: {e}")

    # Database Query Methods
    def execute_database_query_to_dataframe(
        self, database_query: str, index_col: Optional[str] = None
    ) -> pd.DataFrame:
        """Execute target database query and return results as DataFrame."""
        return super().execute_database_query_to_dataframe(database_query, index_col)

    def execute_database_query_to_prettytable(
        self, database_query: str, is_print: bool = False
    ) -> Optional[PrettyTable]:
        """Execute target database query and return/print results as PrettyTable."""
        return super().execute_database_query_to_prettytable(database_query, is_print)

    # Database CRUD Operations
    def insert_database_record(self, table_name: str, data: Dict[str, Any]) -> int:
        """Insert single database record and return inserted id."""
        try:
            database_placeholder = self._get_database_placeholder()
            database_columns = ",".join(data.keys())
            database_placeholders = ",".join([database_placeholder] * len(data))
            database_query = f"INSERT INTO {table_name} ({database_columns}) VALUES ({database_placeholders})"

            with self._database_cursor() as cursor:
                try:
                    cursor.execute(database_query, list(data.values()))
                    self.commit()
                    return getattr(cursor, "lastrowid", 0)
                except Exception as e:
                    self.rollback()
                    raise DatabaseError(f"Insert operation failed: {e}")
        except Exception as e:
            raise DatabaseError(f"Failed to insert record: {e}")

    def bulk_insert_database_records(
        self, table_name: str, records: List[Dict[str, Any]]
    ) -> None:
        """Insert multiple database records."""
        if not records:
            return

        try:
            database_placeholder = self._get_database_placeholder()
            database_columns = ",".join(records[0].keys())
            database_placeholders = ",".join([database_placeholder] * len(records[0]))
            database_query = f"INSERT INTO {table_name} ({database_columns}) VALUES ({database_placeholders})"

            with self._database_cursor() as cursor:
                try:
                    cursor.executemany(
                        database_query, [list(record.values()) for record in records]
                    )
                    self.commit()
                except Exception as e:
                    self.rollback()
                    raise DatabaseError(f"Bulk insert operation failed: {e}")
        except Exception as e:
            raise DatabaseError(f"Failed to bulk insert records: {e}")

    def update_database_records(
        self, table_name: str, data: Dict[str, Any], where: Dict[str, Any]
    ) -> int:
        """Update database records matching criteria."""
        try:
            database_placeholder = self._get_database_placeholder()
            set_clause = ",".join(f"{k}={database_placeholder}" for k in data.keys())
            where_clause = " AND ".join(
                f"{k}={database_placeholder}" for k in where.keys()
            )
            database_query = (
                f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            )

            with self._database_cursor() as cursor:
                try:
                    cursor.execute(
                        database_query, list(data.values()) + list(where.values())
                    )
                    self.commit()
                    return cursor.rowcount
                except Exception as e:
                    self.rollback()
                    raise DatabaseError(f"Update operation failed: {e}")
        except Exception as e:
            raise DatabaseError(f"Failed to update records: {e}")

    def delete_database_records(self, table_name: str, where: Dict[str, Any]) -> int:
        """Delete database records matching criteria."""
        try:
            database_placeholder = self._get_database_placeholder()
            where_clause = " AND ".join(
                f"{k}={database_placeholder}" for k in where.keys()
            )
            database_query = f"DELETE FROM {table_name} WHERE {where_clause}"

            with self._database_cursor() as cursor:
                try:
                    cursor.execute(database_query, list(where.values()))
                    self.commit()
                    return cursor.rowcount
                except Exception as e:
                    self.rollback()
                    raise DatabaseError(f"Delete operation failed: {e}")
        except Exception as e:
            raise DatabaseError(f"Failed to delete records: {e}")

    def select_database_records(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Select database records with optional filters."""
        try:
            database_placeholder = self._get_database_placeholder()
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
        except Exception as e:
            raise DatabaseError(f"Failed to select records: {e}")

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
        self, procedure_name: str, procedure_params: Optional[List[Any]] = None
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

    # Database Context Manager
    def __enter__(self) -> "DatabaseConnector":
        """Target database context manager entry."""
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Target database context manager exit with cleanup."""
        super().__exit__(exc_type, exc_val, exc_tb)

    def close_database_connection(self) -> None:
        """Close target database connection."""
        super().close_database_connection()


# test_module.py - For testing the dunder methods
