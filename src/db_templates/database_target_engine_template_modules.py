# data
from typing import Any, Callable, Dict
import importlib
  
def get_db_target_engine_module(module_name: str) -> Any:
    """
    Dynamically import and return the specified database module.

    Args:
        module_name (str): Name of the module to import (e.g., 'psycopg2', 'pyodbc')

    Returns:
        Any: The imported module

    Raises:
        ImportError: If the module cannot be imported
    """
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Failed to import {module_name}. Make sure it's installed.") from e

def load_default_parameter_keys_dict(target_database_engine:str, d: Dict[str, Any]) -> Dict[str, Any]:
    """
        Modify the load_default_parameter_keys_dict function to exclude the DEFAULT_PARAMETERS USERNAME and PASSWORD
        
        Only the default parameters from a configuration dictionary d that are specific to a specific target database engine. 
        The function returns a dictionary containing these parameters, excluding sensitive information like usernames and passwords.
        
    Args:
        target_database_engine (str): _description_
        d (Dict[str, Any]): _description_

    Returns:
        Dict[str, Any]: _description_
    """
    keys = d[target_database_engine]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["LOAD_DEFAULT_PARAMETER_KEYS"]
    return {key: d[target_database_engine]["DEFAULT_PARAMETERS"][key] for key in [k for k in keys if k not in ["USERNAME", "PASSWORD"]]}

def load_dsn_parameter_keys_dict(target_database_engine:str, d: Dict[str, Any]) -> Dict[str, Any]:
    """
        Modify the load_dsn_parameter_keys_dict function to exclude the DEFAULT_PARAMETERS UID(USERNAME) and PWD(PASSWORD)
        
        Only the default parameters from a configuration dictionary d that are specific to a specific target database engine. 
        The function returns a dictionary containing these parameters, excluding sensitive information like usernames and passwords.
        
    Args:
        target_database_engine (str): _description_
        d (Dict[str, Any]): _description_

    Returns:
        Dict[str, Any]: _description_
    """
    keys = d[target_database_engine]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["LOAD_DSN_PARAMETER_KEYS"]
    return {key: d[target_database_engine]["DEFAULT_PARAMETERS"][key] for key in [k for k in keys if k not in ["UID","PWD"]]}  # not in DSN "USERNAME", "PASSWORD"

MSSQL: Dict[str, Dict[str, Any]] = {
    "MSSQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{ODBC Driver 17 for SQL Server}",
            "DSN_NAME": "Northwinds2024StudentDSN",
            "DATABASE_NAME": "Northwinds2024Student",
            "SERVER": "localhost",
            "PORT_NUMBER": 13001,
            "USERNAME": "sa",
            "PASSWORD": "PH@123456789",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DRIVER", "DSN_NAME","DATABASE_NAME","SERVER","PORT_NUMBER"],
                "LOAD_DSN_PARAMETER_KEYS": ["DSN","UID","PWD"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "METHOD_LOAD_DSN_PARAMETER_KEYS_DICT": load_dsn_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": True,
                "BASE_CONNECTION_STRING": "DRIVER={0}; SERVER={1},{2}; DATABASE={3}; UID={4}; PWD={5};",
                "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};"
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["MSSQL"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["MSSQL"]["DEFAULT_PARAMETERS"]["DRIVER"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["SERVER"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["PORT_NUMBER"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["PASSWORD"]
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["MSSQL"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["MSSQL"]["DEFAULT_PARAMETERS"]["DSN_NAME"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["UID"],
                d["MSSQL"]["DEFAULT_PARAMETERS"]["PWD"]
            )
        },
        "CRUDBASIC": {
            "IMPORT":"pyodbc",
            "PARAMETER_PLACEHOLDER":"?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
       },
        "CREATE_DATABASE_CONNECTION": {
            "CONNECTION_NOTES": "Use pyodbc.connect with the appropriate connection string: LAMBDA_FINALIZED_BASE_CONNECTION_STRING or LAMBDA_FINALIZED_DSN_CONNECTION_STRING if ODBC DSN is supported.",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('pyodbc').connect(finalized_parameter_connection_string)
        }
    }
}

"""
    MSSQL Dictionary Structure and Usage

    This dictionary contains configuration and connection details for Microsoft SQL Server (MSSQL) database operations.

    Structure:
    1. DEFAULT_PARAMETERS:
    - Contains default connection parameters such as driver, DSN name, database name, server, port, username, and password.
    - Includes FORMAT_CONNECTION_STRING subdictionary with configuration for connection string formatting.

    2. FINALIZED_CONNECTION_PARAMS:
    - LAMBDA_FINALIZED_BASE_CONNECTION_STRING: Lambda function to format the base connection string using default parameters.
    - LAMBDA_FINALIZED_DSN_CONNECTION_STRING: Lambda function to format the DSN connection string.

    3. CRUDBASIC:
    - Specifies the import module (pyodbc) and parameter placeholder for SQL queries.

    4. CREATE_DATABASE_CONNECTION:
    - CONNECTION_NOTES: Provides guidance on using pyodbc.connect with the appropriate connection string.
    - LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING: Lambda function to create a database connection using pyodbc.

    Usage:
    1. Accessing connection strings:
    base_conn_string = MSSQL["MSSQL"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](MSSQL)
    final_base_connection_string = MYSQL["MYSQL"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](MYSQL)
    print("Base Connection String:", final_base_connection_string)
    
    dsn_conn_string = MSSQL["MSSQL"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_DSN_CONNECTION_STRING"](MSSQL)
    final_dsn_connection_string = MYSQL["MYSQL"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_DSN_CONNECTION_STRING"](MYSQL)
    print("DSN Connection String:", final_dsn_connection_string)

    2. Creating a database connection:
    connection_func = MSSQL["MSSQL"]["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](base_conn_string)
    db_connection = connection_func()

    Note: Ensure that pyodbc is installed and the ODBC driver is properly configured on your system before using this configuration.

"""

MYSQL: Dict[str, Any] = {
    "MYSQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{MySQL ODBC 8.2 ANSI Driver}",
            "DSN_NAME": "MySQLNorthwindOrderDSN",
            "SERVER": "localhost",
            "PORT_NUMBER": 20101,
            "DATABASE_NAME": "NorthwindOrderSubsystem",
            "USERNAME": "root",
            "PASSWORD": "Password",
            "MULTI_HOST": 1,
            "CHARSET": "utf8mb4",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DRIVER", "DSN_NAME","DATABASE_NAME","SERVER","PORT_NUMBER","MULTI_HOST"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "METHOD_LOAD_DSN_PARAMETER_KEYS_DICT": load_dsn_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": True,
                "BASE_CONNECTION_STRING": "DRIVER={0}; SERVER={1}; PORT={2}; DATABASE={3}; UID={4}; PWD={5}; MULTI_HOST=1; CHARSET={6};",
                "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};",
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["MYSQL"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["MYSQL"]["DEFAULT_PARAMETERS"]["DRIVER"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["SERVER"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["PORT_NUMBER"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["PASSWORD"],
                d["MYSQL"]["DEFAULT_PARAMETERS"]["CHARSET"]
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["MYSQL"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["MYSQL"]["DEFAULT_PARAMETERS"]["DSN_NAME"]
            )
        },
        "CRUDBASIC": {
            "IMPORT":"pyodbc",
            "PARAMETER_PLACEHOLDER":"?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        },
        "CREATE_DATABASE_CONNECTION": {
            "CONNECTION_NOTES": "Use pyodbc.connect with the appropriate connection string: LAMBDA_FINALIZED_BASE_CONNECTION_STRING or LAMBDA_FINALIZED_DSN_CONNECTION_STRING if ODBC DSN is supported.",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('pyodbc').connect(finalized_parameter_connection_string)
        }
    }
}
"""
    MYSQL Dictionary Structure and Usage

    This dictionary contains configuration and connection details for MySQL database operations using ODBC.

    Structure:
    1. DEFAULT_PARAMETERS:
    - Contains default connection parameters such as driver, DSN name, server, port, database name, username, password, multi-host setting, and charset.
    - Includes FORMAT_CONNECTION_STRING subdictionary with configuration for connection string formatting.

    2. FINALIZED_CONNECTION_PARAMS:
    - LAMBDA_FINALIZED_BASE_CONNECTION_STRING: Lambda function to format the base connection string using default parameters.
    - LAMBDA_FINALIZED_DSN_CONNECTION_STRING: Lambda function to format the DSN connection string.

    3. CRUDBASIC:
    - Specifies the import module (pyodbc) and parameter placeholder for SQL queries.

    4. CREATE_DATABASE_CONNECTION:
    - CONNECTION_NOTES: Provides guidance on using pyodbc.connect with the appropriate connection string.
    - LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING: Lambda function to create a database connection using pyodbc.

    Usage:
    1. Accessing connection strings:
    base_conn_string = MYSQL["MYSQL"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](MYSQL)
    dsn_conn_string = MYSQL["MYSQL"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_DSN_CONNECTION_STRING"](MYSQL)

    2. Creating a database connection:
    connection_func = MYSQL["MYSQL"]["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](base_conn_string)
    db_connection = connection_func()

    Key Features:
    - Supports both standard and DSN-based connections
    - Uses MySQL ODBC 8.2 ANSI Driver
    - Configures multi-host and UTF-8 character set by default
    - Provides flexibility for customizing connection parameters

    Note:   Ensure that pyodbc is installed and the MySQL ODBC driver is properly configured on your system 
            before using this configuration. The default configuration uses localhost on port 20101, 
            but these can be adjusted as needed.
"""

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
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DRIVER", "DSN_NAME","DATABASE_NAME","SERVER","PORT_NUMBER"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "METHOD_LOAD_DSN_PARAMETER_KEYS_DICT": load_dsn_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": "Y",
                "BASE_CONNECTION_STRING": "DRIVER={0}; SERVER={1}; Port={2}; DATABASE={3}; UID={4}; PWD={5};",
                "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};",
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["DRIVER"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["SERVER"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["PORT_NUMBER"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["PASSWORD"]
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["POSTGRESQL"]["DEFAULT_PARAMETERS"]["DSN_NAME"]
            )
        },
        "CRUDBASIC": {
            "IMPORT":"pyodbc",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True,
            "PARAMETER_PLACEHOLDER":"?"
        },
        "CREATE_DATABASE_CONNECTION": {
            "CONNECTION_NOTES": "Use pyodbc.connect with the appropriate connection string: LAMBDA_FINALIZED_BASE_CONNECTION_STRING or LAMBDA_FINALIZED_DSN_CONNECTION_STRING if ODBC DSN is supported.",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('pyodbc').connect(finalized_parameter_connection_string)
        }
    }
}
"""
    POSTGRESQL Dictionary Structure and Usage

    This dictionary contains configuration and connection details for PostgreSQL database operations.

    Structure:
    1. DEFAULT_PARAMETERS:
    - Contains default connection parameters such as 
            driver, DSN name, database name, server, port, username, and password.
    - Includes FORMAT_CONNECTION_STRING subdictionary with configuration for connection string formatting.
        - LOAD_DEFAULT_PARAMETER_KEYS: List of keys to load from default parameters.
        - METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT: Function to load default parameter keys.
        - IS_DSN_NAME_SUPPORTED: Indicates whether DSN is supported ("Y" in this case).
        - BASE_CONNECTION_STRING: Template for the base connection string.
        - BASE_ODBC_DSN_CONNECTION_STRING: Template for the DSN connection string.

    2. FINALIZED_CONNECTION_PARAMS:
    - LAMBDA_FINALIZED_BASE_CONNECTION_STRING: Lambda function to format the base connection string 
                                            using default parameters.
    - LAMBDA_FINALIZED_DSN_CONNECTION_STRING: Lambda function to format the DSN connection string.

    3. CRUDBASIC:
    - IMPORT: Specifies the import module (pyodbc).
    - PARAMETER_PLACEHOLDER: Defines the SQL parameter placeholder ("?").

    4. CREATE_DATABASE_CONNECTION:
    - CONNECTION_NOTES: Provides guidance on using pyodbc.connect with the appropriate connection string.
    - LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING: Lambda function to create a database connection using pyodbc.

    Usage:
    1. Accessing connection strings:
    base_conn_string = 
        POSTGRESQL["POSTGRESQL"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](POSTGRESQL)
    dsn_conn_string = 
        POSTGRESQL["POSTGRESQL"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_DSN_CONNECTION_STRING"](POSTGRESQL)

    2. Creating a database connection:
    connection_func = 
        POSTGRESQL["POSTGRESQL"]["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](base_conn_string)
    db_connection = connection_func()

    Note: Ensure that pyodbc is installed and the PostgreSQL ODBC driver is properly configured on your system before using this configuration. The default driver used is "{PostgreSQL ANSI(x64)}", which may need to be adjusted based on your system setup.
"""
DUCKDB: dict[str, Any] = {
    "DUCKDB": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{DuckDB Driver}",
            "DSN_NAME": "",
            "FULLY_QUALIFIED_PATH": r"Q:\\Database\\Accounting",
            "DATABASE_NAME": r"Accounting.duckdb",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DRIVER", "DSN_NAME","FULLY_QUALIFIED_PATH","DATABASE_NAME"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": False,
                "FORMAT_BASE_CONNECTION_STRING": "{0}\\{1}",
                "FORMAT_BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};"
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["DUCKDB"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["FORMAT_BASE_CONNECTION_STRING"].format(
                d["DUCKDB"]["DEFAULT_PARAMETERS"]["FULLY_QUALIFIED_PATH"], d["DUCKDB"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"]),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["DUCKDB"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["FORMAT_BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["DUCKDB"]["DEFAULT_PARAMETERS"]["DSN_NAME"])
        },
        "CRUDBASIC": {
            "IMPORT":"duckdb",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": False,
            "PARAMETER_PLACEHOLDER":"?"
        },
        "CREATE_DATABASE_CONNECTION": {
            "CONNECTION_NOTES": "Use pyodbc.connect with the appropriate connection string: LAMBDA_FINALIZED_BASE_CONNECTION_STRING or LAMBDA_FINALIZED_DSN_CONNECTION_STRING if ODBC DSN is supported.",
            "TARGET_ENGINE_MODULE_IMPORT": "duckdb",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('duckdb').connect(finalized_parameter_connection_string)
        }
    }
}
"""
    DUCKDB Dictionary Structure and Usage

    This dictionary contains configuration and connection details for DuckDB database operations.

    Structure:
    1. DEFAULT_PARAMETERS:
    - Contains default connection parameters such as driver, DSN name, fully qualified path, and database name.
    - Includes FORMAT_CONNECTION_STRING subdictionary with configuration for connection string formatting.
    - Note: DSN_NAME is empty by default, as DSN is not supported for DuckDB.

    2. FINALIZED_CONNECTION_PARAMS:
    - LAMBDA_FINALIZED_BASE_CONNECTION_STRING: 
            Lambda function to format the base connection string using the fully qualified path and database name.
    - LAMBDA_FINALIZED_DSN_CONNECTION_STRING: 
            Lambda function to format the DSN connection string (not typically used for DuckDB).

    3. CRUDBASIC:
    - Specifies the import module (pyodbc) and parameter placeholder for SQL queries.

    4. CREATE_DATABASE_CONNECTION:
    - CONNECTION_NOTES: Provides guidance on using the appropriate connection string.
    - LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING: 
            Lambda function to create a database connection using duckdb.connect().

    Usage:
    1. Accessing connection strings:
    base_conn_string = 
        DUCKDB["DUCKDB"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](DUCKDB)
    # Note: DSN connection string is not typically used for DuckDB

    2. Creating a database connection:
    connection_func = 
        DUCKDB["DUCKDB"]["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](base_conn_string)
    db_connection = connection_func()

    Key Points:
    - DuckDB uses file-based databases, so the connection string is typically just the path to the database file.
    - The FULLY_QUALIFIED_PATH and DATABASE_NAME are combined to form the complete path to the DuckDB file.
    - DSN (Data Source Name) is not supported for DuckDB, so the DSN-related fields are typically not used.
    - The connection is created using duckdb.connect() rather than pyodbc.connect().

    Note: Ensure that the DuckDB Python package is installed (pip install duckdb) before using this configuration.
"""
SQLITE3: Dict[str, Dict[str, Any]] = {
    "SQLITE3": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{SQLite3 ODBC Driver}",
            "DSN_NAME": "ChinookDatabaseDSN",
            "FULLY_QUALIFIED_PATH": r"D:\\Sqlite3\\Databases",
            "DATABASE_NAME": r"chinook.db",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DRIVER", "DSN_NAME","FULLY_QUALIFIED_PATH","DATABASE_NAME"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "METHOD_LOAD_DSN_PARAMETER_KEYS_DICT": load_dsn_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": "Y",
                "BASE_CONNECTION_STRING": "Driver={0};Database={1}{2};LongNames=0;Timeout=1000;NoTXN=0;SyncPragma=NORMAL;StepAPI=0;",
                "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};",
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["SQLITE3"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["SQLITE3"]["DEFAULT_PARAMETERS"]["DRIVER"], 
                d["SQLITE3"]["DEFAULT_PARAMETERS"]["FULLY_QUALIFIED_PATH"],
                "\\" + d["SQLITE3"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"]
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["SQLITE3"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["SQLITE3"]["DEFAULT_PARAMETERS"]["DSN_NAME"]
            )
        },
        "CRUDBASIC": {
            "IMPORT":"pyodbc",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": False,            
            "PARAMETER_PLACEHOLDER":"?"
        },
        "CREATE_DATABASE_CONNECTION": {
            "CONNECTION_NOTES": "Use pyodbc.connect with the appropriate connection string: LAMBDA_FINALIZED_BASE_CONNECTION_STRING or LAMBDA_FINALIZED_DSN_CONNECTION_STRING if ODBC DSN is supported.",
            "TARGET_ENGINE_MODULE_IMPORT": "pyodbc",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('pyodbc').connect(finalized_parameter_connection_string)
        }
    }
}

"""
    SQLITE3 Dictionary Structure and Usage

    This dictionary contains configuration and connection details for SQLite3 database operations using ODBC.

    Structure:
    1. DEFAULT_PARAMETERS:
    - DRIVER: Specifies the ODBC driver for SQLite3.
    - DSN_NAME: Name of the DSN (Data Source Name) for the Chinook database.
    - FULLY_QUALIFIED_PATH: The directory path where the SQLite3 database is located.
    - DATABASE_NAME: The name of the SQLite3 database file.
    - FORMAT_CONNECTION_STRING: Subdictionary with configuration for connection string formatting.
        - Includes methods for loading default parameters and specifies base connection strings.

    2. FINALIZED_CONNECTION_PARAMS:
    - LAMBDA_FINALIZED_BASE_CONNECTION_STRING: 
        Lambda function to format the base connection string using default parameters.
        Format: "Driver={DRIVER};Database={FULLY_QUALIFIED_PATH}\{DATABASE_NAME};LongNames=0;Timeout=1000;NoTXN=0;SyncPragma=NORMAL;StepAPI=0;"
    - LAMBDA_FINALIZED_DSN_CONNECTION_STRING: Lambda function to format the DSN connection string.
        Format: "DSN={DSN_NAME};"

    3. CRUDBASIC:
    - IMPORT: Specifies the import module (pyodbc) for database operations.
    - PARAMETER_PLACEHOLDER: Defines the placeholder character ('?') for SQL query parameters.

    4. CREATE_DATABASE_CONNECTION:
    - CONNECTION_NOTES: Provides guidance on using pyodbc.connect with the appropriate connection string.
    - LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING: Lambda function to create a database connection using pyodbc.

    Usage:
    1. Accessing connection strings:
    base_conn_string = SQLITE3["SQLITE3"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](SQLITE3)
    dsn_conn_string = SQLITE3["SQLITE3"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_DSN_CONNECTION_STRING"](SQLITE3)

    2. Creating a database connection:
    connection_func = SQLITE3["SQLITE3"]["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](base_conn_string)
    db_connection = connection_func()

    Note: Ensure that pyodbc is installed and the SQLite3 ODBC driver is properly configured on your system 
          before using this configuration. The default configuration assumes the Chinook sample database is being used.
""" 

PSYCOPG2: Dict[str, Dict[str, Any]] = {
    "PSYCOPG2": {
        "DEFAULT_PARAMETERS": {
            "DATABASE_NAME": "NorthwindOrderSubsystem",
            "SERVER": "localhost",
            "PORT_NUMBER": 20301,
            "USERNAME": "postgres",
            "PASSWORD": "Password",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DRIVER", "DATABASE_NAME","SERVER","PORT_NUMBER"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": "N",
                "BASE_CONNECTION_STRING": "host={0}; port={1}; database={2}; user={3}; password={4};",
                "BASE_ODBC_DSN_CONNECTION_STRING": None
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["SERVER"],
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["PORT_NUMBER"],
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["PASSWORD"]
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["PSYCOPG2"]["DEFAULT_PARAMETERS"]["DSN_NAME"]
            )
        },
        "CRUDBASIC": {
            "IMPORT":"psycopg2",
            "PARAMETER_PLACEHOLDER":"%s",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        },
        "CREATE_DATABASE_CONNECTION": {
            "CONNECTION_NOTES": "Use pyodbc.connect with the appropriate connection string: LAMBDA_FINALIZED_BASE_CONNECTION_STRING or LAMBDA_FINALIZED_DSN_CONNECTION_STRING if ODBC DSN is supported.",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('psycopg2').connect(finalized_parameter_connection_string)
        }
    }
}
"""
    PSYCOPG2 Dictionary Structure and Usage

    This dictionary contains configuration and connection details for PostgreSQL database operations using the psycopg2 library.

    Structure:
    1. DEFAULT_PARAMETERS:
    - Contains default connection parameters such as database name, server, port, username, and password.
    - Includes FORMAT_CONNECTION_STRING subdictionary with configuration for connection string formatting.
    - Note: ODBC DSN is not supported for this configuration (IS_DSN_NAME_SUPPORTED: "N").

    2. FINALIZED_CONNECTION_PARAMS:
    - LAMBDA_FINALIZED_BASE_CONNECTION_STRING: Lambda function to format the base connection string using default parameters.
    - LAMBDA_FINALIZED_DSN_CONNECTION_STRING: Lambda function for DSN connection string (returns None as DSN is not supported).

    3. CRUDBASIC:
    - Specifies the import module (psycopg2) and parameter placeholder ("%s") for SQL queries.

    4. CREATE_DATABASE_CONNECTION:
    - CONNECTION_NOTES: Provides guidance on using psycopg2.connect with the appropriate connection string.
    - LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING: Lambda function to create a database connection using psycopg2.

    Usage:
    1. Accessing the base connection string:
    base_conn_string = PSYCOPG2["PSYCOPG2"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](PSYCOPG2)

    2. Creating a database connection:
    connection_func = PSYCOPG2["PSYCOPG2"]["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](base_conn_string)
    db_connection = connection_func()

    Note: Ensure that psycopg2 is installed in your Python environment before using this configuration. 
          Unlike the MSSQL configuration, this setup does not support ODBC DSN connections.

    Key Differences from MSSQL:
    1. No DRIVER parameter is required.
    2. The connection string format is different, using key=value pairs.
    3. The parameter placeholder for SQL queries is "%s" instead of "?".
    4. DSN connections are not supported.
    5. The import module is 'psycopg2' instead of 'pyodbc'.

    This configuration is specifically tailored for PostgreSQL databases and utilizes the psycopg2 library for database interactions.
"""