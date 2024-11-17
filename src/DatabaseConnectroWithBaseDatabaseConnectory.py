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
from .db_templates.database_target_engine_template_modules import MSSQL,MYSQL,POSTGRESQL,PSYCOPG2,SQLITE3,DUCKDB as template
from .db_templates.database_target_engine_modules_enum_contraints import TargetDatabaseEngine, TargetDatabaseConnectionStringOption

class DatabaseConnector(BaseDatabaseConnector):
    """
    A fluent interface for database connections supporting multiple engines.
    Uses method chaining for configuration and execution.
    """
    
    def __init__(self, engine_type: TargetDatabaseEngine, 
                 connect_option: TargetDatabaseConnectionStringOption):
        """Initialize database connection with specified engine and options."""
        super().__init__()
        self.target_database_engine_name = engine_type.name
        self.connect_option = connect_option
        self.engine_config = self._load_engine_config()

    def _load_engine_config(self) -> Dict[str, Any]:
        """Load engine-specific configuration."""
        try:
             return getattr(template, self.target_database_engine_name)
        except AttributeError as e:
            raise DatabaseError(f"Unsupported database engine: {self.target_database_engine_name}") from e

    def connect_to_database(self) -> 'DatabaseConnector':
        """Establish database connection."""
        try:
            module_name = self.engine_config['MODULE']
            module = importlib.import_module(module_name)
            self._connection = module.connect(self._connection_string)
            return self
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}")

    # ---- Query Method Overrides ----
    def execute_sql_to_dataframe(self, sql: str, index_col: Optional[str] = None) -> pd.DataFrame:
        """Execute SQL and return results as DataFrame."""
        return super().execute_sql_to_dataframe(sql, index_col)

    def execute_sql_to_prettytable(self, sql: str, is_print: bool = False) -> Optional[PrettyTable]:
        """Execute SQL and return/print results as PrettyTable."""
        return super().execute_sql_to_prettytable(sql, is_print)

    # ---- CRUD Operation Overrides ----
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert single record and return inserted id."""
        return super().insert(table, data)

    def bulk_insert(self, table: str, records: List[Dict[str, Any]]) -> None:
        """Insert multiple records."""
        super().bulk_insert(table, records)

    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """Update records matching criteria."""
        return super().update(table, data, where)

    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """Delete records matching criteria."""
        return super().delete(table, where)

    def select(self, table: str, columns: Optional[List[str]] = None, 
               where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Select records with optional column and where clause filters."""
        return super().select(table, columns, where)

    # ---- Transaction Management Overrides ----
    @contextmanager
    def transaction(self):
        """Context manager for transaction handling."""
        with super().transaction():
            yield

    def begin_transaction(self) -> None:
        """Start a new transaction."""
        super().begin_transaction()

    def commit(self) -> None:
        """Commit current transaction."""
        super().commit()

    def rollback(self) -> None:
        """Rollback current transaction."""
        super().rollback()

    def savepoint(self, name: str) -> None:
        """Create a savepoint in current transaction."""
        super().savepoint(name)

    def rollback_to(self, name: str) -> None:
        """Rollback to specified savepoint."""
        super().rollback_to(name)

    # ---- Stored Procedure Override ----
    def execute_procedure(self, name: str, params: Optional[List[Any]] = None) -> Optional[List[Any]]:
        """Execute stored procedure with optional parameters."""
        return super().execute_procedure(name, params)

    # ---- Backup and Restore Overrides ----
    def backup_database(self, path: str) -> None:
        """Backup database to specified path."""
        super().backup_database(path)

    def restore_database(self, path: str) -> None:
        """Restore database from specified path."""
        super().restore_database(path)

    # ---- Custom Method Implementations ----
    def change_default_username_and_password(self, show_password: bool = False) -> 'DatabaseConnector':
        """Change database credentials."""
        super().change_default_username_and_password(show_password)
        return self

    def finalization_of_connection_parameters(self, **params) -> 'DatabaseConnector':
        """Finalize connection parameters with custom values."""
        super().finalization_of_connection_parameters(**params)
        return self

    # ---- Context Manager Overrides ----
    def __enter__(self) -> 'DatabaseConnector':
        """Context manager entry."""
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit with connection cleanup."""
        super().__exit__(exc_type, exc_val, exc_tb)

    def close(self) -> None:
        """Explicitly close the database connection."""
        super().close()

# Usage Example
def main():
    # Create connection options
    connection_options = TargetDatabaseConnectionStringOption(
        server="localhost",
        database="test_db",
        username="user",
        password="pass",
        port=1433
    )

    # Initialize database connector
    with DatabaseConnector(TargetDatabaseEngine.MSSQL, TargetDatabaseConnectionStringOption.Customize_DSN_AndChangeUserPwd) as db:
        try:
            # Configure and establish connection
            db.finalization_of_connection_parameters(
                timeout=30,
                encrypt=True
            ).connect_to_database()

            # Perform database operations
            with db.transaction():
                # Insert data
                db.insert("users", {
                    "name": "John Doe",
                    "email": "john@example.com"
                })

                # Query data
                results_df = db.execute_sql_to_dataframe(
                    "SELECT * FROM users WHERE name LIKE ?",
                    index_col="id"
                )
                print("Results as DataFrame:")
                print(results_df)

                # Pretty table output
                db.execute_sql_to_prettytable(
                    "SELECT * FROM users ORDER BY name",
                    is_print=True
                )

        except DatabaseError as e:
            print(f"Database operation failed: {e}")
            raise

if __name__ == "__main__":
    main()