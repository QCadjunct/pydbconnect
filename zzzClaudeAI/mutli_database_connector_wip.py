"""   MultiDatabaseConnector class for connecting to multiple databases with different engines. """

from getpass import getpass
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import logging
from contextlib import contextmanager
from functools import wraps
import importlib
import pandas as pd
from pandas import DataFrame
from src.db_templates.base_database_connector import (
    BaseDatabaseConnector,
    DatabaseError,
)
from src.db_templates.database_target_engine_template_modules import (
    load_default_parameter_keys_dict,
    load_dsn_parameter_keys_dict,
    MSSQL,
    MYSQL,
    POSTGRESQL,
    PSYCOPG2,
    SQLITE3,
    DUCKDB as template,
)
from src.db_templates.database_target_engine_modules_enum_contraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
    ChangeDefaultUsernameAndPassword,
)
from src.utils import preload_default_parameters
from src.exceptions import (
    DatabaseError,
    ChangeDefaultUsernameAndPassword,
    DSNUnsupportedByTragetEngineError,
)


class MultiDatabaseConnector(BaseDatabaseConnector):
    def __init__(self):
        super().__init__()
        self.attached_database_instances: Dict[str, Dict[str, Any]] = {}
        self.attached_database_aliased_connections: Dict[str, Any] = {}
        self.active_attached_database_alias_name: Optional[str] = None
        self._active_attached_database_transaction: Optional[str] = None
        self._attached_database_operation_logger = logging.getLogger(__name__)

    def _load_target_database_engine_template_config(self) -> Dict[str, Any]:
        """Load engine-specific configuration."""
        try:
            return getattr(template, self.target_database_engine_name)
        except AttributeError as e:
            raise DatabaseError(
                f"Unsupported database engine: {self.target_database_engine_name}"
            ) from e

    def check_if_dsn_is_supported(self) -> "TargetDatabaseConnectionStringOption":
        """Check if DSN is supported by target database engine."""

        if (
            not self.target_database_engine_type.supports_dsn
            and self.target_database_engine_connect_option.uses_dsn
        ):
            raise DSNUnsupportedByTragetEngineError(
                f"DSN connections are not supported by {self.target_database_engine_name}"
            )
        return self.target_database_engine_connect_option

    def attach_database_instance(
        self,
        database_alias_name: str,
        target_database_engine_type: TargetDatabaseEngine,
        target_database_engine_connect_option: TargetDatabaseConnectionStringOption,
    ) -> "MultiDatabaseConnector":
        try:
            self.target_database_engine_name = target_database_engine_type.name
            self.target_database_engine_connect_option = (
                self.check_if_dsn_is_supported()
            )
            self.target_database_engine_template_config = (
                self._load_target_database_engine_template_config()
            )

            self.attached_database_instances[database_alias_name] = {
                "database_alias_name": database_alias_name,
                "target_database_engine_type": target_database_engine_type,
                "target_database_engine_connect_option": target_database_engine_connect_option,
                "target_database_engine_template_config": self.target_database_engine_template_config,
                "finalized_connection_parameters": self.finalization_of_connection_parameters,
                "is_active": True,
                "attached_at": datetime.now(),
                "detached_at": None,
            }

            if not self.active_attached_database_alias_name:
                self.active_attached_database_alias_name = database_alias_name

            self._attached_database_operation_logger.info(
                f"Successfully attached database: {database_alias_name}"
            )
            return self

        except Exception as e:
            self._attached_database_operation_logger.error(
                f"Failed to attach database {database_alias_name}: {str(e)}"
            )
            raise DatabaseError(
                f"Failed to attach database {database_alias_name}: {str(e)}"
            )

    def get_default_database_parameters(self) -> Dict[str, Any]:
        """Get default parameters from template."""
        if not self.active_attached_database_alias_name:
            raise DatabaseError("No active database alias")

        instance = self.attached_database_instances[
            self.active_attached_database_alias_name
        ]
        target_database_engine_name = instance["target_database_engine_type"].name

        if self.connect_option.uses_dsn:
            return load_dsn_parameter_keys_dict(
                self.target_database_engine_name,
                {
                    target_database_engine_name: self.target_database_engine_template_config[
                        self.target_database_engine_name
                    ]
                },
            )
        else:
            return load_default_parameter_keys_dict(
                self.target_database_engine_name,
                {
                    target_database_engine_name: self.target_database_engine_template_config[
                        self.target_database_engine_name
                    ]
                },
            )

    @preload_default_parameters(get_default_database_parameters)
    def finalize_database_connection_parameters(
        self, **params
    ) -> "MultiDatabaseConnector":
        super().finalization_of_connection_parameters(**params)
        return self

    def connect_to_database(self) -> "MultiDatabaseConnector":
        if not self.active_attached_database_alias_name:
            raise DatabaseError("No active database alias")

        try:
            instance = self.attached_database_instances[
                self.active_attached_database_alias_name
            ]
            self.target_database_engine_name = instance[
                "target_database_engine_type"
            ].name

            connection_creator = self.target_database_engine_template_config[
                self.target_database_engine_name
            ]["CREATE_DATABASE_CONNECTION"][
                "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"
            ]
            database_connection = connection_creator(self._connection_string)()

            self.attached_database_aliased_connections[
                self.active_attached_database_alias_name
            ] = database_connection
            self._connection = database_connection

            return self

        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")

        if target_database_alias not in self.attached_database_aliased_connections:
            raise DatabaseError(f"Database alias {target_database_alias} not attached")

        database_connection = self.attached_database_aliased_connections[
            target_database_alias
        ]

        try:
            if (
                self._active_attached_database_transaction
                and self._active_attached_database_transaction != target_database_alias
            ):
                raise DatabaseError(
                    f"Cannot start transaction on {target_database_alias} while transaction "
                    f"active on {self._active_attached_database_transaction}"
                )

            self._active_attached_database_transaction = target_database_alias
            database_connection.autocommit = False
            yield
            database_connection.commit()

        except Exception as e:
            database_connection.rollback()
            raise DatabaseError(f"Transaction failed: {str(e)}")

        finally:
            database_connection.autocommit = True
            self._active_attached_database_transaction = None

    def execute_database_query(
        self, query: str, database_alias_name: Optional[str] = None
    ) -> pd.DataFrame:
        target_database_alias = (
            database_alias_name or self.active_attached_database_alias_name
        )
        if not target_database_alias:
            raise DatabaseError("No active database alias")

        if target_database_alias not in self.attached_database_aliased_connections:
            raise DatabaseError(f"Database alias {target_database_alias} not attached")

        try:
            instance = self.attached_database_instances[target_database_alias]
            placeholder = instance["target_database_engine_template_config"][
                instance["target_database_engine_type"].name
            ]["CRUDBASIC"]["PARAMETER_PLACEHOLDER"]

            return pd.read_sql(
                query.replace("?", placeholder),
                self.attached_database_aliased_connections[target_database_alias],
            )
        except Exception as e:
            self._attached_database_operation_logger.error(
                f"Query failed on database alias {target_database_alias}: {str(e)}"
            )
            raise DatabaseError(f"Query failed: {str(e)}")

    def execute_many_database_query(
        self,
        query: str,
        parameters: List[Any],
        database_alias_name: Optional[str] = None,
    ) -> None:
        target_database_alias = (
            database_alias_name or self.active_attached_database_alias_name
        )
        if not target_database_alias:
            raise DatabaseError("No active database alias")

        if target_database_alias not in self.attached_database_aliased_connections:
            raise DatabaseError(f"Database alias {target_database_alias} not attached")

        try:
            instance = self.attached_database_instances[target_database_alias]
            placeholder = instance["target_database_engine_template_config"][
                instance["target_database_engine_type"].name
            ]["CRUDBASIC"]["PARAMETER_PLACEHOLDER"]

            with self.attached_database_aliased_connections[
                target_database_alias
            ].cursor() as cursor:
                cursor.executemany(query.replace("?", placeholder), parameters)
                self.attached_database_aliased_connections[
                    target_database_alias
                ].commit()

            self._attached_database_operation_logger.debug(
                f"Batch execution successful on database alias: {target_database_alias}"
            )
        except Exception as e:
            self._attached_database_operation_logger.error(
                f"Batch execution failed on database alias {target_database_alias}: {str(e)}"
            )
            raise DatabaseError(f"Batch execution failed: {str(e)}")

    def copy_table(
        self,
        source_database_alias_name: str,
        target_database_alias_name: str,
        table_name: str,
        batch_size: int = 1000,
    ) -> None:
        if (
            source_database_alias_name not in self.attached_database_instances
            or target_database_alias_name not in self.attached_database_instances
        ):
            raise DatabaseError("Source or target database alias not attached")

        try:
            source_database_config = self.attached_database_instances[
                source_database_alias_name
            ]["target_database_engine_template_config"]
            schema_query = source_database_config.get(
                "INFORMATION_SCHEMA_QUERY",
                """SELECT COLUMN_NAME, DATA_TYPE 
                  FROM INFORMATION_SCHEMA.COLUMNS 
                  WHERE TABLE_NAME = '{table_name}'""",
            )

            schema_df = self.execute_database_query(
                schema_query.format(table_name=table_name), source_database_alias_name
            )

            columns = [
                f"{row['COLUMN_NAME']} {row['DATA_TYPE']}"
                for _, row in schema_df.iterrows()
            ]
            create_query = f"CREATE TABLE {table_name} ({', '.join(columns)})"

            with self.database_transaction(target_database_alias_name):
                self.execute_database_query(create_query, target_database_alias_name)

            total_rows = 0
            offset = 0

            while True:
                select_query = f"""
                   SELECT * FROM {table_name} 
                   ORDER BY (SELECT NULL) 
                   OFFSET {offset} ROWS FETCH NEXT {batch_size} ROWS ONLY
               """

                batch_df = self.execute_database_query(
                    select_query, source_database_alias_name
                )
                if batch_df.empty:
                    break

                target_database_config = self.attached_database_instances[
                    target_database_alias_name
                ]["target_database_engine_template_config"]
                placeholder = target_database_config[
                    self.instances[target_database_alias_name]["engine_type"].name
                ]["CRUDBASIC"]["PARAMETER_PLACEHOLDER"]

                placeholders = ",".join([placeholder] * len(batch_df.columns))
                insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"

                with self.database_transaction(target_database_alias_name):
                    self.execute_many_database_query(
                        insert_query,
                        batch_df.values.tolist(),
                        target_database_alias_name,
                    )

                total_rows += len(batch_df)
                offset += batch_size
                self._attached_database_operation_logger.info(
                    f"Copied {total_rows} rows to {target_database_alias_name}.{table_name}"
                )

            self._attached_database_operation_logger.info(
                f"Successfully copied table {table_name} from {source_database_alias_name} to {target_database_alias_name}"
            )

        except Exception as e:
            self._attached_database_operation_logger.error(
                f"Failed to copy table {table_name}: {str(e)}"
            )
            raise DatabaseError(f"Failed to copy table: {str(e)}")

    def validate_attached_database_state(self, database_alias_name: str) -> None:
        if database_alias_name not in self.attached_database_instances:
            raise DatabaseError(f"Database alias {database_alias_name} not attached")

        instance = self.attached_database_instances[database_alias_name]
        if not instance["is_active"]:
            raise DatabaseError(
                f"Database alias {database_alias_name} is not active. "
                f"Detached at: {instance['detached_at']}"
            )

        if database_alias_name not in self.attached_database_aliased_connections:
            raise ConnectionError(
                f"No active connection for database alias {database_alias_name}"
            )

    def get_database_template_info(
        self, database_alias_name: Optional[str] = None
    ) -> Dict[str, Any]:
        target_database_alias = (
            database_alias_name or self.active_attached_database_alias_name
        )
        self.validate_attached_database_state(target_database_alias)

        instance = self.attached_database_instances[target_database_alias]
        self.target_database_engine_name = instance["target_database_engine_type"].name

        return {
            "engine_type": self.target_database_engine_name,
            "connection_type": instance["target_database_engine_connect_option"].name,
            "requires_credentials": instance["target_database_engine_template_config"][
                self.target_database_engine_name
            ]["CRUDBASIC"]["IS_USERNAME_AND_PASSWORD_REQUIRED"],
            "supports_dsn": instance["target_database_engine_connect_option"].uses_dsn,
            "placeholder": instance["target_database_engine_template_config"][
                self.target_database_engine_name
            ]["CRUDBASIC"]["PARAMETER_PLACEHOLDER"],
        }


def switch_attached_database_alias(
    self, database_alias_name: str
) -> "MultiDatabaseConnector":
    if database_alias_name not in self.attached_database_instances:
        raise DatabaseError(f"Database alias {database_alias_name} not attached")

    self.active_attached_database_alias_name = database_alias_name
    if database_alias_name in self.attached_database_aliased_connections:
        self._connection = self.attached_database_aliased_connections[
            database_alias_name
        ]

    instance = self.attached_database_instances[database_alias_name]
    self.target_database_engine_name = instance["target_database_engine_type"].name
    self.target_database_engine_connect_option = instance[
        "target_database_engine_connect_option"
    ]
    self.target_database_engine_template_config = instance[
        "target_database_engine_template_config"
    ]

    return self


@contextmanager
def database_transaction(self, database_alias_name: Optional[str] = None):
    target_database_alias = (
        database_alias_name or self.active_attached_database_alias_name
    )
    if not target_database_alias:
        raise DatabaseError("No active database alias")
