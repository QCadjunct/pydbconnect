from typing import Dict, Any, Optional, Callable
from pathlib import Path

def create_base_connection_string(params: Dict[str, Any]) -> str:
    """Create standard connection string format"""
    driver = params.get('DRIVER', '')
    return (
        f"DRIVER={driver};"
        f"SERVER={params['SERVER']};"
        f"PORT={params['PORT_NUMBER']};"
        f"DATABASE={params['DATABASE_NAME']};"
    ) if driver else ""

def create_dsn_connection_string(params: Dict[str, Any]) -> str:
    """Create DSN connection string format"""
    return f"DSN={params['DSN_NAME']};"

# Microsoft SQL Server Template
MSSQL: Dict[str, Dict[str, Any]] = {
    "MSSQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{ODBC Driver 17 for SQL Server}",
            "DSN_NAME": "Northwinds2024StudentDSN",
            "DATABASE_NAME": "Northwinds2024Student",
            "SERVER": "localhost",
            "PORT_NUMBER": 13001,
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DRIVER", "DSN_NAME", "DATABASE_NAME", "SERVER", "PORT_NUMBER"
                ],
                "IS_DSN_NAME_SUPPORTED": True
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda params: (
                f"DRIVER={params['DRIVER']};"
                f"SERVER={params['SERVER']},{params['PORT_NUMBER']};"
                f"DATABASE={params['DATABASE_NAME']};"
                f"TrustServerCertificate=yes;Encrypt=yes;"
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda params: create_dsn_connection_string(params)
        },
        "CRUDBASIC": {
            "IMPORT": "pyodbc",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        }
    }
}

# PostgreSQL Template
POSTGRESQL: Dict[str, Dict[str, Any]] = {
    "POSTGRESQL": {
        "DEFAULT_PARAMETERS": {
            "DATABASE_NAME": "postgres",
            "SERVER": "localhost",
            "PORT_NUMBER": 5432,
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DATABASE_NAME", "SERVER", "PORT_NUMBER"
                ],
                "IS_DSN_NAME_SUPPORTED": False
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda params: (
                f"host={params['SERVER']} "
                f"port={params['PORT_NUMBER']} "
                f"dbname={params['DATABASE_NAME']}"
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": None
        },
        "CRUDBASIC": {
            "IMPORT": "psycopg2",
            "PARAMETER_PLACEHOLDER": "%s",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        }
    }
}

# MySQL Template
MYSQL: Dict[str, Dict[str, Any]] = {
    "MYSQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{MySQL ODBC 8.0 ANSI Driver}",
            "DSN_NAME": "MySQLDSN",
            "DATABASE_NAME": "mysql",
            "SERVER": "localhost",
            "PORT_NUMBER": 3306,
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DRIVER", "DSN_NAME", "DATABASE_NAME", "SERVER", "PORT_NUMBER"
                ],
                "IS_DSN_NAME_SUPPORTED": True
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda params: (
                f"DRIVER={params['DRIVER']};"
                f"SERVER={params['SERVER']};"
                f"PORT={params['PORT_NUMBER']};"
                f"DATABASE={params['DATABASE_NAME']};"
                f"CHARSET=utf8mb4;"
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda params: create_dsn_connection_string(params)
        },
        "CRUDBASIC": {
            "IMPORT": "pyodbc",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        }
    }
}

# SQLite Template
SQLITE3: Dict[str, Dict[str, Any]] = {
    "SQLITE3": {
        "DEFAULT_PARAMETERS": {
            "DATABASE_NAME": "database.db",
            "FULLY_QUALIFIED_PATH": str(Path.cwd()),
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DATABASE_NAME", "FULLY_QUALIFIED_PATH"
                ],
                "IS_DSN_NAME_SUPPORTED": False
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda params: str(
                Path(params['FULLY_QUALIFIED_PATH']) / params['DATABASE_NAME']
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": None
        },
        "CRUDBASIC": {
            "IMPORT": "sqlite3",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": False
        }
    }
}

# DuckDB Template
DUCKDB: Dict[str, Dict[str, Any]] = {
    "DUCKDB": {
        "DEFAULT_PARAMETERS": {
            "DATABASE_NAME": "database.duckdb",
            "FULLY_QUALIFIED_PATH": str(Path.cwd()),
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DATABASE_NAME", "FULLY_QUALIFIED_PATH"
                ],
                "IS_DSN_NAME_SUPPORTED": False
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda params: str(
                Path(params['FULLY_QUALIFIED_PATH']) / params['DATABASE_NAME']
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": None
        },
        "CRUDBASIC": {
            "IMPORT": "duckdb",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": False
        }
    }
}

# PSYCOPG2 Template
PSYCOPG2: Dict[str, Dict[str, Any]] = {
    "PSYCOPG2": {
        "DEFAULT_PARAMETERS": {
            "DATABASE_NAME": "postgres",
            "SERVER": "localhost",
            "PORT_NUMBER": 5432,
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [
                    "DATABASE_NAME", "SERVER", "PORT_NUMBER"
                ],
                "IS_DSN_NAME_SUPPORTED": False
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda params: (
                f"host={params['SERVER']} "
                f"port={params['PORT_NUMBER']} "
                f"dbname={params['DATABASE_NAME']}"
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": None
        },
        "CRUDBASIC": {
            "IMPORT": "psycopg2",
            "PARAMETER_PLACEHOLDER": "%s",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        }
    }
}

# Template Registry
TEMPLATES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "MSSQL": MSSQL,
    "POSTGRESQL": POSTGRESQL,
    "MYSQL": MYSQL,
    "SQLITE3": SQLITE3,
    "DUCKDB": DUCKDB,
    "PSYCOPG2": PSYCOPG2
}

def get_template(engine_name: str) -> Dict[str, Dict[str, Any]]:
    """Get database template by engine name"""
    if engine_name not in TEMPLATES:
        raise KeyError(f"No template found for engine: {engine_name}")
    return TEMPLATES[engine_name]