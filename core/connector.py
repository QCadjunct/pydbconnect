"""Database Connector Implementation."""

from typing import Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from contextlib import contextmanager
import importlib
import pandas as pd
from datetime import datetime
from pathlib import Path
from getpass import getpass
from dotenv import load_dotenv
from prettytable import PrettyTable
import os
from utils.decorators import preload_parameters, ensure_connected
from templates.constraints import (
    ChangeDefaultUsernameAndPassword,
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
    FileFormat,
)
import templates.engines as templates

from .transaction_manager import TransactionManager  # Add this import


@dataclass
class FormatOptions:
    """Configuration options for file format handling."""

    compression: Optional[str] = None
    encoding: Optional[str] = None
    date_format: Optional[str] = None
    float_format: Optional[str] = None
    batch_size: Optional[int] = None
    chunk_size: Optional[int] = None

    # Format-specific options
    excel_options: Optional[Dict[str, Any]] = None
    json_options: Optional[Dict[str, Any]] = None
    csv_options: Optional[Dict[str, Any]] = None
    parquet_options: Optional[Dict[str, Any]] = None

    def get_format_options(self, file_format: FileFormat) -> Dict[str, Any]:
        """Get options specific to a file format.

        Args:
            file_format: The FileFormat enum member

        Returns:
            Dictionary of format-specific options
        """
        base_options = {
            "compression": self.compression,
            "encoding": self.encoding,
        }

        format_specific = {
            FileFormat.CSV: self.csv_options or {},
            FileFormat.EXCEL: self.excel_options or {},
            FileFormat.JSON: self.json_options or {},
            FileFormat.PARQUET: self.parquet_options or {},
        }

        options = base_options.copy()
        options.update(format_specific.get(file_format, {}))

        # Remove None values
        return {k: v for k, v in options.items() if v is not None}


# Exception definitions must come first
#
# The fundamental approach of having exceptions defined before imports
# remains the same in both versions. Therefore, we should keep
# the original format as it's working and
# maintains your established code style.


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
        # Engine configuration
        self.target_database_engine_type = target_database_engine
        self.target_database_engine_name = target_database_engine.name
        self.target_database_engine_connect_option = target_database_engine_connect_option

        # Connection state
        self._connection = None
        self._module = None
        self._credentials = {"username": None, "password": None, "is_default": True}
        self._connection_string = None

        # Load configuration
        self.engine_config = self._load_engine_config(templates)
        self.change_database_usr_and_pwd_option = target_database_engine_connect_option.allow_credential_changes

        # Validate DSN support
        self._validate_dsn_support()

        # Load environment
        self._load_environment()

        # Add transaction manager
        self.transaction_manager = TransactionManager(self)

    def _load_engine_config(self, templates) -> Dict[str, Any]:
        """Load engine-specific configuration."""
        try:
            return getattr(templates, self.target_database_engine_name)
        except AttributeError as e:
            raise DatabaseError(f"Unsupported database engine: {self.target_database_engine_name}") from e

    def _load_environment(self) -> None:
        """Load environment variables from .env file."""
        env_path = Path.cwd() / ".env"

        if env_path.exists():
            load_dotenv(env_path)
            if self.target_database_engine_name:
                self._credentials.update(
                    {
                        "username": os.getenv(f"{self.target_database_engine_name}_USERNAME", ""),
                        "password": os.getenv(f"{self.target_database_engine_name}_PASSWORD", ""),
                        "is_default": True,
                    }
                )
        else:
            print(f"No .env file found at {env_path}")

    def _validate_dsn_support(self) -> None:
        """Validate DSN support for engine."""
        if not self.target_database_engine_type.supports_dsn and self.target_database_engine_connect_option.uses_dsn:
            raise ConnectionError(f"DSN not supported by {self.target_database_engine_name}")

    def set_credentials_based_on_connect_option(self) -> "DatabaseConnector":
        """Set database credentials based on connection option."""
        credential_change = self.target_database_engine_connect_option.allow_credential_changes

        if credential_change == 1:  # do_not_change_username_passord
            return self

        credential_mode = self.target_database_engine_connect_option.changes_credentials
        if credential_mode.changes_default_credentials:
            show_password = credential_mode == ChangeDefaultUsernameAndPassword.ChangeUserAndPwdPlusShow
            username = input("Enter database username: ")
            password = input("Enter database password: ") if show_password else getpass("Enter database password: ")

            self._credentials.update({"username": username, "password": password, "is_default": False})
        return self

    def _get_default_parameters(self) -> Dict[str, Any]:
        """Get dynamic default parameters from engine config."""
        config = self.engine_config[self.target_database_engine_name]
        format_config = config["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]

        if self.target_database_engine_connect_option.uses_dsn:
            param_keys = format_config["LOAD_DSN_PARAMETER_KEYS"]
        else:
            param_keys = format_config["LOAD_DEFAULT_PARAMETER_KEYS"]

        return {key: config["DEFAULT_PARAMETERS"].get(key) for key in param_keys}

    def _build_connection_string(self, params: Dict[str, Any]) -> str:
        """Build connection string using provided parameters."""
        try:
            engine_template = getattr(templates, self.target_database_engine_name)

            if self.target_database_engine_connect_option.uses_dsn:
                connection_string = engine_template[self.target_database_engine_name]["FINALIZED_CONNECTION_PARAMS"][
                    "LAMBDA_FINALIZED_DSN_CONNECTION_STRING"
                ](engine_template)
            else:
                engine_template[self.target_database_engine_name]["DEFAULT_PARAMETERS"].update(params)
                connection_string = engine_template[self.target_database_engine_name]["FINALIZED_CONNECTION_PARAMS"][
                    "LAMBDA_FINALIZED_BASE_CONNECTION_STRING"
                ](engine_template)

            if connection_string is None:
                raise DatabaseError("Connection string generation not supported")

            return connection_string

        except KeyError as e:
            raise DatabaseError(f"Missing required parameter: {e}")
        except Exception as e:
            raise DatabaseError(f"Connection string error: {str(e)}")

    @preload_parameters(_get_default_parameters)
    def finalization_of_connection_parameters(self, **params) -> "DatabaseConnector":
        """Finalize connection parameters using engine's parameter loading methods."""
        try:
            engine_config = self.engine_config[self.target_database_engine_name]
            format_config = engine_config["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]

            if self.target_database_engine_connect_option.uses_dsn:
                load_method = format_config["METHOD_LOAD_DSN_PARAMETER_KEYS_DICT"]
            else:
                load_method = format_config["METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT"]

            default_params = load_method(self.target_database_engine_name, self.engine_config)
            default_params.update(params)

            if engine_config["CREATE_DATABASE_CONNECTION"]["REQUIRES_CREDENTIALS"]:
                if not all([self._credentials["username"], self._credentials["password"]]):
                    raise CredentialsError("Username and password required but not provided")

                default_params.update(
                    {
                        "USERNAME": self._credentials["username"],
                        "PASSWORD": self._credentials["password"],
                    }
                )

            self._connection_string = self._build_connection_string(default_params)
            return self

        except KeyError as e:
            raise DatabaseError(f"Missing configuration key: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Failed to finalize connection parameters: {str(e)}")

    def connect_to_database(self) -> "DatabaseConnector":
        """Establish database connection."""
        if not self._connection_string:
            raise ConnectionError("Connection string not prepared")

        try:
            if not self._module:
                module_name = self.engine_config[self.target_database_engine_name]["CRUDBASIC"]["IMPORT"]
                self._module = importlib.import_module(module_name)

            connection_lambda = self.engine_config[self.target_database_engine_name]["CREATE_DATABASE_CONNECTION"][
                "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"
            ](self._connection_string)

            self._connection = connection_lambda()
            self.is_database_active = True
            self.database_attached_at = datetime.now()
            self.database_detached_at = None

            return self

        except Exception as e:
            self._connection = None
            self._module = None
            self.is_database_active = False
            raise ConnectionError(f"Failed to connect: {str(e)}")

    @contextmanager
    def _cursor(self):
        """Context manager for database cursor."""
        if not self._connection or not self.is_database_active:
            raise ConnectionError("No active database connection")

        cursor = self._connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    # @ensure_connected
    # def execute_query_to_dataframe(self, query: str, index_col: Optional[str] = None) -> "DatabaseConnector":
    #     """Execute query and return connector for chaining."""
    #     if not self._connection or not self.is_database_active:
    #         raise ConnectionError("Database connection not active")

    #     try:
    #         with self._cursor() as cursor:
    #             cursor.execute(query)
    #             columns = [col[0] for col in cursor.description]
    #             data = [list(row) for row in cursor.fetchall()]

    #             df = pd.DataFrame(data, columns=columns) if data else pd.DataFrame()
    #             if index_col and index_col in df.columns:
    #                 df.set_index(index_col, inplace=True)

    #             self._current_df = df
    #             return self

    #     except Exception as e:
    #         raise DatabaseError(f"Query execution failed: {e}")

    @ensure_connected
    def execute_query_to_dataframe(
        self, query: str, params: Optional[Tuple] = None, index_col: Optional[str] = None
    ) -> "DatabaseConnector":
        """Execute query and return connector for chaining."""
        if not self._connection or not self.is_database_active:
            raise ConnectionError("Database connection not active")

        try:
            with self._cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                data = [list(row) for row in cursor.fetchall()]

                df = pd.DataFrame(data, columns=columns) if data else pd.DataFrame()
                if index_col and index_col in df.columns:
                    df.set_index(index_col, inplace=True)

                self._current_df = df
                return self

        except Exception as e:
            raise DatabaseError(f"Query execution failed: {e}")

    # Add to connector.py

    def _check_format_dependencies(self, file_format: FileFormat) -> bool:
        """Check if required dependencies are installed for the file format."""
        try:
            if file_format == FileFormat.XLSX or file_format == FileFormat.XLS:
                import openpyxl

                return True
            elif file_format == FileFormat.PARQUET:
                import pyarrow

                return True
            elif file_format == FileFormat.FEATHER:
                import pyarrow

                return True
            elif file_format == FileFormat.ORC:
                import pyarrow

                return True
            elif file_format == FileFormat.HDF:
                import tables

                return True
            else:
                # CSV, JSON are part of pandas core
                return True
        except ImportError:
            return False

    def save_to_file(
        self,
        path: Union[str, Path],
        file_format: Optional[FileFormat] = None,
        format_options: Optional[FormatOptions] = None,
        **kwargs,
    ) -> "DatabaseConnector":
        """Save current DataFrame using specified format with options.

        Args:
            path: Path to save file
            file_format: Optional FileFormat enum member
            format_options: Optional FormatOptions for additional configuration
            **kwargs: Additional keyword arguments for the writer

        Returns:
            Self for method chaining
        """
        if not hasattr(self, "_current_df"):
            return self

        path = Path(path)
        if file_format is None:
            extension = path.suffix.lstrip(".")
            file_format = FileFormat.from_extension(extension)
            if file_format is None:
                raise ValueError(f"Unsupported file extension: {extension}")

        # Check dependencies
        if not self._check_format_dependencies(file_format):
            format_to_package = {
                FileFormat.XLSX: "openpyxl",
                FileFormat.XLS: "openpyxl",
                FileFormat.PARQUET: "pyarrow",
                FileFormat.FEATHER: "pyarrow",
                FileFormat.ORC: "pyarrow",
                FileFormat.HDF: "tables",
            }
            package = format_to_package.get(file_format, "unknown")
            print(f"Warning: {file_format.name} format requires {package}. Skipping file: {path}")
            return self

        try:
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            # Merge format options with kwargs
            save_kwargs = kwargs.copy()
            if format_options:
                save_kwargs.update(format_options.get_format_options(file_format))

                # Handle batch processing if specified
                if format_options.batch_size and hasattr(self._current_df, "shape"):
                    total_rows = self._current_df.shape[0]
                    for i in range(0, total_rows, format_options.batch_size):
                        batch_df = self._current_df.iloc[i : i + format_options.batch_size]
                        batch_path = path.parent / f"{path.stem}_batch_{i//format_options.batch_size}{path.suffix}"
                        file_format.write_dataframe(batch_df, str(batch_path), **save_kwargs)
                        print(f"Saved batch: {batch_path}")
                    return self

            # Regular save without batching
            file_format.write_dataframe(self._current_df, str(path), **save_kwargs)
            print(f"Saved: {path}")

        except Exception as e:
            print(f"Warning: Failed to save {path}: {str(e)}")

        return self

    def to_dataframe(self) -> pd.DataFrame:
        """Get the current DataFrame and clear it from memory."""
        if not hasattr(self, "_current_df"):
            return pd.DataFrame()

        df = self._current_df
        del self._current_df
        return df

    def display_dataframe_info(self, df: pd.DataFrame, title: str = "") -> None:
        """Display detailed information about a DataFrame.

        Args:
            df: pandas DataFrame to analyze
            title: Optional title for the info display
        """
        if title:
            print(f"\n=== {title} ===")
        print("DataFrame Info:")
        df.info(memory_usage="deep")
        print("\nDataFrame Shape:", df.shape)
        print("\nDataFrame Preview:")
        print(df)

    @ensure_connected
    def execute_query_to_prettytable(
        self, query: str, sql_parameters: Optional[tuple] = None, print_result: bool = False
    ) -> Optional[PrettyTable]:
        """Execute query and return/print results as PrettyTable."""
        if not self._connection or not self.is_database_active:
            raise ConnectionError("Database connection not active")

        with self._cursor() as cursor:
            try:
                if sql_parameters:
                    cursor.execute(query, sql_parameters)
                else:
                    cursor.execute(query)
                table = PrettyTable()
                table.field_names = [col[0] for col in cursor.description]
                table.add_rows(cursor.fetchall())

                if print_result:
                    print(table)
                    return None
                return table
            except Exception as e:
                raise DatabaseError(f"Query execution failed: {e}")

    @ensure_connected
    def execute(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> "DatabaseConnector":
        """Execute a general SQL statement (DML or DDL).

        Args:
            sql: SQL statement to execute
            params: Optional parameters for the SQL statement

        Returns:
            Self for method chaining

        Raises:
            ConnectionError: If database connection is not active
            DatabaseError: If statement execution fails
        """
        if not self._connection or not self.is_database_active:
            raise ConnectionError("Database connection not active")

        try:
            with self._cursor() as cursor:
                if params is not None:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)

                if not getattr(self._connection, "closed", False):
                    self._connection.commit()

            return self

        except Exception as e:
            if not getattr(self._connection, "closed", False):
                self._connection.rollback()
            raise DatabaseError(f"Statement execution failed: {e}")

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            try:
                if not getattr(self._connection, "closed", False):
                    self._connection.close()
            except Exception:
                pass
            finally:
                self._connection = None
                self._module = None
                self.is_database_active = False
                self.database_detached_at = datetime.now()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":

    print("\nWarning: This is the core connector module.")
    print("For examples, please run files in core/examples/ instead.")
    print("\nDebug Info:")
    print(f"\nCurrent directory: {os.getcwd()}")
    print(f"\nCurrent file: {__file__}")
    print(f"\nEnvironment variables: {os.environ}")
