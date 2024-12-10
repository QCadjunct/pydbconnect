# Description: Database connector implementation.
"""Database Connector Implementation."""
from typing import Dict, Any, Optional, Type, Union
from types import TracebackType
from contextlib import contextmanager
import importlib
import pandas as pd
from datetime import datetime
from pathlib import Path
from getpass import getpass
from dotenv import load_dotenv
from prettytable import PrettyTable
import os
from templates.constraints import IsolationLevel

from core.exceptions import DatabaseError, ConnectionError

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.decorators import preload_parameters, ensure_connected

import templates.engines as templates
from templates.constraints import (
    ChangeDefaultUsernameAndPassword,
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
    IsolationLevel,
)


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
        self.target_database_engine_connect_option = (
            target_database_engine_connect_option
        )
        # Transactional methods
        self._transaction_level = 0
        self._savepoints = []
        self._current_isolation = IsolationLevel.READ_COMMITTED

        # Connection state
        self._connection = None
        self._module = None
        self._transaction_active = False
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
        """
        Load environment variables from .env file.
        Uses Path.cwd() to determine the relative location of the .env file.
        """
        # Get current working directory
        cwd = Path.cwd()

        # Define .env path relative to current working directory
        env_path = cwd / ".env"

        # Check if .env exists and load it
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
        """
        Set database credentials based on connection option.
        Uses properties from TargetDatabaseConnectionStringOption to determine behavior.
        """
        credential_change = (
            self.target_database_engine_connect_option.allow_credential_changes
        )
        # Check if credentials should not be changed (value == 1)
        if credential_change == 1:  # do_not_change_username_passord
            # Keep default credentials from environment
            return self

        # Handle credential changes for change_username_password (value == 2)
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

        # Choose parameter loading method based on connection type
        if self.target_database_engine_connect_option.uses_dsn:
            param_keys = format_config["LOAD_DSN_PARAMETER_KEYS"]
        else:
            param_keys = format_config["LOAD_DEFAULT_PARAMETER_KEYS"]

        # Load only the required parameters for this connection type
        return {key: config["DEFAULT_PARAMETERS"].get(key) for key in param_keys}

    def _build_connection_string(self, params: Dict[str, Any]) -> str:
        """Build connection string using provided parameters."""
        try:
            # Get the engine template directly
            engine_template = getattr(templates, self.target_database_engine_name)

            # Access the engine's configuration properly
            # Note: engine_template already has the target engine name as the top level key
            if self.target_database_engine_connect_option.uses_dsn:
                connection_string = engine_template[self.target_database_engine_name][
                    "FINALIZED_CONNECTION_PARAMS"
                ]["LAMBDA_FINALIZED_DSN_CONNECTION_STRING"](engine_template)
            else:
                # Update the template parameters with our overrides
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

            # Get the appropriate parameter loading method
            if self.target_database_engine_connect_option.uses_dsn:
                load_method = format_config["METHOD_LOAD_DSN_PARAMETER_KEYS_DICT"]
            else:
                load_method = format_config["METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT"]

            # Load default parameters using engine's method
            default_params = load_method(
                self.target_database_engine_name, self.engine_config
            )

            # Update with any custom parameters
            default_params.update(params)

            # Add credentials if required
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
            # Load module if not already loaded
            if not self._module:
                module_name = self.engine_config[self.target_database_engine_name][
                    "CRUDBASIC"
                ]["IMPORT"]
                self._module = importlib.import_module(module_name)

            # Create connection using the lambda from engine config
            connection_lambda = self.engine_config[self.target_database_engine_name][
                "CREATE_DATABASE_CONNECTION"
            ]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](self._connection_string)

            self._connection = connection_lambda()

            # Update state
            self.is_database_active = True
            self.database_attached_at = datetime.now()
            self.database_detached_at = None
            self._transaction_active = False

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
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert single record."""
        if not self._connection or not self.is_database_active:
            raise ConnectionError("Database connection not active")

        placeholder = self.engine_config["CRUDBASIC"]["PARAMETER_PLACEHOLDER"]
        columns = ",".join(data.keys())
        placeholders = ",".join([placeholder] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        with self._cursor() as cursor:
            try:
                cursor.execute(query, list(data.values()))
                last_id = cursor.lastrowid
                if self._connection and not getattr(self._connection, "closed", False):
                    self._connection.commit()
                return last_id
            except Exception as e:
                if self._connection and not getattr(self._connection, "closed", False):
                    self._connection.rollback()
                raise DatabaseError(f"Insert failed: {e}")

    @ensure_connected
    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """Update records."""
        if not self._connection or not self.is_database_active:
            raise ConnectionError("Database connection not active")

        placeholder = self.engine_config["CRUDBASIC"]["PARAMETER_PLACEHOLDER"]
        set_clause = ",".join(f"{k}={placeholder}" for k in data)
        where_clause = " AND ".join(f"{k}={placeholder}" for k in where)
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

        with self._cursor() as cursor:
            try:
                cursor.execute(query, list(data.values()) + list(where.values()))
                rows_affected = cursor.rowcount
                if self._connection and not getattr(self._connection, "closed", False):
                    self._connection.commit()
                return rows_affected
            except Exception as e:
                if self._connection and not getattr(self._connection, "closed", False):
                    self._connection.rollback()
                raise DatabaseError(f"Update failed: {e}")

    @ensure_connected
    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """Delete records."""
        if not self._connection or not self.is_database_active:
            raise ConnectionError("Database connection not active")

        placeholder = self.engine_config["CRUDBASIC"]["PARAMETER_PLACEHOLDER"]
        where_clause = " AND ".join(f"{k}={placeholder}" for k in where)
        query = f"DELETE FROM {table} WHERE {where_clause}"

        with self._cursor() as cursor:
            try:
                cursor.execute(query, list(where.values()))
                rows_affected = cursor.rowcount
                if self._connection and not getattr(self._connection, "closed", False):
                    self._connection.commit()
                return rows_affected
            except Exception as e:
                if self._connection and not getattr(self._connection, "closed", False):
                    self._connection.rollback()
                raise DatabaseError(f"Delete failed: {e}")

    @ensure_connected
    def execute_ddl(self, query: str) -> None:
        """Execute DDL statement."""
        if not self._connection or not self.is_database_active:
            raise ConnectionError("Database connection not active")

        with self._cursor() as cursor:
            try:
                cursor.execute(query)
                if self._connection and not getattr(self._connection, "closed", False):
                    self._connection.commit()
            except Exception as e:
                if self._connection and not getattr(self._connection, "closed", False):
                    self._connection.rollback()
                raise DatabaseError(f"DDL execution failed: {e}")

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            try:
                if self._transaction_active and not getattr(
                    self._connection, "closed", False
                ):
                    self._connection.rollback()
                if not getattr(self._connection, "closed", False):
                    self._connection.close()
            except Exception:
                pass
            finally:
                self._connection = None
                self._module = None
                self._transaction_active = False
                self.is_database_active = False
                self.database_detached_at = datetime.now()


def begin_transaction(
    self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED
) -> None:
    """Begin a transaction with specified isolation level."""
    if not self._connection:
        raise ConnectionError("No database connection")

    try:
        if isolation_level != self._current_isolation:
            self.set_isolation_level(isolation_level)

        self._connection.autocommit = False
        self._transaction_level += 1
        self._transaction_active = True

        # Create savepoint for nested transactions
        if self._transaction_level > 1:
            self.create_savepoint(f"SP_LEVEL_{self._transaction_level}")
    except Exception as e:
        raise DatabaseError(f"Failed to begin transaction: {str(e)}")


def commit(self) -> None:
    """Commit current transaction level."""
    if not self._connection:
        raise ConnectionError("No database connection")

    if not self._transaction_active:
        raise DatabaseError("No active transaction")

    try:
        if self._transaction_level > 1:
            # Release savepoint for nested transaction
            self.release_savepoint(self._savepoints[-1])
        else:
            # Commit main transaction
            self._connection.commit()
            self._transaction_active = False

        self._transaction_level -= 1
    except Exception as e:
        raise DatabaseError(f"Failed to commit transaction: {str(e)}")


def rollback(self, savepoint_name: Optional[str] = None) -> None:
    """Rollback to savepoint or full transaction."""
    if not self._connection:
        raise ConnectionError("No database connection")

    if savepoint_name:
        with self._cursor() as cursor:
            cursor.execute(f"ROLLBACK TRANSACTION {savepoint_name}")
    else:
        self._connection.rollback()
        self._transaction_level = 0
        self._savepoints.clear()

    def create_savepoint(self, name: str) -> None:
        """Create a savepoint in the current transaction."""
        if not self._transaction_active:
            raise DatabaseError("No active transaction")

        with self._cursor() as cursor:
            cursor.execute(f"SAVE TRANSACTION {name}")

    def rollback_to_savepoint(self, name: str) -> None:
        """Rollback to a specific savepoint."""
        if not self._transaction_active:
            raise DatabaseError("No active transaction")

        with self._cursor() as cursor:
            cursor.execute(f"ROLLBACK TRANSACTION {name}")

    def _get_current_isolation_level(self) -> Optional[IsolationLevel]:
        """Get current isolation level."""
        if not self._connection:
            return None

        try:
            engine_config = self.engine_config[self.target_database_engine_name]
            # Get isolation level query from engine configuration
            isolation_query = engine_config.get("TRANSACTION_MANAGEMENT", {}).get(
                "GET_ISOLATION_LEVEL_QUERY"
            )

            if not isolation_query:
                return self._current_isolation

            with self._cursor() as cursor:
                cursor.execute(isolation_query)
                result = cursor.fetchone()
                return IsolationLevel(result[0].upper()) if result else None

        except Exception as e:
            raise DatabaseError(f"Failed to get isolation level: {str(e)}")

    def __enter__(self):
        """Simple context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Simple context manager exit."""
        self.close()


# # def main():
# #     """mssql connection demonstration."""
# #     try:
# #         # initialize connector
# #         db = databaseconnector(
# #             target_database_engine=targetdatabaseengine.mssql,
# #             target_database_engine_connect_option=targetdatabaseconnectionstringoption.defaultformatanddefaultuserpwd,
# #         )

# #         # proper method chaining
# #         with (
# #             db.set_credentials_based_on_connect_option()
# #             .finalization_of_connection_parameters(
# #                 server="127.0.0.1", port_number=13001, database_name="adventureworks2019"
# #             )
# #             .connect_to_database() as conn
# #         ):
# #             print("\nstarting crud operations test:")

# #             # create schema
# #             print("\n1. creating schema:")
# #             conn.execute_ddl(
# #                 """
# #                 if not exists (select * from sys.schemas where name = 'aproduction')
# #                 begin
# #                     exec('create schema [aproduction]')
# #                 end
# #                 """
# #             )
# #             print("schema created successfully.")

# #             # create table with data
# #             print("\n2. creating table with data:")
# #             conn.execute_ddl(
# #                 """
# #                 if exists (select * from sys.tables where name = 'productinventory' and schema_name(schema_id) = 'aproduction')
# #                     drop table [aproduction].[productinventory]

# #                 select  productid,
# #                         locationid,
# #                         shelf,
# #                         bin,
# #                         quantity,
# #                         rowguid,
# #                         modifieddate
# #                 into [aproduction].[productinventory]
# #                 from [production].[productinventory]
# #                 """
# #             )
# #             print("table created and populated successfully.")

# #             # verify table creation and initial data
# #             print("\n3. initial quantity values:")
# #             conn.execute_query_to_prettytable(
# #                 """
# #                 select top 10
# #                     productid,
# #                     locationid,
# #                     quantity
# #                 from [aproduction].[productinventory]
# #                 order by productid
# #                 """,
# #                 print_result=true,
# #             )

# #             # update data
# #             print("\n4. updating quantities:")
# #             conn.execute_ddl(
# #                 """
# #                 update [aproduction].[productinventory]
# #                 set quantity = quantity + 30
# #                 where (productid % 2 = 1);
# #                 """
# #             )
# #             print("update completed successfully.")

# #             # verify the update
# #             print("\n5. updated quantity values:")
# #             conn.execute_query_to_prettytable(
# #                 """
# #                 select top 10
# #                     productid,
# #                     locationid,
# #                     quantity,
# #                     case
# #                         when productid % 2 = 1 then 'updated (+30)'
# #                         else 'not updated'
# #                     end as status
# #                 from [aproduction].[productinventory]
# #                 order by productid
# #                 """,
# #                 print_result=true,
# #             )

# #     except connectionerror as e:
# #         print(f"connection error: {e}")
# #     except databaseerror as e:
# #         print(f"database error: {e}")
# #     except exception as e:
# #         print(f"unexpected error: {e}")
# #     finally:
# #         if "db" in locals():
# #             db.close()
# #         print("\ntest completed and connection closed.")


# # if __name__ == "__main__":
# #     main()
# def main():
#     """MSSQL connection demonstration."""
#     try:
#         # Initialize connector
#         db = DatabaseConnector(
#             target_database_engine=TargetDatabaseEngine.MSSQL,
#             target_database_engine_connect_option=TargetDatabaseConnectionStringOption.CustomizeFormatAndDefaultUserPwd,
#         )

#         # Original method chaining with context manager
#         with (
#         ):

#             # test 1: check sql server version and CurrentDatabase
#             print("\n1. sql server version:")
#             version_result = conn.execute_query_to_prettytable(
#                 "select @@version as version,db_name() as CurrentDatabase",
#                 print_result=True,
#             )

#             print("\nStarting AdventoSQL Day 5:")

#             # verify table creation and initial data
#             print("\n2. AdventOfSQL Day 5:")
#             conn.execute_query_to_prettytable(
#                 """
#                     SELECT tp.production_date as ProductionDate,
#                         lag(tp.toys_produced) over (order by tp.production_date) as PreviousToysProduced,
#                         tp.toys_produced as ToysProduced,
#                         lead(tp.toys_produced) over (order by tp.production_date) as NextToysProduced,
#                         tp.toys_produced - lag(tp.toys_produced) over (order by tp.production_date) as PreviousProductionChange,
#                         format(1.-(tp.toys_produced*1.0 /lead(tp.toys_produced) over (order by tp.production_date desc)),'P') as PreviousProductionChangePCT,
#                         tp.toys_produced - lead(tp.toys_produced) over (order by tp.production_date )  as NextProductionChange,
#                         format(1. -(tp.toys_produced*1.0 /lead(tp.toys_produced) over (order by tp.production_date )),'P') as NextProductionChangePCT,
#                         row_number() over(order by tp.production_date desc) as row_number
#                         from  Day5.toy_production as tp
#                     order by tp.production_date desc,PreviousToysProduced
#         """,
#                 print_result=True,
#             )

#             # # # verify table creation and initial data
#             # # print("\n2. AdventOfSQL Day 5:")
#             # # conn.execute_query_to_dataframe(
#             # #     """

#             # #         SELECT tp.production_date as ProductionDate,
#             # #             lag(tp.toys_produced) over (order by tp.production_date) as PreviousToysProduced,
#             # #             tp.toys_produced as ToysProduced,
#             # #             lead(tp.toys_produced) over (order by tp.production_date) as NextToysProduced,
#             # #             tp.toys_produced - lag(tp.toys_produced) over (order by tp.production_date) as PreviousProductionChange,
#             # #             format(1.-(tp.toys_produced*1.0 /lead(tp.toys_produced) over (order by tp.production_date desc)),'P') as PreviousProductionChangePCT,
#             # #             tp.toys_produced - lead(tp.toys_produced) over (order by tp.production_date )  as NextProductionChange,
#             # #             format(1. -(tp.toys_produced*1.0 /lead(tp.toys_produced) over (order by tp.production_date )),'P') as NextProductionChangePCT,
#             # #             row_number() over(order by tp.production_date desc) as df_index
#             # #             from  Day5.toy_production as tp
#             # #         order by tp.production_date desc,PreviousToysProduced
#             # #     """,
#             # #     index_col="df_index",
#             # # )

#     except ConnectionError as e:
#         print(f"Connection error: {e}")
#     except DatabaseError as e:
#         print(f"Database error: {e}")
#     except Exception as e:
#         print(f"Unexpected error: {e}")
#     finally:
#         if "db" in locals():
#             db.close()
#         print("\nTest completed and connection closed.")

# if __name__ == "__main__":
#     main()
