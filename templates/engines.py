# database_target_engine_template_modules.py
from typing import Any, Dict
import importlib


def get_db_target_engine_module(module_name: str) -> Any:
    """
    Import database module dynamically.

    Args:
        module_name: Module to import (e.g., 'psycopg2', 'pyodbc')

    Returns:
        Imported module object

    Raises:
        ImportError: If module import fails
    """
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(
            f"Failed to import {module_name}. Make sure it's installed."
        ) from e


def load_default_parameter_keys_dict(
    target_database_engine: str, d: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Load default parameters excluding credentials.

    Args:
        target_database_engine: Database engine name
        d: Configuration dictionary

    Returns:
        Dictionary of non-credential parameters
    """
    keys = d[target_database_engine]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"][
        "LOAD_DEFAULT_PARAMETER_KEYS"
    ]
    return {
        key: d[target_database_engine]["DEFAULT_PARAMETERS"][key]
        for key in [k for k in keys if k not in ["USERNAME", "PASSWORD"]]
    }


def load_dsn_parameter_keys_dict(
    target_database_engine: str, d: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Load DSN parameters excluding credentials.

    Args:
        target_database_engine: Database engine name
        d: Configuration dictionary

    Returns:
        Dictionary of non-credential DSN parameters
    """
    keys = d[target_database_engine]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"][
        "LOAD_DSN_PARAMETER_KEYS"
    ]
    return {
        key: d[target_database_engine]["DEFAULT_PARAMETERS"][key]
        for key in [k for k in keys if k not in ["UID", "PWD"]]
    }


# Database Engine Configuration Templates
MSSQL: Dict[str, Dict[str, Any]] = {
    "MSSQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{ODBC Driver 17 for SQL Server}",
            "DSN_NAME": "AdventureWorks2019DSN",
            "DATABASE_NAME": "AdventureWorks2019",
            "SERVER": "localhost",
            "PORT_NUMBER": 13001,
            "USERNAME": "sa",
            "PASSWORD": "PH@123456789",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DRIVER",
                    "DSN_NAME",
                    "DATABASE_NAME",
                    "SERVER",
                    "PORT_NUMBER",
                ],
                "LOAD_DSN_PARAMETER_KEYS": ["DSN", "UID", "PWD"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "METHOD_LOAD_DSN_PARAMETER_KEYS_DICT": load_dsn_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": True,
                "BASE_CONNECTION_STRING": "DRIVER={0}; SERVER={1},{2}; DATABASE={3}; UID={4}; PWD={5};",
                "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};",
            },
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["MSSQL"][
                "DEFAULT_PARAMETERS"
            ]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["MSSQL"]["DEFAULT_PARAMETERS"]["DRIVER"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["SERVER"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["PORT_NUMBER"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["PASSWORD"],
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["MSSQL"][
                "DEFAULT_PARAMETERS"
            ]["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["MSSQL"]["DEFAULT_PARAMETERS"]["DSN_NAME"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["PASSWORD"],
            ),
        },
        "CRUDBASIC": {
            "IMPORT": "pyodbc",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True,
        },
        "CREATE_DATABASE_CONNECTION": {
            "REQUIRES_CREDENTIALS": True,
            "CONNECTION_NOTES": "Use pyodbc.connect with connection string",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module(
                "pyodbc"
            ).connect(
                finalized_parameter_connection_string
            ),
        },
        "TRANSACTION_MANAGEMENT": {
            "IS_ISOLATION_SUPPORTED": True,
            "GET_ISOLATION_LEVEL_QUERY": """
                SELECT CASE transaction_isolation_level 
                    WHEN 0 THEN 'UNSPECIFIED'
                    WHEN 1 THEN 'READ UNCOMMITTED' 
                    WHEN 2 THEN 'READ COMMITTED'
                    WHEN 3 THEN 'REPEATABLE READ'
                    WHEN 4 THEN 'SERIALIZABLE'
                    WHEN 5 THEN 'SNAPSHOT'
                END AS TRANSACTION_ISOLATION_LEVEL
                FROM sys.dm_exec_sessions 
                WHERE session_id = @@SPID
            """,
        },
    }
}

MYSQL: Dict[str, Dict[str, Any]] = {
    "MYSQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{MySQL ODBC 8.2 ANSI Driver}",
            "DSN_NAME": "MySQLNorthwindOrderDSN",
            "SERVER": "localhost",
            "PORT_NUMBER": 20101,
            "DATABASE_NAME": "NorthwindOrderSubsystem",
            "MULTI_HOST": 1,
            "CHARSET": "utf8mb4",
            "USERNAME": "root",
            "PASSWORD": "Password",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DRIVER",
                    "DSN_NAME",
                    "DATABASE_NAME",
                    "SERVER",
                    "PORT_NUMBER",
                    "MULTI_HOST",
                ],
                "LOAD_DSN_PARAMETER_KEYS": ["DSN", "UID", "PWD"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "METHOD_LOAD_DSN_PARAMETER_KEYS_DICT": load_dsn_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": True,
                "BASE_CONNECTION_STRING": "DRIVER={0}; SERVER={1}; PORT={2}; DATABASE={3}; UID={4}; PWD={5}; MULTI_HOST=1; CHARSET={6};",
                "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};",
            },
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["MYSQL"][
                "DEFAULT_PARAMETERS"
            ]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["MYSQL"]["DEFAULT_PARAMETERS"]["DRIVER"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["SERVER"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["PORT_NUMBER"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["PASSWORD"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["CHARSET"],
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["MYSQL"][
                "DEFAULT_PARAMETERS"
            ]["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["MYSQL"]["DEFAULT_PARAMETERS"]["DSN_NAME"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["PASSWORD"],
            ),
        },
        "CRUDBASIC": {
            "IMPORT": "pyodbc",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True,
        },
        "CREATE_DATABASE_CONNECTION": {
            "REQUIRES_CREDENTIALS": True,
            "CONNECTION_NOTES": "Use pyodbc.connect with connection string",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module(
                "pyodbc"
            ).connect(
                finalized_parameter_connection_string
            ),
        },
        "IS_ISOLATION_SUPPORTED": True,
        "TRANSACTION_MANAGEMENT": {
            "GET_ISOLATION_LEVEL_QUERY": "SHOW TRANSACTION ISOLATION LEVEL"
        },
    }
}


# Continuation of database_target_engine_template_modules.py

POSTGRESQL: Dict[str, Dict[str, Any]] = {
    "POSTGRESQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{PostgreSQL ANSI(x64)}",
            "DSN_NAME": "PostgreSQL_DSN",
            "DATABASE_NAME": "NorthwindOrderSubsystem",
            "SERVER": "localhost",
            "PORT_NUMBER": 20301,
            "USERNAME": "postgres",
            "PASSWORD": "Password",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DRIVER",
                    "DSN_NAME",
                    "DATABASE_NAME",
                    "SERVER",
                    "PORT_NUMBER",
                ],
                "LOAD_DSN_PARAMETER_KEYS": ["DSN", "UID", "PWD"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "METHOD_LOAD_DSN_PARAMETER_KEYS_DICT": load_dsn_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": True,
                "BASE_CONNECTION_STRING": "DRIVER={0}; SERVER={1}; Port={2}; DATABASE={3}; UID={4}; PWD={5};",
                "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};",
            },
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["POSTGRESQL"][
                "DEFAULT_PARAMETERS"
            ]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["DRIVER"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["SERVER"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["PORT_NUMBER"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["PASSWORD"],
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["POSTGRESQL"][
                "DEFAULT_PARAMETERS"
            ]["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["DSN_NAME"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["PASSWORD"],
            ),
        },
        "CRUDBASIC": {
            "IMPORT": "pyodbc",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True,
        },
        "CREATE_DATABASE_CONNECTION": {
            "REQUIRES_CREDENTIALS": True,
            "CONNECTION_NOTES": "Use pyodbc.connect with connection string",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module(
                "pyodbc"
            ).connect(
                finalized_parameter_connection_string
            ),
        },
        "TRANSACTION_MANAGEMENT": {
            "IS_ISOLATION_SUPPORTED": True,
            "GET_ISOLATION_LEVEL_QUERY": """
                SELECT CASE current_setting('transaction_isolation') 
                    WHEN 'read uncommitted' THEN 'READ UNCOMMITTED'
                    WHEN 'read committed' THEN 'READ COMMITTED'
                    WHEN 'repeatable read' THEN 'REPEATABLE READ'
                    WHEN 'serializable' THEN 'SERIALIZABLE'
                    ELSE 'SNAPSHOT'  -- PostgreSQL does not have a SNAPSHOT isolation level by default
                END AS TRANSACTION_ISOLATION_LEVEL;
            """,
        },
    }
}

SQLITE3: Dict[str, Dict[str, Any]] = {
    "SQLITE3": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{SQLite3 ODBC Driver}",
            "DSN_NAME": "ChinookDatabaseDSN",
            "FULLY_QUALIFIED_PATH": r"D:\\Sqlite3\\Databases",
            "DATABASE_NAME": r"chinook.db",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DRIVER",
                    "DSN_NAME",
                    "FULLY_QUALIFIED_PATH",
                    "DATABASE_NAME",
                ],
                "LOAD_DSN_PARAMETER_KEYS": ["DSN"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "METHOD_LOAD_DSN_PARAMETER_KEYS_DICT": load_dsn_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": True,
                "BASE_CONNECTION_STRING": "Driver={0};Database={1}{2};LongNames=0;Timeout=1000;NoTXN=0;SyncPragma=NORMAL;StepAPI=0;",
                "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};",
            },
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["SQLITE3"][
                "DEFAULT_PARAMETERS"
            ]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["SQLITE3"]["DEFAULT_PARAMETERS"]["DRIVER"],
                d["SQLITE3"]["DEFAULT_PARAMETERS"]["FULLY_QUALIFIED_PATH"],
                "\\" + d["SQLITE3"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["SQLITE3"][
                "DEFAULT_PARAMETERS"
            ]["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["SQLITE3"]["DEFAULT_PARAMETERS"]["DSN_NAME"]
            ),
        },
        "CRUDBASIC": {
            "IMPORT": "pyodbc",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": False,
        },
        "CREATE_DATABASE_CONNECTION": {
            "REQUIRES_CREDENTIALS": True,
            "CONNECTION_NOTES": "Use pyodbc.connect with connection string",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module(
                "pyodbc"
            ).connect(
                finalized_parameter_connection_string
            ),
        },
        "TRANSACTION_MANAGEMENT": {
            "IS_ISOLATION_SUPPORTED": False,
            "GET_ISOLATION_LEVEL_QUERY": """
                SELECT 'READ UNCOMMITTED' AS TRANSACTION_ISOLATION_LEVEL;
                -- This is a placeholder. SQLite does not natively support this kind of query.
            """,
        },
    }
}

DUCKDB: Dict[str, Dict[str, Any]] = {
    "DUCKDB": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{DuckDB Driver}",
            "DSN_NAME": "",
            "FULLY_QUALIFIED_PATH": r"Q:\\Database\\Accounting",
            "DATABASE_NAME": r"Accounting.duckdb",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DRIVER",
                    "DSN_NAME",
                    "FULLY_QUALIFIED_PATH",
                    "DATABASE_NAME",
                ],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": False,
                "BASE_CONNECTION_STRING": "{0}\\{1}",
                "BASE_ODBC_DSN_CONNECTION_STRING": None,
            },
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["DUCKDB"][
                "DEFAULT_PARAMETERS"
            ]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["DUCKDB"]["DEFAULT_PARAMETERS"]["FULLY_QUALIFIED_PATH"],
                d["DUCKDB"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: None,
        },
        "CRUDBASIC": {
            "IMPORT": "duckdb",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": False,
        },
        "CREATE_DATABASE_CONNECTION": {
            "REQUIRES_CREDENTIALS": False,
            "CONNECTION_NOTES": "Use duckdb.connect with connection string",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module(
                "duckdb"
            ).connect(
                finalized_parameter_connection_string
            ),
        },
        "TRANSACTION_MANAGEMENT": {
            "IS_ISOLATION_SUPPORTED": True,
            "GET_ISOLATION_LEVEL_QUERY": """
                SELECT 
                    CASE current_setting('isolation_level') 
                        WHEN 'read uncommitted' THEN 'READ UNCOMMITTED'
                        WHEN 'read committed' THEN 'READ COMMITTED'
                        WHEN 'serializable' THEN 'SERIALIZABLE'
                        ELSE 'UNKNOWN'
                    END AS TRANSACTION_ISOLATION_LEVEL
                """,
        },
    }
}

PSYCOPG2: Dict[str, Dict[str, Any]] = {
    "PSYCOPG2": {
        "DEFAULT_PARAMETERS": {
            "DATABASE_NAME": "NorthwindOrderSubsystem",
            "SERVER": "localhost",
            "PORT_NUMBER": 20301,
            "USERNAME": "postgres",
            "PASSWORD": "Password",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DATABASE_NAME",
                    "SERVER",
                    "PORT_NUMBER",
                ],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": False,
                "BASE_CONNECTION_STRING": "host={0} port={1} dbname={2} user={3} password={4}",
                "BASE_ODBC_DSN_CONNECTION_STRING": None,
            },
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["PSYCOPG2"][
                "DEFAULT_PARAMETERS"
            ]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["SERVER"],
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["PORT_NUMBER"],
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["PASSWORD"],
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: None,
        },
        "CRUDBASIC": {
            "IMPORT": "psycopg2",
            "PARAMETER_PLACEHOLDER": "%s",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True,
        },
        "CREATE_DATABASE_CONNECTION": {
            "REQUIRES_CREDENTIALS": True,
            "CONNECTION_NOTES": "Use psycopg2.connect with connection string",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module(
                "psycopg2"
            ).connect(
                finalized_parameter_connection_string
            ),
        },
        "TRANSACTION_MANAGEMENT": {
            "IS_ISOLATION_SUPPORTED": True,
            "GET_ISOLATION_LEVEL_QUERY": """
                SELECT CASE current_setting('transaction_isolation') 
                    WHEN 'read uncommitted' THEN 'READ UNCOMMITTED'
                    WHEN 'read committed' THEN 'READ COMMITTED'
                    WHEN 'repeatable read' THEN 'REPEATABLE READ'
                    WHEN 'serializable' THEN 'SERIALIZABLE'
                    ELSE 'SNAPSHOT'  -- PostgreSQL does not have a SNAPSHOT isolation level by default
                END AS TRANSACTION_ISOLATION_LEVEL;
            """,
        },
    }
}
