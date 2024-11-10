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
from .db_constants.enum_connection_constants import TargetDatabaseEngine, TargetDatabaseConnectionStringOption

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
        self.engine_config = self._load_engine_config()
        self._connection = None
        self._credentials = {'username': None, 'password': None, 'is_default': True}
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

    @contextmanager
    def _cursor(self):
        """Context manager for cursor handling."""
        if not self._connection:
            raise ConnectionError("No active database connection")
        cursor = self._connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

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
            default_params = self.engine_config['DEFAULT_PARAMETERS'].copy()
            default_params.update(params)
            
            if self.engine_config['REQUIRES_CREDENTIALS']:
                if not all([self._credentials['username'], self._credentials['password']]):
                    raise CredentialsError("Username and password required but not provided")
                default_params.update({
                    'USERNAME': self._credentials['username'],
                    'PASSWORD': self._credentials['password']
                })
            
            self._connection_string = self._build_connection_string(default_params)
            return self
        except KeyError as e:
            raise DatabaseError(f"Missing required parameter: {e}")

    def _build_connection_string(self, params: Dict[str, Any]) -> str:
        """Build connection string from parameters."""
        try:
            template = (self.engine_config['DSN_TEMPLATE'] 
                       if self.connect_option.uses_dsn 
                       else self.engine_config['CONNECTION_TEMPLATE'])
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

    # ---- Core Query Methods ----
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
        with self._cursor() as cursor:
            try:
                cursor.execute(sql)
                table = PrettyTable()
                table.field_names = [col[0] for col in cursor.description]
                table.add_rows(cursor.fetchall())
                
                if is_print:
                    print(table)
                    return None
                return table
            except Exception as e:
                raise DatabaseError(f"Query execution failed: {e}")

    # ---- Basic CRUD Operations ----
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert single record and return inserted id."""
        placeholder = self.engine_config.get('PLACEHOLDER', '?')
        columns = ','.join(data.keys())
        placeholders = ','.join([placeholder] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        with self._cursor() as cursor:
            cursor.execute(query, list(data.values()))
            self._connection.commit()
            return cursor.lastrowid

    def bulk_insert(self, table: str, records: List[Dict[str, Any]]) -> None:
        """Insert multiple records."""
        if not records:
            return

        placeholder = self.engine_config.get('PLACEHOLDER', '?')
        columns = ','.join(records[0].keys())
        placeholders = ','.join([placeholder] * len(records[0]))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        with self._cursor() as cursor:
            cursor.executemany(query, [list(record.values()) for record in records])
            self._connection.commit()

    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """Update records matching criteria."""
        placeholder = self.engine_config.get('PLACEHOLDER', '?')
        set_clause = ','.join(f"{k}={placeholder}" for k in data.keys())
        where_clause = ' AND '.join(f"{k}={placeholder}" for k in where.keys())
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

        with self._cursor() as cursor:
            cursor.execute(query, list(data.values()) + list(where.values()))
            self._connection.commit()
            return cursor.rowcount

    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """Delete records matching criteria."""
        placeholder = self.engine_config.get('PLACEHOLDER', '?')
        where_clause = ' AND '.join(f"{k}={placeholder}" for k in where.keys())
        query = f"DELETE FROM {table} WHERE {where_clause}"

        with self._cursor() as cursor:
            cursor.execute(query, list(where.values()))
            self._connection.commit()
            return cursor.rowcount

    def select(self, table: str, columns: Optional[List[str]] = None, 
               where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Select records with optional column and where clause filters."""
        placeholder = self.engine_config.get('PLACEHOLDER', '?')
        cols = ','.join(columns) if columns else '*'
        query = f"SELECT {cols} FROM {table}"
        params = []

        if where:
            where_clause = ' AND '.join(f"{k}={placeholder}" for k in where.keys())
            query += f" WHERE {where_clause}"
            params = list(where.values())

        with self._cursor() as cursor:
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    # ---- Transaction Management ----
    @contextmanager
    def transaction(self):
        """Context manager for transaction handling."""
        if hasattr(self._connection, 'autocommit'):
            previous_autocommit = self._connection.autocommit
            self._connection.autocommit = False

        try:
            yield
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            raise DatabaseError(f"Transaction failed: {e}")
        finally:
            if hasattr(self._connection, 'autocommit'):
                self._connection.autocommit = previous_autocommit

    def begin_transaction(self) -> None:
        """Start a new transaction."""
        if hasattr(self._connection, 'autocommit'):
            self._connection.autocommit = False

    def commit(self) -> None:
        """Commit current transaction."""
        self._connection.commit()

    def rollback(self) -> None:
        """Rollback current transaction."""
        self._connection.rollback()

    def savepoint(self, name: str) -> None:
        """Create a savepoint in current transaction."""
        with self._cursor() as cursor:
            cursor.execute(f"SAVEPOINT {name}")

    def rollback_to(self, name: str) -> None:
        """Rollback to specified savepoint."""
        with self._cursor() as cursor:
            cursor.execute(f"ROLLBACK TO SAVEPOINT {name}")

    # ---- Stored Procedures ----
    def execute_procedure(self, name: str, params: Optional[List[Any]] = None) -> Optional[List[Any]]:
        """Execute stored procedure with optional parameters."""
        with self._cursor() as cursor:
            if params:
                cursor.callproc(name, params)
            else:
                cursor.callproc(name)
            try:
                return cursor.fetchall()
            except:
                return None

    # ---- Backup and Restore ----
    def backup_database(self, path: str) -> None:
        """Backup database to specified path."""
        backup_command = self.engine_config.get('BACKUP_COMMAND', '').format(path=path)
        if not backup_command:
            raise DatabaseError(f"Backup not supported for {self.engine_type.value}")

        with self._cursor() as cursor:
            cursor.execute(backup_command)

    def restore_database(self, path: str) -> None:
        """Restore database from specified path."""
        restore_command = self.engine_config.get('RESTORE_COMMAND', '').format(path=path)
        if not restore_command:
            raise DatabaseError(f"Restore not supported for {self.engine_type.value}")

        with self._cursor() as cursor:
            cursor.execute(restore_command)

    # ---- Context Manager Support ----
    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with connection cleanup."""
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass

    def close(self):
        """Explicitly close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None