"""Multi-Database Connector Implementation."""

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


class MultiDatabaseConnector:
    """Multi-database connector implementation."""

    def __init__(self):
        """Initialize multi-database connector."""
        self.database_instances: Dict[str, Dict[str, Any]] = {}
        self.database_connections: Dict[str, Any] = {}
        self.active_database: Optional[str] = None
        self._active_transaction: Optional[str] = None

    def _load_engine_config(self, engine_name: str) -> Dict[str, Any]:
        """Load engine-specific configuration."""
        try:
            return getattr(self.templates.engines, engine_name)
        except AttributeError as e:
            raise DatabaseError(f"Unsupported database engine: {engine_name}") from e

    def _validate_dsn_support(
        self,
        engine_type: TargetDatabaseEngine,
        connect_option: TargetDatabaseConnectionStringOption,
    ) -> None:
        """Validate DSN support for engine."""
        if not engine_type.supports_dsn and connect_option.uses_dsn:
            raise ConnectionError(f"DSN not supported by {engine_type.name}")

    def attach_database(
        self,
        alias: str,
        engine_type: TargetDatabaseEngine,
        connect_option: TargetDatabaseConnectionStringOption,
    ) -> "MultiDatabaseConnector":
        """Attach a new database instance."""
        try:
            # Validate DSN support
            self._validate_dsn_support(engine_type, connect_option)

            # Load configuration
            engine_config = self._load_engine_config(engine_type.name)

            # Store instance information
            self.database_instances[alias] = {
                "engine_type": engine_type,
                "connect_option": connect_option,
                "config": engine_config,
                "credentials": {"username": None, "password": None, "is_default": True},
                "connection_string": None,
                "is_active": False,
                "attached_at": datetime.now(),
                "detached_at": None,
            }

            # Set as active if first database
            if not self.active_database:
                self.active_database = alias

            return self
        except Exception as e:
            raise DatabaseError(f"Failed to attach database {alias}: {str(e)}")

    def set_credentials(self, alias: str, show_password: bool = False) -> "MultiDatabaseConnector":
        """Set credentials for specified database."""
        if alias not in self.database_instances:
            raise DatabaseError(f"Database {alias} not attached")

        instance = self.database_instances[alias]
        if instance["config"]["REQUIRES_CREDENTIALS"]:
            username = input(f"Enter username for {alias}: ")
            password = (
                input(f"Enter password for {alias}: ") if show_password else getpass(f"Enter password for {alias}: ")
            )

            instance["credentials"].update({"username": username, "password": password, "is_default": False})

        return self

    def _build_connection_string(self, alias: str, params: Dict[str, Any]) -> str:
        """Build connection string for specified database."""
        try:
            instance = self.database_instances[alias]
            template = (
                instance["config"]["DSN_TEMPLATE"]
                if instance["connect_option"].uses_dsn
                else instance["config"]["CONNECTION_TEMPLATE"]
            )
            return template.format(**params)
        except KeyError as e:
            raise DatabaseError(f"Invalid connection parameter for {alias}: {e}")

    @preload_parameters(_build_connection_string)
    def prepare_connection(self, alias: str, **params) -> "MultiDatabaseConnector":
        """Prepare connection parameters for specified database."""
        try:
            instance = self.database_instances[alias]

            # Get default parameters
            default_params = instance["config"]["DEFAULT_PARAMETERS"].copy()
            default_params.update(params)

            # Add credentials if required
            if instance["config"]["REQUIRES_CREDENTIALS"]:
                if not all(
                    [
                        instance["credentials"]["username"],
                        instance["credentials"]["password"],
                    ]
                ):
                    raise CredentialsError(f"Credentials required for {alias}")

                default_params.update(
                    {
                        "username": instance["credentials"]["username"],
                        "password": instance["credentials"]["password"],
                    }
                )

            instance["connection_string"] = self._build_connection_string(alias, default_params)
            return self
        except Exception as e:
            raise DatabaseError(f"Failed to prepare connection for {alias}: {e}")

    def connect(self, alias: str) -> "MultiDatabaseConnector":
        """Connect to specified database."""
        try:
            instance = self.database_instances[alias]
            if not instance["connection_string"]:
                raise ConnectionError(f"Connection string not prepared for {alias}")

            module_name = instance["config"]["MODULE"]
            module = importlib.import_module(module_name)
            connection = module.connect(instance["connection_string"])

            self.database_connections[alias] = connection
            instance["is_active"] = True

            return self
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {alias}: {e}")

    def switch_database(self, alias: str) -> "MultiDatabaseConnector":
        """Switch active database."""
        if alias not in self.database_instances:
            raise DatabaseError(f"Database {alias} not attached")
        if not self.database_instances[alias]["is_active"]:
            raise ConnectionError(f"Database {alias} not connected")

        self.active_database = alias
        return self

    @contextmanager
    def cursor(self, alias: Optional[str] = None):
        """Get cursor for specified or active database."""
        target = alias or self.active_database
        if not target:
            raise DatabaseError("No active database")

        if target not in self.database_connections:
            raise ConnectionError(f"Database {target} not connected")

        cursor = self.database_connections[target].cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    @ensure_connected
    def execute_query(self, query: str, alias: Optional[str] = None) -> pd.DataFrame:
        """Execute query on specified or active database."""
        target = alias or self.active_database
        return pd.read_sql(query, self.database_connections[target])

    def copy_table(
        self,
        source_alias: str,
        target_alias: str,
        table_name: str,
        batch_size: int = 1000,
    ) -> None:
        """Copy table between databases."""
        if not all(alias in self.database_instances for alias in [source_alias, target_alias]):
            raise DatabaseError("Source or target database not attached")

        try:
            # Get schema
            schema_query = f"SELECT * FROM {table_name} WHERE 1=0"
            schema_df = self.execute_query(schema_query, source_alias)
            columns = schema_df.columns.tolist()

            # Create target table
            create_columns = [f"{col} TEXT" for col in columns]  # Simplified schema
            create_query = f"CREATE TABLE {table_name} ({', '.join(create_columns)})"
            with self.transaction(target_alias):
                with self.cursor(target_alias) as cursor:
                    cursor.execute(create_query)

            # Copy data in batches
            offset = 0
            while True:
                # Get batch of data
                select_query = f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
                batch_df = self.execute_query(select_query, source_alias)
                if batch_df.empty:
                    break

                # Insert batch
                placeholders = ",".join(["?"] * len(columns))
                insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"

                with self.transaction(target_alias):
                    with self.cursor(target_alias) as cursor:
                        cursor.executemany(insert_query, batch_df.values.tolist())

                offset += batch_size

        except Exception as e:
            raise DatabaseError(f"Failed to copy table: {e}")

    @contextmanager
    def transaction(self, alias: Optional[str] = None):
        """Transaction context for specified or active database."""
        target = alias or self.active_database
        if not target:
            raise DatabaseError("No active database")

        if target not in self.database_connections:
            raise ConnectionError(f"Database {target} not connected")

        if self._active_transaction and self._active_transaction != target:
            raise DatabaseError(f"Transaction already active on {self._active_transaction}")

        connection = self.database_connections[target]
        try:
            self._active_transaction = target
            yield
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            self._active_transaction = None

    def close(self, alias: Optional[str] = None) -> None:
        """Close connection to specified or all databases."""
        if alias:
            if alias in self.database_connections:
                self.database_connections[alias].close()
                self.database_connections.pop(alias)
                self.database_instances[alias]["is_active"] = False
                self.database_instances[alias]["detached_at"] = datetime.now()
                if self.active_database == alias:
                    self.active_database = next(iter(self.database_connections), None)
        else:
            for db_alias in list(self.database_connections.keys()):
                self.close(db_alias)

    def __enter__(self) -> "MultiDatabaseConnector":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


def main():
    """Simple demonstration of MultiDatabaseConnector."""
    try:
        # Create connector
        multi_db = MultiDatabaseConnector()

        # Attach SQLite databases
        with (
            multi_db.attach_database(
                "db1",
                TargetDatabaseEngine.SQLITE3,
                TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
            )
            .prepare_connection("db1", database=":memory:")
            .connect("db1") as connector
        ):

            # Create test table
            with connector.cursor() as cursor:
                cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
                cursor.execute("INSERT INTO test (value) VALUES (?)", ("test value",))

            # Query data
            results = connector.execute_query("SELECT * FROM test")
            print(f"Test query results:\n{results}")

    except DatabaseError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
