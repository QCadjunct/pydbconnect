"""Multi-Database Connector Implementation."""

from typing import Dict, Any, Optional, Tuple
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
)
import templates.engines as templates


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
        self.instances: Dict[str, Dict[str, Any]] = {}
        self.active_alias: Optional[str] = None

    def _load_engine_config(self, engine_name: str) -> Dict[str, Any]:
        """Load engine-specific configuration."""
        try:
            return getattr(templates, engine_name)
        except AttributeError as e:
            raise DatabaseError(f"Unsupported database engine: {engine_name}") from e

    def _validate_dsn_support(
        self, engine_type: TargetDatabaseEngine, connect_option: TargetDatabaseConnectionStringOption
    ) -> None:
        """Validate DSN support for engine."""
        if not engine_type.supports_dsn and connect_option.uses_dsn:
            raise ConnectionError(f"DSN not supported by {engine_type.name}")

    def _load_environment(self, alias: str) -> None:
        """Load environment variables for database instance."""
        env_path = Path.cwd() / ".env"
        instance = self.instances[alias]
        engine_name = instance["engine_type"].name

        if env_path.exists():
            load_dotenv(env_path)
            if engine_name:
                instance["credentials"].update(
                    {
                        "username": os.getenv(f"{engine_name}_USERNAME", ""),
                        "password": os.getenv(f"{engine_name}_PASSWORD", ""),
                        "is_default": True,
                    }
                )

    def attach_database(
        self,
        alias: str,
        engine_type: TargetDatabaseEngine,
        connect_option: TargetDatabaseConnectionStringOption,
    ) -> "MultiDatabaseConnector":
        """Attach a new database instance."""
        try:
            self._validate_dsn_support(engine_type, connect_option)

            # Initialize instance configuration
            self.instances[alias] = {
                "engine_type": engine_type,
                "engine_name": engine_type.name,
                "connect_option": connect_option,
                "connection": None,
                "module": None,
                "credentials": {"username": None, "password": None, "is_default": True},
                "connection_string": None,
                "engine_config": self._load_engine_config(engine_type.name),
                "is_active": False,
                "attached_at": datetime.now(),
                "detached_at": None,
            }

            # Load environment variables
            self._load_environment(alias)

            # Set as active if first database
            if not self.active_alias:
                self.active_alias = alias

            return self
        except Exception as e:
            raise DatabaseError(f"Failed to attach database {alias}: {str(e)}")

    def set_credentials(self, alias: str) -> "MultiDatabaseConnector":
        """Set database credentials based on connection option."""
        if alias not in self.instances:
            raise DatabaseError(f"Database {alias} not attached")

        instance = self.instances[alias]
        credential_change = instance["connect_option"].allow_credential_changes

        if credential_change == 1:  # do_not_change_username_password
            return self

        credential_mode = instance["connect_option"].changes_credentials
        if credential_mode.changes_default_credentials:
            show_password = credential_mode == ChangeDefaultUsernameAndPassword.ChangeUserAndPwdPlusShow
            username = input(f"Enter username for {alias}: ")
            password = (
                input(f"Enter password for {alias}: ") if show_password else getpass(f"Enter password for {alias}: ")
            )

            instance["credentials"].update({"username": username, "password": password, "is_default": False})

        return self

    def _get_default_parameters(self, alias: str) -> Dict[str, Any]:
        """Get dynamic default parameters from engine config."""
        instance = self.instances[alias]
        config = instance["engine_config"][instance["engine_name"]]
        format_config = config["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]

        if instance["connect_option"].uses_dsn:
            param_keys = format_config["LOAD_DSN_PARAMETER_KEYS"]
        else:
            param_keys = format_config["LOAD_DEFAULT_PARAMETER_KEYS"]

        return {key: config["DEFAULT_PARAMETERS"].get(key) for key in param_keys}

    def _build_connection_string(self, alias: str, params: Dict[str, Any]) -> str:
        """Build connection string using provided parameters."""
        try:
            instance = self.instances[alias]
            engine_template = instance["engine_config"]

            if instance["connect_option"].uses_dsn:
                connection_string = engine_template[instance["engine_name"]]["FINALIZED_CONNECTION_PARAMS"][
                    "LAMBDA_FINALIZED_DSN_CONNECTION_STRING"
                ](engine_template)
            else:
                engine_template[instance["engine_name"]]["DEFAULT_PARAMETERS"].update(params)
                connection_string = engine_template[instance["engine_name"]]["FINALIZED_CONNECTION_PARAMS"][
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
    def finalize_connection_parameters(self, alias: str, **params) -> "MultiDatabaseConnector":
        """Finalize connection parameters for specified database."""
        try:
            instance = self.instances[alias]
            engine_config = instance["engine_config"][instance["engine_name"]]
            format_config = engine_config["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]

            if instance["connect_option"].uses_dsn:
                load_method = format_config["METHOD_LOAD_DSN_PARAMETER_KEYS_DICT"]
            else:
                load_method = format_config["METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT"]

            default_params = load_method(instance["engine_name"], instance["engine_config"])
            default_params.update(params)

            if engine_config["CREATE_DATABASE_CONNECTION"]["REQUIRES_CREDENTIALS"]:
                if not all([instance["credentials"]["username"], instance["credentials"]["password"]]):
                    raise CredentialsError("Username and password required but not provided")

                default_params.update(
                    {
                        "USERNAME": instance["credentials"]["username"],
                        "PASSWORD": instance["credentials"]["password"],
                    }
                )

            instance["connection_string"] = self._build_connection_string(alias, default_params)
            return self

        except Exception as e:
            raise DatabaseError(f"Failed to finalize connection parameters for {alias}: {str(e)}")

    def connect(self, alias: str) -> "MultiDatabaseConnector":
        """Connect to specified database."""
        if alias not in self.instances:
            raise DatabaseError(f"Database {alias} not attached")

        instance = self.instances[alias]
        if not instance["connection_string"]:
            raise ConnectionError(f"Connection string not prepared for {alias}")

        try:
            if not instance["module"]:
                module_name = instance["engine_config"][instance["engine_name"]]["CRUDBASIC"]["IMPORT"]
                instance["module"] = importlib.import_module(module_name)

            connection_lambda = instance["engine_config"][instance["engine_name"]]["CREATE_DATABASE_CONNECTION"][
                "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"
            ](instance["connection_string"])

            instance["connection"] = connection_lambda()
            instance["is_active"] = True
            instance["attached_at"] = datetime.now()
            instance["detached_at"] = None

            return self

        except Exception as e:
            instance["connection"] = None
            instance["module"] = None
            instance["is_active"] = False
            raise ConnectionError(f"Failed to connect to {alias}: {str(e)}")

    def switch_database(self, alias: str) -> "MultiDatabaseConnector":
        """Switch active database."""
        if alias not in self.instances:
            raise DatabaseError(f"Database {alias} not attached")
        if not self.instances[alias]["is_active"]:
            raise ConnectionError(f"Database {alias} not connected")

        self.active_alias = alias
        return self

    @contextmanager
    def _cursor(self, alias: Optional[str] = None):
        """Context manager for database cursor."""
        target = alias or self.active_alias
        if not target:
            raise DatabaseError("No active database")

        instance = self.instances[target]
        if not instance["connection"] or not instance["is_active"]:
            raise ConnectionError(f"No active connection for database {target}")

        cursor = instance["connection"].cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    @ensure_connected
    def execute_query_to_dataframe(
        self, query: str, alias: Optional[str] = None, index_col: Optional[str] = None
    ) -> pd.DataFrame:
        """Execute query and return results as DataFrame."""
        target = alias or self.active_alias
        instance = self.instances[target]

        if not instance["connection"] or not instance["is_active"]:
            raise ConnectionError(f"Database connection not active for {target}")

        try:
            with self._cursor(target) as cursor:
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
        self, query: str, alias: Optional[str] = None, print_result: bool = False
    ) -> Optional[PrettyTable]:
        """Execute query and return/print results as PrettyTable."""
        target = alias or self.active_alias
        instance = self.instances[target]

        if not instance["connection"] or not instance["is_active"]:
            raise ConnectionError(f"Database connection not active for {target}")

        with self._cursor(target) as cursor:
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
    def execute_statement(self, sql: str, alias: Optional[str] = None) -> None:
        """Execute a general SQL statement (DML or DDL)."""
        target = alias or self.active_alias
        instance = self.instances[target]

        if not instance["connection"] or not instance["is_active"]:
            raise ConnectionError(f"Database connection not active for {target}")

        try:
            with self._cursor(target) as cursor:
                cursor.execute(sql)
                if not getattr(instance["connection"], "closed", False):
                    instance["connection"].commit()
        except Exception as e:
            if not getattr(instance["connection"], "closed", False):
                instance["connection"].rollback()
            raise DatabaseError(f"Statement execution failed: {e}")

    @ensure_connected
    def execute(
        self, sql: str, params: Optional[Tuple[Any, ...]] = None, alias: Optional[str] = None
    ) -> "MultiDatabaseConnector":
        """Execute a general SQL statement with parameters."""
        target = alias or self.active_alias
        instance = self.instances[target]

        if not instance["connection"] or not instance["is_active"]:
            raise ConnectionError(f"Database connection not active for {target}")

        try:
            with self._cursor(target) as cursor:
                if params is not None:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)

                if not getattr(instance["connection"], "closed", False):
                    instance["connection"].commit()

            return self

        except Exception as e:
            if not getattr(instance["connection"], "closed", False):
                instance["connection"].rollback()
            raise DatabaseError(f"Statement execution failed: {e}")

    def close(self, alias: Optional[str] = None) -> None:
        """Close connection to specified or all databases."""
        if alias:
            if alias in self.instances:
                instance = self.instances[alias]
                if instance["connection"]:
                    try:
                        if not getattr(instance["connection"], "closed", False):
                            instance["connection"].close()
                    except Exception:
                        pass
                    finally:
                        instance["connection"] = None
                        instance["module"] = None
                        instance["is_active"] = False
                        instance["detached_at"] = datetime.now()
                        if self.active_alias == alias:
                            self.active_alias = next((k for k, v in self.instances.items() if v["is_active"]), None)
        else:
            for db_alias in list(self.instances.keys()):
                self.close(db_alias)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
