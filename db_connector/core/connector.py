"""Database Connector Implementation."""

from typing import Dict, Any, Optional, List
from contextlib import contextmanager
import importlib
import pandas as pd
from datetime import datetime
from pathlib import Path
from getpass import getpass
from dotenv import load_dotenv
from prettytable import PrettyTable
import os

from ..templates import engines as templates
from ..templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
    ChangeDefaultUsernameAndPassword,
)
from ..utils.decorators import preload_parameters, ensure_connected


class DatabaseError(Exception):
    """Base exception for database operations."""

    pass


class ConnectionError(DatabaseError):
    """Connection failure errors."""

    pass


class CredentialsError(DatabaseError):
    """Credential-related issues."""

    pass


class DatabaseConnector:
    """Database connector implementation."""

    def __init__(
        self,
        target_database_engine: TargetDatabaseEngine,
        target_database_engine_connect_option: TargetDatabaseConnectionStringOption,
    ):
        """Initialize database connector."""
        self.target_database_engine_type = target_database_engine
        self.target_database_engine_name = target_database_engine.name
        self.target_database_engine_connect_option = (
            target_database_engine_connect_option
        )

        # Core attributes
        self._connection = None
        self._credentials = {"username": None, "password": None, "is_default": True}
        self._connection_string = None

        # Load configuration
        self.engine_config = self._load_engine_config(templates)
        self.change_database_usr_and_pwd_option = (
            target_database_engine_connect_option.changes_credentials
        )

        # Validate DSN support
        self._validate_dsn_support()

        # Load environment and attach default credentials
        self._load_environment()

        # Track state
        self.is_database_active = False
        self.database_attached_at = None
        self.database_detached_at = None

    def _load_engine_config(self, templates) -> Dict[str, Any]:
        """Load engine-specific configuration."""
        try:
            return getattr(templates.engines, self.target_database_engine_name)
        except AttributeError as e:
            raise DatabaseError(
                f"Unsupported database engine: {self.target_database_engine_name}"
            ) from e

    def _load_environment(self) -> None:
        """Load environment variables."""
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)
            if self.target_database_engine_name:
                self._credentials.update(
                    {
                        "username": os.getenv(
                            f"{self.target_database_engine_name}_USERNAME"
                        ),
                        "password": os.getenv(
                            f"{self.target_database_engine_name}_PASSWORD"
                        ),
                        "is_default": True,
                    }
                )

    def _validate_dsn_support(self) -> None:
        """Validate DSN support for engine."""
        if (
            not self.target_database_engine_type.supports_dsn
            and self.target_database_engine_connect_option.uses_dsn
        ):
            raise ConnectionError(
                f"DSN not supported by {self.target_database_engine_name}"
            )

    def set_credentials_based_on_connect_option(
        self, show_password: bool = False
    ) -> "DatabaseConnector":
        """Set database credentials."""
        if self.change_database_usr_and_pwd_option.changes_default_credentials:
            username = input("Enter database username: ")
            password = (
                input("Enter database password: ")
                if show_password
                else getpass("Enter database password: ")
            )

            self._credentials.update(
                {"username": username, "password": password, "is_default": False}
            )
        return self

    def _build_connection_string(self, params: Dict[str, Any]) -> str:
        """Build connection string from parameters."""
        try:
            template = (
                self.engine_config["DSN_TEMPLATE"]
                if self.target_database_engine_connect_option.uses_dsn
                else self.engine_config["CONNECTION_TEMPLATE"]
            )
            return template.format(**params)
        except KeyError as e:
            raise DatabaseError(f"Invalid connection parameter: {e}")

    @preload_parameters(_build_connection_string)
    def finalization_of_connection_parameters(self, **params) -> "DatabaseConnector":
        """Finalize connection parameters."""
        try:
            # Add credentials if required
            if self.engine_config["REQUIRES_CREDENTIALS"]:
                if not all(
                    [self._credentials["username"], self._credentials["password"]]
                ):
                    raise CredentialsError(
                        "Username and password required but not provided"
                    )

                params.update(
                    {
                        "username": self._credentials["username"],
                        "password": self._credentials["password"],
                    }
                )

            self._connection_string = self._build_connection_string(params)
            return self
        except Exception as e:
            raise DatabaseError(f"Failed to finalize connection parameters: {e}")

    def connect_to_database(self) -> "DatabaseConnector":
        """Establish database connection."""
        try:
            module_name = self.engine_config["MODULE"]
            module = importlib.import_module(module_name)
            self._connection = module.connect(self._connection_string)
            self.is_database_active = True
            self.database_attached_at = datetime.now()
            return self
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")

    @contextmanager
    def _cursor(self):
        """Context manager for database cursor."""
        if not self._connection:
            raise ConnectionError("No active connection")
        cursor = self._connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    @ensure_connected
    def execute_query_to_dataframe(
        self, query: str, index_col: Optional[str] = None
    ) -> pd.DataFrame:
        """Execute query and return results as DataFrame."""
        return pd.read_sql(query, self._connection, index_col=index_col)

    @ensure_connected
    def execute_query_to_prettytable(
        self, query: str, print_result: bool = False
    ) -> Optional[PrettyTable]:
        """Execute query and return/print results as PrettyTable."""
        with self._cursor() as cursor:
            cursor.execute(query)
            table = PrettyTable()
            table.field_names = [col[0] for col in cursor.description]
            table.add_rows(cursor.fetchall())

            if print_result:
                print(table)
                return None
            return table

    @contextmanager
    def transaction(self):
        """Transaction context manager."""
        if not self._connection:
            raise ConnectionError("No active connection")

        try:
            yield
            self._connection.commit()
        except Exception:
            self._connection.rollback()
            raise

    @ensure_connected
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert single record."""
        placeholder = self.engine_config["CRUDBASIC"]["PARAMETER_PLACEHOLDER"]
        columns = ",".join(data.keys())
        placeholders = ",".join([placeholder] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        with self._cursor() as cursor:
            try:
                cursor.execute(query, list(data.values()))
                self._connection.commit()
                return cursor.lastrowid
            except Exception as e:
                self._connection.rollback()
                raise DatabaseError(f"Insert failed: {e}")

    @ensure_connected
    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """Update records."""
        placeholder = self.engine_config["CRUDBASIC"]["PARAMETER_PLACEHOLDER"]
        set_clause = ",".join(f"{k}={placeholder}" for k in data)
        where_clause = " AND ".join(f"{k}={placeholder}" for k in where)
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

        with self._cursor() as cursor:
            try:
                cursor.execute(query, list(data.values()) + list(where.values()))
                self._connection.commit()
                return cursor.rowcount
            except Exception as e:
                self._connection.rollback()
                raise DatabaseError(f"Update failed: {e}")

    @ensure_connected
    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """Delete records."""
        placeholder = self.engine_config["CRUDBASIC"]["PARAMETER_PLACEHOLDER"]
        where_clause = " AND ".join(f"{k}={placeholder}" for k in where)
        query = f"DELETE FROM {table} WHERE {where_clause}"

        with self._cursor() as cursor:
            try:
                cursor.execute(query, list(where.values()))
                self._connection.commit()
                return cursor.rowcount
            except Exception as e:
                self._connection.rollback()
                raise DatabaseError(f"Delete failed: {e}")

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            try:
                self._connection.close()
            finally:
                self._connection = None
                self.is_database_active = False
                self.database_detached_at = datetime.now()

    def __enter__(self) -> "DatabaseConnector":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


def main():
    """Simple demonstration of DatabaseConnector."""
    try:
        # Initialize connector
        db = DatabaseConnector(
            target_database_engine=TargetDatabaseEngine.SQLITE3,
            target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
        )

        # Connect and execute simple query
        with db.finalization_of_connection_parameters(
            database=":memory:"
        ).connect_to_database() as conn:
            with conn._cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                print(f"Connection test result: {result[0]}")

    except DatabaseError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
