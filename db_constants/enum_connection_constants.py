# pydatabaseconnection/db_constants/enum_connection_constants.py
from enum import Enum

class TargetDatabaseEngine(Enum):
    """Supported database engines."""
    MSSQL = "MSSQL"
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    ORACLE = "ORACLE"
    SQLITE = "SQLITE"

class TargetDatabaseConnectionStringOption(Enum):
    """Connection string format options grouped in 4's."""
    # Group 1: DefaultFormat Options (1-4)
    DefaultFormatConnectionStrAndDefaultUserPwd = 1
    DefaultFormatConnectionStrAndChangeUserPwd = 2
    CustomizeFormatConnectionStrAndDefaultUserPwd = 3
    CustomizeFormatConnectionStrAndChangeUserPwd = 4
    
    # Group 2: DSN Options (5-8)
    Default_DSN_AndDefaultUserPwd = 5
    Default_DSN_AndChangeUserPwd = 6
    Customize_DSN_AndDefaultUserPwd = 7
    Customize_DSN_AndChangeUserPwd = 8

    @classmethod
    def is_default_format(cls, option) -> bool:
        """Check if option is in DefaultFormat group (1-4)."""
        return 1 <= option.value <= 4

    @classmethod
    def is_dsn_format(cls, option) -> bool:
        """Check if option is in DSN group (5-8)."""
        return 5 <= option.value <= 8

    @classmethod
    def uses_default_credentials(cls, option) -> bool:
        """Check if option uses default credentials (odd numbers)."""
        return option.value % 2 == 1

    @classmethod
    def uses_custom_credentials(cls, option) -> bool:
        """Check if option uses custom credentials (even numbers)."""
        return option.value % 2 == 0
