"""Database Connector Implementation."""

from typing import Dict, Any, Optional
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


from utils.decorators import preload_parameters, ensure_connected
from templates.constraints import (
    ChangeDefaultUsernameAndPassword,
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
)
import templates.engines as templates


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
        self.target_database_engine_connect_option = (
            target_database_engine_connect_option
        )

        # Connection state
        self._connection = None
        self._module = None
        self._credentials = {"username": None, "password": None, "is_default": True}
        self._connection_string = None

        # Load configuration
        self.engine_config = self._load_engine_config(templates)
        self.change_database_usr_and_pwd_option = (
            target_database_engine_connect_option.allow_credential_changes
        )

        # Validate DSN support
        self._validate_dsn_support()

        # Load environment
        self._load_environment()

        # Track state
        self.is_database_active = False
        self.database_attached_at = None
        self.database_detached_at = None

    def _load_engine_config(self, templates) -> Dict[str, Any]:
        """Load engine-specific configuration."""
        try:
            return getattr(templates, self.target_database_engine_name)
        except AttributeError as e:
            raise DatabaseError(
                f"Unsupported database engine: {self.target_database_engine_name}"
            ) from e

    def _load_environment(self) -> None:
        """Load environment variables from .env file."""
        env_path = Path.cwd() / ".env"

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
        else:
            print(f"No .env file found at {env_path}")

    def _validate_dsn_support(self) -> None:
        """Validate DSN support for engine."""
        if (
            not self.target_database_engine_type.supports_dsn
            and self.target_database_engine_connect_option.uses_dsn
        ):
            raise ConnectionError(
                f"DSN not supported by {self.target_database_engine_name}"
            )

    def set_credentials_based_on_connect_option(self) -> "DatabaseConnector":
        """Set database credentials based on connection option."""
        credential_change = (
            self.target_database_engine_connect_option.allow_credential_changes
        )

        if credential_change == 1:  # do_not_change_username_passord
            return self

        credential_mode = self.target_database_engine_connect_option.changes_credentials
        if credential_mode.changes_default_credentials:
            show_password = (
                credential_mode
                == ChangeDefaultUsernameAndPassword.ChangeUserAndPwdPlusShow
            )
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
                connection_string = engine_template[self.target_database_engine_name][
                    "FINALIZED_CONNECTION_PARAMS"
                ]["LAMBDA_FINALIZED_DSN_CONNECTION_STRING"](engine_template)
            else:
                engine_template[self.target_database_engine_name][
                    "DEFAULT_PARAMETERS"
                ].update(params)
                connection_string = engine_template[self.target_database_engine_name][
                    "FINALIZED_CONNECTION_PARAMS"
                ]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](engine_template)

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
            format_config = engine_config["DEFAULT_PARAMETERS"][
                "FORMAT_CONNECTION_STRING"
            ]

            if self.target_database_engine_connect_option.uses_dsn:
                load_method = format_config["METHOD_LOAD_DSN_PARAMETER_KEYS_DICT"]
            else:
                load_method = format_config["METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT"]

            default_params = load_method(
                self.target_database_engine_name, self.engine_config
            )
            default_params.update(params)

            if engine_config["CREATE_DATABASE_CONNECTION"]["REQUIRES_CREDENTIALS"]:
                if not all(
                    [self._credentials["username"], self._credentials["password"]]
                ):
                    raise CredentialsError(
                        "Username and password required but not provided"
                    )

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
                module_name = self.engine_config[self.target_database_engine_name][
                    "CRUDBASIC"
                ]["IMPORT"]
                self._module = importlib.import_module(module_name)

            connection_lambda = self.engine_config[self.target_database_engine_name][
                "CREATE_DATABASE_CONNECTION"
            ]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](self._connection_string)

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

    @ensure_connected
    def execute_query_to_dataframe(
        self, query: str, index_col: Optional[str] = None
    ) -> pd.DataFrame:
        """Execute query and return results as DataFrame."""
        if not self._connection or not self.is_database_active:
            raise ConnectionError("Database connection not active")

        try:
            with self._cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                data = cursor.fetchall()
                if data:
                    df = pd.DataFrame(data, columns=columns)
                    if index_col and index_col in df.columns:
                        df.set_index(index_col, inplace=True)
                    return df
                return pd.DataFrame()
        except Exception as e:
            raise DatabaseError(f"Query execution failed: {e}")

    @ensure_connected
    def execute_query_to_prettytable(
        self, query: str, print_result: bool = False
    ) -> Optional[PrettyTable]:
        """Execute query and return/print results as PrettyTable."""
        if not self._connection or not self.is_database_active:
            raise ConnectionError("Database connection not active")

        with self._cursor() as cursor:
            try:
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
    def execute_statement(self, sql: str) -> None:
        """Execute a general SQL statement (DML or DDL).

        Args:
            sql: SQL statement to execute
        """
        if not self._connection or not self.is_database_active:
            raise ConnectionError("Database connection not active")

        try:
            with self._cursor() as cursor:
                cursor.execute(sql)
                if not getattr(self._connection, "closed", False):
                    self._connection.commit()
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
    import os

    print("\nWarning: This is the core connector module.")
    print("For examples, please run files in core/examples/ instead.")
    print(f"\nDebug Info:")
    print(f"Current directory: {os.getcwd()}")
    print(f"Current file: {__file__}")
    print(f"Environment variables: {os.environ}")
