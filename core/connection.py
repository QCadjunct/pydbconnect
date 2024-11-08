
from typing import Optional, Union, Dict, Any, List, Callable
from contextlib import contextmanager
import pandas as pd
from .template_manager import TemplateManager
from ..types.exceptions import (
    DatabaseError,
    DatabaseConnectionError, 
    DatabaseOperationError,
    ValidationError
)

class DatabaseConnection:
    """
    Main database connection class providing fluent interface for database operations.
    Manages database connections and operations with support for different database engines.
    """
    
    def __init__(self, engine_type: str, use_dsn: bool = False):
        """Initialize database connection configuration."""
        self.template_manager = TemplateManager(engine_type)
        self.use_dsn = use_dsn
        self._connection = None
        self._params = self.template_manager.get_default_params()
        self._credentials = {"username": None, "password": None}
        self._transaction_level = 0
        self._panda_dataframe: Optional[pd.DataFrame] = None
        self._dataframe_history: List[pd.DataFrame] = []
        self._last_query: Optional[str] = None

    def with_credentials(self, username: str, password: str) -> 'DatabaseConnection':
        """Set database credentials."""
        if self.template_manager.requires_authentication():
            if not username or not password:
                raise ValidationError("Username and password are required")
            self._credentials["username"] = username
            self._credentials["password"] = password
        return self

    def with_credentials_from_env(self) -> 'DatabaseConnection':
        """Load credentials from environment variables."""
        self._credentials = self.template_manager.get_credentials_from_env()
        return self

    def with_params(self, **params: Any) -> 'DatabaseConnection':
        """Set connection parameters."""
        self._validate_params(params)
        self._params.update(params)
        return self

    def _validate_params(self, params: Dict[str, Any]) -> None:
        """Validate connection parameters."""
        required_params = self.template_manager.get_required_params()
        missing = [p for p in required_params if p not in params and p not in self._params]
        if missing:
            raise ValidationError(f"Missing required parameters: {missing}")

    def connect(self) -> 'DatabaseConnection':
        """Establish database connection."""
        try:
            if self.template_manager.requires_authentication():
                self._params.update({
                    "USERNAME": self._credentials["username"],
                    "PASSWORD": self._credentials["password"]
                })

            conn_string = self.template_manager.get_connection_string(
                self._params,
                self.use_dsn
            )
            self._connection = self.template_manager.create_connection(conn_string)
            return self
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to connect: {str(e)}")

    def execute(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute a database query."""
        if not self._connection:
            raise DatabaseConnectionError("No active connection")
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params or ())
            return cursor
        except Exception as e:
            raise DatabaseOperationError(f"Query execution failed: {str(e)}")

    def execute_sql_to_panda_dataframe(
        self,
        sql_command: str,
        index_column: Optional[str] = None,
        return_dataframe: bool = True,
        store_history: bool = False,
        **kwargs: Any
    ) -> Union['DatabaseConnection', pd.DataFrame]:
        """Execute SQL and return results as DataFrame."""
        if not self._connection:
            raise DatabaseConnectionError("No active connection")

        try:
            self._last_query = sql_command
            self._panda_dataframe = pd.read_sql(
                sql_command,
                self._connection,
                index_col=index_column,
                **kwargs
            )

            if store_history:
                self._dataframe_history.append(self._panda_dataframe.copy())

            return self._panda_dataframe if return_dataframe else self
        except Exception as e:
            raise DatabaseOperationError(f"DataFrame creation failed: {str(e)}")

    def transform_dataframe(
        self,
        transformation: Union[Callable[[pd.DataFrame], pd.DataFrame], str],
        columns: Optional[List[str]] = None,
        **kwargs: Any
    ) -> 'DatabaseConnection':
        """Apply transformation to the current DataFrame."""
        if self._panda_dataframe is None:
            raise DatabaseOperationError("No DataFrame available")

        try:
            if callable(transformation):
                self._panda_dataframe = transformation(self._panda_dataframe)
            else:
                transform_map = {
                    'fillna': lambda df: df.fillna(kwargs.get('value', 0)),
                    'dropna': lambda df: df.dropna(**kwargs),
                    'standardize': lambda df: (
                        df[columns] if columns else df
                    ).pipe(lambda x: (x - x.mean()) / x.std())
                }
                if transformation not in transform_map:
                    raise ValueError(f"Unknown transformation: {transformation}")
                self._panda_dataframe = transform_map[transformation](self._panda_dataframe)
            return self
        except Exception as e:
            raise DatabaseOperationError(f"Transformation failed: {str(e)}")

    @contextmanager
    def transaction(self):
        """Transaction context manager."""
        try:
            self.begin_transaction()
            yield self
            self.commit()
        except Exception as e:
            self.rollback()
            raise DatabaseError(f"Transaction failed: {str(e)}")

    def begin_transaction(self) -> 'DatabaseConnection':
        """Start a new transaction."""
        if self._transaction_level == 0:
            self.execute("BEGIN TRANSACTION")
        self._transaction_level += 1
        return self

    def commit(self) -> 'DatabaseConnection':
        """Commit the current transaction."""
        if self._transaction_level > 0:
            self._transaction_level -= 1
            if self._transaction_level == 0:
                self.execute("COMMIT")
        return self

    def rollback(self) -> 'DatabaseConnection':
        """Rollback the current transaction."""
        if self._transaction_level > 0:
            self.execute("ROLLBACK")
            self._transaction_level = 0
        return self

    def bulk_insert(
        self,
        table: str,
        df: pd.DataFrame,
        batch_size: int = 1000
    ) -> 'DatabaseConnection':
        """Perform bulk insert operation."""
        if len(df) == 0:
            return self

        placeholder = self.template_manager.get_parameter_placeholder()
        columns = df.columns.tolist()
        value_placeholders = f"({','.join([placeholder] * len(columns))})"
        query = f"INSERT INTO {table} ({','.join(columns)}) VALUES {value_placeholders}"

        try:
            with self.transaction():
                for i in range(0, len(df), batch_size):
                    batch = df.iloc[i:i + batch_size]
                    self.execute_many(query, batch.values.tolist())
            return self
        except Exception as e:
            raise DatabaseOperationError(f"Bulk insert failed: {str(e)}")

    def execute_many(self, query: str, params_list: List[tuple]) -> 'DatabaseConnection':
        """Execute multiple queries with parameters."""
        if not self._connection:
            raise DatabaseConnectionError("No active connection")
        try:
            cursor = self._connection.cursor()
            cursor.executemany(query, params_list)
            return self
        except Exception as e:
            raise DatabaseOperationError(f"Execute many failed: {str(e)}")

    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._connection is not None

    @property
    def in_transaction(self) -> bool:
        """Check if currently in a transaction."""
        return self._transaction_level > 0

    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
