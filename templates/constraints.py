from enum import Enum
from typing import Dict, Any, Type, Callable, Optional, List
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

from abc import ABC, abstractmethod
import importlib

# from db_connector.templates import engines as templates
import templates.engines as templates


class ChangeDefaultUsernameAndPassword(Enum):
    """Connection string options for database connections."""

    # Standard connection strings
    DoNotChangeUserAndPwd = 1
    ChangeUserAndPwd = 2
    ChangeUserAndPwdPlusShow = 3

    @property
    def changes_default_credentials(self) -> bool:
        return self.value in (2, 3)

    @property
    def show_password(self) -> bool:
        return self.value == 3

    @property
    def change_default_username_and_password(self) -> int:
        """Get the name of the ChangeDefaultUsernameAndPassword."""
        return self.value


class TargetDatabaseEngine(Enum):
    """Database engines supported by pydbconnect."""

    MSSQL = "MSSQL"
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    SQLITE3 = "SQLITE3"
    DUCKDB = "DUCKDB"
    PSYCOPG2 = "PSYCOPG2"

    @property
    def target_database_engine_name(self) -> str:
        """Get the name of the target database engine."""
        return self.name

    @property
    def requires_authentication(self) -> bool:
        """
        Check if engine requires username/password authentication.
        Gets value from engine configuration.
        """

        return self.engine_config.get("CREATE_DATABASE_CONNECTION", False).get("REQUIRES_CREDENTIALS", False)

    @property
    def engine_config(self) -> dict:
        """Get the configuration for this engine."""
        return getattr(templates, self.target_database_engine_name)

    @property
    def supports_dsn(self) -> bool:
        """
        Check if engine supports DSN connections.
        Gets value from engine configuration.
        """
        return (
            self.engine_config.get("DEFAULT_PARAMETERS", {})
            .get("FORMAT_CONNECTION_STRING", {})
            .get("IS_DSN_NAME_SUPPORTED", False)
        )

    @property
    def no_dsn_supports(self) -> int:
        """
        Check if engine does not support DSN connections.
        Gets value from engine configuration.
        """
        return (
            1
            if not self.engine_config.get("DEFAULT_PARAMETERS", {})
            .get("FORMAT_CONNECTION_STRING", {})
            .get("IS_DSN_NAME_SUPPORTED", False)
            else 2
        )

    @property
    def import_module(self) -> str:
        """
        Get the Python module name required for this engine.
        Gets value from engine configuration.
        """
        return self.engine_config.get("CRUDBASIC", {}).get("IMPORT", "")

    def load_engine_config(self) -> Dict[str, Any]:
        """Load complete engine configuration."""

        return getattr(templates, self.target_database_engine_name)

    def get_placeholder(self) -> str:
        """Get SQL parameter placeholder for this engine."""
        return self.engine_config.get("CRUDBASIC", {}).get("PARAMETER_PLACEHOLDER", "?")

    def validate_connection_option(self, option: "TargetDatabaseConnectionStringOption") -> bool:
        """
        Validate if the connection option is compatible with this engine.

        Args:
            option: The connection option to validate

        Returns:
            bool: True if option is compatible, False otherwise
        """
        # DSN validation
        if option.uses_dsn and not self.supports_dsn:
            return False

        # Authentication validation
        if option.changes_credentials and not self.requires_authentication:
            return False

        return True


class TargetDatabaseConnectionStringOption(Enum):
    """Connection string options for database connections."""

    # Standard connection strings
    DefaultFormatAndDefaultUserPwd = 1
    DefaultFormatAndChangeUserPwd = 2
    CustomizeFormatAndDefaultUserPwd = 3
    CustomizeFormatAndChangeUserPwd = 4

    # DSN connection strings
    Default_DSN_AndDefaultUserPwd = 5
    Default_DSN_AndChangeUserPwd = 6
    Customize_DSN_AndDefaultUserPwd = 7
    Customize_DSN_AndChangeUserPwd = 8

    @property
    def target_database_connection_string_option(self) -> str:
        """Get the name of the TargetDatabaseConnectionStringOption."""
        return self.name

    @property
    def uses_dsn(self) -> bool:
        """Check if this option uses DSN connection."""
        # if self.target_database_connection_string_option in [5, 6, 7, 8] use DSN connection

        uses_dsn_connection = (5, 6, 7, 8)
        return self.target_database_connection_string_option in uses_dsn_connection

    @property
    def changes_credentials(self) -> "ChangeDefaultUsernameAndPassword":
        """Check if this option requires credential changes."""
        return (
            ChangeDefaultUsernameAndPassword.ChangeUserAndPwd
            if not (self.value % 2 == 0)
            else ChangeDefaultUsernameAndPassword.DoNotChangeUserAndPwd
        )

    @property
    def allow_credential_changes(self) -> int:
        """Check if this option allows credential changes."""

        #    class  ChangeDefaultUsernameAndPassword(Enum)
        #    DoNotChangeUserAndPwd= 1
        #    ChangeUserAndPwd = 2
        #
        #   change_username_password if self.target_database_connection_string_option in [2, 4, 6, 8] else do_not_change_username_passord
        #
        do_not_change_username_passord = 1
        change_username_password = 2
        do_not_change = (2, 4, 6, 8)
        return (
            change_username_password
            if self.target_database_connection_string_option in do_not_change
            else do_not_change_username_passord
        )

    @property
    def uses_custom_format(self) -> bool:
        """Check if this option uses custom connection string format."""
        return True if self.target_database_connection_string_option in (3, 4, 7, 8) else False

    @property
    def changes_default_credentials(self) -> bool:
        """Check if this option requires credential changes."""
        return self.value in (2, 3)

    def validate_for_engine(self, engine: TargetDatabaseEngine) -> bool:
        """
        Validate if this option is compatible with given database engine.

        Args:
            engine: The database engine to validate against

        Returns:
            bool: True if compatible, False otherwise
        """
        return engine.validate_connection_option(self)


class DatabaseConnectionError(Exception):
    """Base exception for database connection errors."""

    pass


class InvalidConnectionOptionError(DatabaseConnectionError):
    """Raised when connection option is incompatible with database engine."""

    def __init__(
        self,
        target_database_engine: TargetDatabaseEngine,
        target_atabase_connection_option: TargetDatabaseConnectionStringOption,
    ):
        """f"Connection option {target_atabase_connection_option.name} is not compatible with {target_database_engine.name}" """

        message = f"Connection option {target_atabase_connection_option.name} is not compatible with {target_database_engine.name}"
        super().__init__(message)


class IsolationLevel(Enum):
    """SQL Standard Isolation Levels with properties."""

    UNSPECIFIED = "UNSPECIFIED"
    READ_UNCOMMITTED = "READ UNCOMMITTED"
    READ_COMMITTED = "READ COMMITTED"
    REPEATABLE_READ = "REPEATABLE READ"
    SERIALIZABLE = "SERIALIZABLE"
    SNAPSHOT = "SNAPSHOT"
    READ_COMMITTED_SNAPSHOT = "READ COMMITTED SNAPSHOT"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_string(cls, value: str) -> "IsolationLevel":
        """Convert string to isolation level enum."""
        try:
            return cls(value.upper())
        except ValueError:
            return cls.UNKNOWN

    @property
    def dirty_reads(self) -> bool:
        return self == IsolationLevel.READ_UNCOMMITTED

    @property
    def non_repeatable_reads(self) -> bool:
        return self in [IsolationLevel.READ_UNCOMMITTED, IsolationLevel.READ_COMMITTED]

    @property
    def phantom_reads(self) -> bool:
        return self in [
            IsolationLevel.READ_UNCOMMITTED,
            IsolationLevel.READ_COMMITTED,
            IsolationLevel.REPEATABLE_READ,
        ]

    @property
    def is_snapshot_based(self) -> bool:
        return self in [IsolationLevel.SNAPSHOT, IsolationLevel.READ_COMMITTED_SNAPSHOT]

    @classmethod
    def get_default_level(cls) -> "IsolationLevel":
        """Get default isolation level."""
        return cls.READ_COMMITTED

    def get_sql_statement(self) -> str:
        """Get SQL to set this isolation level."""
        return f"SET TRANSACTION ISOLATION LEVEL {self.value}"


class FileExtension(Enum):
    """Supported file extensions."""

    CSV = "csv"
    JSON = "json"
    HTML = "html"
    XML = "xml"
    XLS = "xls"
    XLSX = "xlsx"
    PARQUET = "parquet"
    FEATHER = "feather"
    HDF = "h5"
    ORC = "orc"
    PICKLE = "pkl"
    SQL = "sql"
    STATA = "stata"


class WriterMethod(Enum):
    """Pandas DataFrame writer methods."""

    CSV = "to_csv"
    JSON = "to_json"
    HTML = "to_html"
    XML = "to_xml"
    EXCEL = "to_excel"
    PARQUET = "to_parquet"
    FEATHER = "to_feather"
    HDF = "to_hdf"
    ORC = "to_orc"
    PICKLE = "to_pickle"
    SQL = "to_sql"
    STATA = "to_stata"


class FileFormat(Enum):
    """Pandas I/O formats with read/write capabilities."""

    # Text formats
    CSV = (FileExtension.CSV, pd.read_csv, WriterMethod.CSV)
    JSON = (FileExtension.JSON, pd.read_json, WriterMethod.JSON)
    HTML = (FileExtension.HTML, pd.read_html, WriterMethod.HTML)
    XML = (FileExtension.XML, pd.read_xml, WriterMethod.XML)

    # Excel formats
    XLS = (FileExtension.XLS, pd.read_excel, WriterMethod.EXCEL)
    XLSX = (FileExtension.XLSX, pd.read_excel, WriterMethod.EXCEL)

    # Binary formats
    PARQUET = (FileExtension.PARQUET, pd.read_parquet, WriterMethod.PARQUET)
    FEATHER = (FileExtension.FEATHER, pd.read_feather, WriterMethod.FEATHER)
    HDF = (FileExtension.HDF, pd.read_hdf, WriterMethod.HDF)
    ORC = (FileExtension.ORC, pd.read_orc, WriterMethod.ORC)
    PICKLE = (FileExtension.PICKLE, pd.read_pickle, WriterMethod.PICKLE)

    # SQL and specialized formats
    SQL = (FileExtension.SQL, pd.read_sql, WriterMethod.SQL)
    STATA = (FileExtension.STATA, pd.read_stata, WriterMethod.STATA)

    def __init__(self, extension: FileExtension, reader: Callable, writer_method: WriterMethod):
        self._extension = extension
        self._reader = reader
        self._writer_method = writer_method

    @property
    def extension(self) -> str:
        """Get file extension."""
        return self._extension.value

    @property
    def value(self) -> str:
        """Get file extension (compatibility with base Enum)."""
        return self._extension.value

    def write_dataframe(self, df: pd.DataFrame, path: str, **kwargs: Any) -> None:
        """Write DataFrame using format-specific writer."""
        writer = getattr(df, self._writer_method.value)
        writer(path, **kwargs)

    def read_file(self, path: str, **kwargs: Any) -> pd.DataFrame:
        """Read file using format-specific reader."""
        return self._reader(path, **kwargs)

    @classmethod
    def get_excel_formats(cls) -> list["FileFormat"]:
        """Get all Excel format types."""
        return [cls.XLS, cls.XLSX]

    @classmethod
    def from_extension(cls, extension: str) -> Optional["FileFormat"]:
        """Get format enum from file extension."""
        try:
            ext = FileExtension(extension.lstrip("."))
            return next(fmt for fmt in cls if fmt._extension == ext)
        except ValueError:
            return None


def test_enums():
    # Test accessing enum values
    print("\nTesting basic enum access:")
    print(
        f"Value of DefaultFormatAndDefaultUserPwd: {TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd.value}"
    )
    print(
        f"Name of DefaultFormatAndDefaultUserPwd: {TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd.name}"
    )

    # Test properties
    option = TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd
    print("\nTesting properties for DefaultFormatAndChangeUserPwd:")
    print(f"Uses DSN: {option.uses_dsn}")
    print(f"Changes credentials: {option.changes_credentials}")
    print(f"Allow credential changes: {option.allow_credential_changes}")
    print(f"Uses custom format: {option.uses_custom_format}")

    # Test DSN option
    dsn_option = TargetDatabaseConnectionStringOption.Default_DSN_AndDefaultUserPwd
    print("\nTesting DSN option:")
    print(f"Uses DSN: {dsn_option.uses_dsn}")
    print(f"Changes credentials: {dsn_option.changes_credentials}")


@dataclass
class TransferMetrics:
    """ETL transfer metrics."""

    table_name: str
    start_time: datetime
    end_time: datetime
    row_count: int
    duration_seconds: float
    source_columns: int
    target_columns: int
    source_data_types: List[str]
    target_data_types: List[str]

    def __str__(self) -> str:
        """Format metrics for display."""
        return (
            f"Table: {self.table_name}\n"
            f"  Rows: {self.row_count:,}\n"
            f"  Duration: {self.duration_seconds:.2f}s\n"
            f"  Columns: {self.source_columns} -> {self.target_columns}\n"
            f"  Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"  End: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )


class TransactionType(Enum):
    """Transaction Types for database transaction management."""

    BEGIN = "BEGIN"
    COMMIT = "COMMIT"
    ROLLBACK = "ROLLBACK"

    @property
    def sql_statement(self) -> str:
        """Get the SQL statement for this transaction type."""
        if self == TransactionType.BEGIN:
            return "BEGIN TRANSACTION"
        return self.value

    @property
    def requires_isolation_level(self) -> bool:
        """Check if this transaction type requires isolation level."""
        return self == TransactionType.BEGIN

    @property
    def can_nest(self) -> bool:
        """Check if this transaction type supports nesting."""
        return self == TransactionType.BEGIN

    @classmethod
    def get_default_type(cls) -> "TransactionType":
        """Get default transaction type."""
        return cls.BEGIN

    @classmethod
    def from_string(cls, value: str) -> "TransactionType":
        """Convert string to transaction type enum."""
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"Invalid transaction type: {value}")


if __name__ == "__main__":
    test_enums()
