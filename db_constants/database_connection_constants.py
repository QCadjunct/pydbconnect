# pydatabaseconnection/db_constants/database_connection_constants.py
from typing import Any, Callable, Dict, Optional, List
import importlib
from dataclasses import dataclass, field
from enum import Enum, auto

class ConnectionStringFormat(Enum):
    """Enum for connection string format options."""
    STANDARD = auto()
    DSN = auto()

@dataclass
class ConnectionConfig:
    """Base configuration for database connections."""
    driver: str
    dsn_name: str = ""
    database_name: str = ""
    server: str = "localhost"
    port_number: int = 0
    username: str = ""
    password: str = ""
    charset: str = "utf8mb4"
    multi_host: bool = False
    fully_qualified_path: str = ""
    additional_params: Dict[str, Any] = field(default_factory=dict)

def get_db_target_engine_module(module_name: str) -> Any:
    """Dynamically import and return the specified database module."""
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Failed to import {module_name}. Make sure it's installed.") from e

def load_default_parameter_keys_dict(target_database_engine: str, d: Dict[str, Any]) -> Dict[str, Any]:
    """Load default parameters excluding credentials."""
    try:
        keys = d[target_database_engine]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["LOAD_DEFAULT_PARAMETER_KEYS"]
        return {
            key: d[target_database_engine]["DEFAULT_PARAMETERS"][key] 
            for key in [k for k in keys if k not in ["USERNAME", "PASSWORD"]]
        }
    except KeyError as e:
        raise KeyError(f"Invalid configuration structure for {target_database_engine}: {str(e)}")

def load_dsn_parameter_keys_dict(target_database_engine: str, d: Dict[str, Any]) -> Dict[str, Any]:
    """Load DSN parameters excluding credentials."""
    try:
        keys = d[target_database_engine]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["LOAD_DSN_PARAMETER_KEYS"]
        return {
            key: d[target_database_engine]["DEFAULT_PARAMETERS"][key] 
            for key in [k for k in keys if k not in ["UID", "PWD"]]
        }
    except KeyError as e:
        raise KeyError(f"Invalid configuration structure for {target_database_engine}: {str(e)}")

class DatabaseEngineConfig:
    """Base class for database engine configurations."""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.format_connection_string = {
            "LOAD_DEFAULT_PARAMETER_KEYS": [
                "DRIVER", "DSN_NAME", "DATABASE_NAME", "SERVER", "PORT_NUMBER"
            ],
            "LOAD_DSN_PARAMETER_KEYS": ["DSN", "UID", "PWD"],
            "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
            "METHOD_LOAD_DSN_PARAMETER_KEYS_DICT": load_dsn_parameter_keys_dict,
        }

    def get_connection_dict(self) -> Dict[str, Any]:
        """Get the complete connection configuration dictionary."""
        raise NotImplementedError

    def _get_base_connection_string(self, d: Dict[str, Any]) -> str:
        """Generate base connection string."""
        raise NotImplementedError

    def _get_dsn_connection_string(self, d: Dict[str, Any]) -> str:
        """Generate DSN connection string."""
        raise NotImplementedError
class MSSQLConfig(DatabaseEngineConfig):
    """MSSQL specific configuration."""
    
    def get_connection_dict(self) -> Dict[str, Any]:
        return {
            "MSSQL": {
                "DEFAULT_PARAMETERS": {
                    "DRIVER": self.config.driver,
                    "DSN_NAME": self.config.dsn_name,
                    "DATABASE_NAME": self.config.database_name,
                    "SERVER": self.config.server,
                    "PORT_NUMBER": self.config.port_number,
                    "USERNAME": self.config.username,
                    "PASSWORD": self.config.password,
                    "FORMAT_CONNECTION_STRING": {
                        **self.format_connection_string,
                        "IS_DSN_NAME_SUPPORTED": True,
                        "BASE_CONNECTION_STRING": "DRIVER={0}; SERVER={1},{2}; DATABASE={3}; UID={4}; PWD={5};",
                        "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};"
                    }
                },
                "FINALIZED_CONNECTION_PARAMS": {
                    "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": self._get_base_connection_string,
                    "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": self._get_dsn_connection_string
                },
                "CRUDBASIC": {
                    "IMPORT": "pyodbc",
                    "PARAMETER_PLACEHOLDER": "?",
                    "IS_USERNAME_AND_PASSWORD_REQUIRED": True
                },
                "CREATE_DATABASE_CONNECTION": {
                    "CONNECTION_NOTES": "Use pyodbc.connect with appropriate connection string",
                    "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": 
                        lambda conn_str: lambda: get_db_target_engine_module('pyodbc').connect(conn_str)
                }
            }
        }

    def _get_base_connection_string(self, d: Dict[str, Any]) -> str:
        params = d["MSSQL"]["DEFAULT_PARAMETERS"]
        return params["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
            params["DRIVER"],
            params["SERVER"],
            params["PORT_NUMBER"],
            params["DATABASE_NAME"],
            params["USERNAME"],
            params["PASSWORD"]
        )

    def _get_dsn_connection_string(self, d: Dict[str, Any]) -> str:
        params = d["MSSQL"]["DEFAULT_PARAMETERS"]
        return params["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
            params["DSN_NAME"],
            params["USERNAME"],
            params["PASSWORD"]
        )

class MySQLConfig(DatabaseEngineConfig):
    """MySQL specific configuration."""
    
    def get_connection_dict(self) -> Dict[str, Any]:
        return {
            "MYSQL": {
                "DEFAULT_PARAMETERS": {
                    "DRIVER": self.config.driver,
                    "DSN_NAME": self.config.dsn_name,
                    "DATABASE_NAME": self.config.database_name,
                    "SERVER": self.config.server,
                    "PORT_NUMBER": self.config.port_number,
                    "USERNAME": self.config.username,
                    "PASSWORD": self.config.password,
                    "MULTI_HOST": 1,
                    "CHARSET": self.config.charset,
                    "FORMAT_CONNECTION_STRING": {
                        **self.format_connection_string,
                        "IS_DSN_NAME_SUPPORTED": True,
                        "BASE_CONNECTION_STRING": "DRIVER={0}; SERVER={1}; PORT={2}; DATABASE={3}; UID={4}; PWD={5}; MULTI_HOST=1; CHARSET={6};",
                        "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};"
                    }
                },
                "FINALIZED_CONNECTION_PARAMS": {
                    "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": self._get_base_connection_string,
                    "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": self._get_dsn_connection_string
                },
                "CRUDBASIC": {
                    "IMPORT": "pyodbc",
                    "PARAMETER_PLACEHOLDER": "?",
                    "IS_USERNAME_AND_PASSWORD_REQUIRED": True
                },
                "CREATE_DATABASE_CONNECTION": {
                    "CONNECTION_NOTES": "Use pyodbc.connect with appropriate connection string",
                    "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": 
                        lambda conn_str: lambda: get_db_target_engine_module('pyodbc').connect(conn_str)
                }
            }
        }

    def _get_base_connection_string(self, d: Dict[str, Any]) -> str:
        params = d["MYSQL"]["DEFAULT_PARAMETERS"]
        return params["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
            params["DRIVER"],
            params["SERVER"],
            params["PORT_NUMBER"],
            params["DATABASE_NAME"],
            params["USERNAME"],
            params["PASSWORD"],
            params["CHARSET"]
        )

    def _get_dsn_connection_string(self, d: Dict[str, Any]) -> str:
        params = d["MYSQL"]["DEFAULT_PARAMETERS"]
        return params["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
            params["DSN_NAME"],
            params["USERNAME"],
            params["PASSWORD"]
        )

class PostgreSQLConfig(DatabaseEngineConfig):
    """PostgreSQL specific configuration."""
    
    def get_connection_dict(self) -> Dict[str, Any]:
        return {
            "POSTGRESQL": {
                "DEFAULT_PARAMETERS": {
                    "DRIVER": self.config.driver,
                    "DSN_NAME": self.config.dsn_name,
                    "DATABASE_NAME": self.config.database_name,
                    "SERVER": self.config.server,
                    "PORT_NUMBER": self.config.port_number,
                    "USERNAME": self.config.username,
                    "PASSWORD": self.config.password,
                    "FORMAT_CONNECTION_STRING": {
                        **self.format_connection_string,
                        "IS_DSN_NAME_SUPPORTED": "Y",
                        "BASE_CONNECTION_STRING": "DRIVER={0}; SERVER={1}; Port={2}; DATABASE={3}; UID={4}; PWD={5};",
                        "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};"
                    }
                },
                "FINALIZED_CONNECTION_PARAMS": {
                    "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": self._get_base_connection_string,
                    "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": self._get_dsn_connection_string
                },
                "CRUDBASIC": {
                    "IMPORT": "pyodbc",
                    "PARAMETER_PLACEHOLDER": "?",
                    "IS_USERNAME_AND_PASSWORD_REQUIRED": True
                },
                "CREATE_DATABASE_CONNECTION": {
                    "CONNECTION_NOTES": "Use pyodbc.connect with appropriate connection string",
                    "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": 
                        lambda conn_str: lambda: get_db_target_engine_module('pyodbc').connect(conn_str)
                }
            }
        }

    def _get_base_connection_string(self, d: Dict[str, Any]) -> str:
        params = d["POSTGRESQL"]["DEFAULT_PARAMETERS"]
        return params["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
            params["DRIVER"],
            params["SERVER"],
            params["PORT_NUMBER"],
            params["DATABASE_NAME"],
            params["USERNAME"],
            params["PASSWORD"]
        )

    def _get_dsn_connection_string(self, d: Dict[str, Any]) -> str:
        params = d["POSTGRESQL"]["DEFAULT_PARAMETERS"]
        return params["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
            params["DSN_NAME"],
            params["USERNAME"],
            params["PASSWORD"]
        )    
class MSSQLConfig(DatabaseEngineConfig):
    """MSSQL specific configuration."""
    
    def get_connection_dict(self) -> Dict[str, Any]:
        return {
            "MSSQL": {
                "DEFAULT_PARAMETERS": {
                    "DRIVER": self.config.driver,
                    "DSN_NAME": self.config.dsn_name,
                    "DATABASE_NAME": self.config.database_name,
                    "SERVER": self.config.server,
                    "PORT_NUMBER": self.config.port_number,
                    "USERNAME": self.config.username,
                    "PASSWORD": self.config.password,
                    "FORMAT_CONNECTION_STRING": {
                        **self.format_connection_string,
                        "IS_DSN_NAME_SUPPORTED": True,
                        "BASE_CONNECTION_STRING": "DRIVER={0}; SERVER={1},{2}; DATABASE={3}; UID={4}; PWD={5};",
                        "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};"
                    }
                },
                "FINALIZED_CONNECTION_PARAMS": {
                    "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": self._get_base_connection_string,
                    "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": self._get_dsn_connection_string
                },
                "CRUDBASIC": {
                    "IMPORT": "pyodbc",
                    "PARAMETER_PLACEHOLDER": "?",
                    "IS_USERNAME_AND_PASSWORD_REQUIRED": True
                },
                "CREATE_DATABASE_CONNECTION": {
                    "CONNECTION_NOTES": "Use pyodbc.connect with appropriate connection string",
                    "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": 
                        lambda conn_str: lambda: get_db_target_engine_module('pyodbc').connect(conn_str)
                }
            }
        }

    def _get_base_connection_string(self, d: Dict[str, Any]) -> str:
        params = d["MSSQL"]["DEFAULT_PARAMETERS"]
        return params["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
            params["DRIVER"],
            params["SERVER"],
            params["PORT_NUMBER"],
            params["DATABASE_NAME"],
            params["USERNAME"],
            params["PASSWORD"]
        )

    def _get_dsn_connection_string(self, d: Dict[str, Any]) -> str:
        params = d["MSSQL"]["DEFAULT_PARAMETERS"]
        return params["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
            params["DSN_NAME"],
            params["USERNAME"],
            params["PASSWORD"]
        )

class MySQLConfig(DatabaseEngineConfig):
    """MySQL specific configuration."""
    
    def get_connection_dict(self) -> Dict[str, Any]:
        return {
            "MYSQL": {
                "DEFAULT_PARAMETERS": {
                    "DRIVER": self.config.driver,
                    "DSN_NAME": self.config.dsn_name,
                    "DATABASE_NAME": self.config.database_name,
                    "SERVER": self.config.server,
                    "PORT_NUMBER": self.config.port_number,
                    "USERNAME": self.config.username,
                    "PASSWORD": self.config.password,
                    "MULTI_HOST": 1,
                    "CHARSET": self.config.charset,
                    "FORMAT_CONNECTION_STRING": {
                        **self.format_connection_string,
                        "IS_DSN_NAME_SUPPORTED": True,
                        "BASE_CONNECTION_STRING": "DRIVER={0}; SERVER={1}; PORT={2}; DATABASE={3}; UID={4}; PWD={5}; MULTI_HOST=1; CHARSET={6};",
                        "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};"
                    }
                },
                "FINALIZED_CONNECTION_PARAMS": {
                    "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": self._get_base_connection_string,
                    "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": self._get_dsn_connection_string
                },
                "CRUDBASIC": {
                    "IMPORT": "pyodbc",
                    "PARAMETER_PLACEHOLDER": "?",
                    "IS_USERNAME_AND_PASSWORD_REQUIRED": True
                },
                "CREATE_DATABASE_CONNECTION": {
                    "CONNECTION_NOTES": "Use pyodbc.connect with appropriate connection string",
                    "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": 
                        lambda conn_str: lambda: get_db_target_engine_module('pyodbc').connect(conn_str)
                }
            }
        }

    def _get_base_connection_string(self, d: Dict[str, Any]) -> str:
        params = d["MYSQL"]["DEFAULT_PARAMETERS"]
        return params["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
            params["DRIVER"],
            params["SERVER"],
            params["PORT_NUMBER"],
            params["DATABASE_NAME"],
            params["USERNAME"],
            params["PASSWORD"],
            params["CHARSET"]
        )

    def _get_dsn_connection_string(self, d: Dict[str, Any]) -> str:
        params = d["MYSQL"]["DEFAULT_PARAMETERS"]
        return params["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
            params["DSN_NAME"],
            params["USERNAME"],
            params["PASSWORD"]
        )

class PostgreSQLConfig(DatabaseEngineConfig):
    """PostgreSQL specific configuration."""
    
    def get_connection_dict(self) -> Dict[str, Any]:
        return {
            "POSTGRESQL": {
                "DEFAULT_PARAMETERS": {
                    "DRIVER": self.config.driver,
                    "DSN_NAME": self.config.dsn_name,
                    "DATABASE_NAME": self.config.database_name,
                    "SERVER": self.config.server,
                    "PORT_NUMBER": self.config.port_number,
                    "USERNAME": self.config.username,
                    "PASSWORD": self.config.password,
                    "FORMAT_CONNECTION_STRING": {
                        **self.format_connection_string,
                        "IS_DSN_NAME_SUPPORTED": "Y",
                        "BASE_CONNECTION_STRING": "DRIVER={0}; SERVER={1}; Port={2}; DATABASE={3}; UID={4}; PWD={5};",
                        "BASE_ODBC_DSN_CONNECTION_STRING": "DSN={0};UID={1};PWD={2};"
                    }
                },
                "FINALIZED_CONNECTION_PARAMS": {
                    "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": self._get_base_connection_string,
                    "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": self._get_dsn_connection_string
                },
                "CRUDBASIC": {
                    "IMPORT": "pyodbc",
                    "PARAMETER_PLACEHOLDER": "?",
                    "IS_USERNAME_AND_PASSWORD_REQUIRED": True
                },
                "CREATE_DATABASE_CONNECTION": {
                    "CONNECTION_NOTES": "Use pyodbc.connect with appropriate connection string",
                    "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": 
                        lambda conn_str: lambda: get_db_target_engine_module('pyodbc').connect(conn_str)
                }
            }
        }

    def _get_base_connection_string(self, d: Dict[str, Any]) -> str:
        params = d["POSTGRESQL"]["DEFAULT_PARAMETERS"]
        return params["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
            params["DRIVER"],
            params["SERVER"],
            params["PORT_NUMBER"],
            params["DATABASE_NAME"],
            params["USERNAME"],
            params["PASSWORD"]
        )

    def _get_dsn_connection_string(self, d: Dict[str, Any]) -> str:
        params = d["POSTGRESQL"]["DEFAULT_PARAMETERS"]
        return params["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
            params["DSN_NAME"],
            params["USERNAME"],
            params["PASSWORD"]
        )        