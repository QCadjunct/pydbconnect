# pydatabaseconnection/db_constants/TemplateNewTargetDatabaseEngine.py
from typing import Any, Dict, Optional
from dataclasses import dataclass

@dataclass
class NewDatabaseEngineConfig:
    """
    Template configuration for new database engine.
    Replace 'NewDatabaseEngine' with your engine name.
    """
    # Required parameters
    driver: str
    database_name: str
    server: str = "localhost"
    port: int = 0
    
    # Optional parameters
    dsn_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    charset: str = "utf8"
    timeout: int = 30
    
    # Additional custom parameters
    custom_params: Dict[str, Any] = None

class NewDatabaseEngineTemplate:
    """
    Template class for adding a new database engine.
    
    Steps to use this template:
    1. Copy this file and rename it to your database engine name
    2. Replace all occurrences of 'NewDatabaseEngine' with your engine name
    3. Modify the configuration parameters and connection string formats
    4. Implement the required methods
    5. Add your engine to the main database_connection_constants.py
    """

    def __init__(self, config: NewDatabaseEngineConfig):
        """Initialize with your engine's configuration."""
        self.config = config
        self.engine_name = "NEW_DATABASE_ENGINE"  # Replace with your engine name

    def get_connection_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate the standardized connection dictionary.
        
        Structure follows the pattern used by other database engines:
        - DEFAULT_PARAMETERS: Basic connection parameters
        - FORMAT_CONNECTION_STRING: Connection string formatting rules
        - FINALIZED_CONNECTION_PARAMS: Connection string generators
        - CRUDBASIC: Basic CRUD operation settings
        - CREATE_DATABASE_CONNECTION: Connection creation handlers
        """
        return {
            self.engine_name: {
                "DEFAULT_PARAMETERS": {
                    "DRIVER": self.config.driver,
                    "DSN_NAME": self.config.dsn_name,
                    "DATABASE_NAME": self.config.database_name,
                    "SERVER": self.config.server,
                    "PORT_NUMBER": self.config.port,
                    "USERNAME": self.config.username,
                    "PASSWORD": self.config.password,
                    "CHARSET": self.config.charset,
                    "TIMEOUT": self.config.timeout,
                    "FORMAT_CONNECTION_STRING": {
                        "LOAD_DEFAULT_PARAMETER_KEYS": [
                            "DRIVER",
                            "DSN_NAME",
                            "DATABASE_NAME",
                            "SERVER",
                            "PORT_NUMBER"
                        ],
                        "LOAD_DSN_PARAMETER_KEYS": ["DSN", "UID", "PWD"],
                        "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": self._load_default_parameters,
                        "METHOD_LOAD_DSN_PARAMETER_KEYS_DICT": self._load_dsn_parameters,
                        "IS_DSN_NAME_SUPPORTED": True,  # Set to False if DSN is not supported
                        "BASE_CONNECTION_STRING": self._get_base_connection_string_template(),
                        "BASE_ODBC_DSN_CONNECTION_STRING": self._get_dsn_connection_string_template()
                    }
                },
                "FINALIZED_CONNECTION_PARAMS": {
                    "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": self._build_base_connection_string,
                    "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": self._build_dsn_connection_string
                },
                "CRUDBASIC": {
                    "IMPORT": "your_driver_module",  # e.g., pyodbc, psycopg2
                    "PARAMETER_PLACEHOLDER": "?",  # or "%s" for some engines
                    "IS_USERNAME_AND_PASSWORD_REQUIRED": True
                },
                "CREATE_DATABASE_CONNECTION": {
                    "CONNECTION_NOTES": "Documentation for your database engine connection",
                    "TARGET_ENGINE_MODULE_IMPORT": "your_driver_module",
                    "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": self._create_connection
                }
            }
        }

    def _get_base_connection_string_template(self) -> str:
        """
        Define your base connection string template.
        
        Example formats:
        ODBC: "DRIVER={0}; SERVER={1}; PORT={2}; DATABASE={3}; UID={4}; PWD={5};"
        URL: "protocol://username:password@host:port/database"
        """
        return "DRIVER={0}; SERVER={1}; PORT={2}; DATABASE={3}; UID={4}; PWD={5};"

    def _get_dsn_connection_string_template(self) -> str:
        """Define your DSN connection string template."""
        return "DSN={0};UID={1};PWD={2};"

    def _load_default_parameters(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Load default parameters excluding sensitive data."""
        keys = d[self.engine_name]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["LOAD_DEFAULT_PARAMETER_KEYS"]
        return {
            key: d[self.engine_name]["DEFAULT_PARAMETERS"][key]
            for key in [k for k in keys if k not in ["USERNAME", "PASSWORD"]]
        }

    def _load_dsn_parameters(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Load DSN parameters excluding sensitive data."""
        keys = d[self.engine_name]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["LOAD_DSN_PARAMETER_KEYS"]
        return {
            key: d[self.engine_name]["DEFAULT_PARAMETERS"][key]
            for key in [k for k in keys if k not in ["UID", "PWD"]]
        }

    def _build_base_connection_string(self, d: Dict[str, Any]) -> str:
        """Build the base connection string."""
        params = d[self.engine_name]["DEFAULT_PARAMETERS"]
        return params["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
            params["DRIVER"],
            params["SERVER"],
            params["PORT_NUMBER"],
            params["DATABASE_NAME"],
            params["USERNAME"],
            params["PASSWORD"]
        )

    def _build_dsn_connection_string(self, d: Dict[str, Any]) -> str:
        """Build the DSN connection string."""
        params = d[self.engine_name]["DEFAULT_PARAMETERS"]
        return params["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
            params["DSN_NAME"],
            params["USERNAME"],
            params["PASSWORD"]
        )

    def _create_connection(self, connection_string: str) -> callable:
        """Create the database connection function."""
        def connect():
            import importlib
            module = importlib.import_module(
                self.get_connection_dict()[self.engine_name]["CRUDBASIC"]["IMPORT"]
            )
            return module.connect(connection_string)
        return connect

# Usage Example:
"""
# 1. Create configuration
config = NewDatabaseEngineConfig(
    driver="YourDriver",
    database_name="YourDB",
    server="localhost",
    port=1234,
    username="user",
    password="pass"
)

# 2. Initialize template
engine = NewDatabaseEngineTemplate(config)

# 3. Get connection dictionary
connection_dict = engine.get_connection_dict()

# 4. Use in your database connection code
connection_string = connection_dict["NEW_DATABASE_ENGINE"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](connection_dict)
"""