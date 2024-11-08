from typing import Dict, Any, Optional, TypeVar, Type
from pathlib import Path
import importlib
from ..types.exceptions import DatabaseConfigError, TemplateError
from ..types.connection_types import (
    ConnectionParams, 
    DatabaseTemplate, 
    TemplateConfig,
    ConnectionStringBuilder
)

T = TypeVar('T', bound='TemplateManager')

class TemplateManager:
    """
    Manages database engine templates and configurations.
    Implements singleton pattern to ensure consistent template management.
    """
    _instance = None
    _templates: Dict[str, DatabaseTemplate] = {}
    _builders: Dict[str, ConnectionStringBuilder] = {}
    _initialized = False

    def __new__(cls: Type[T]) -> T:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._load_default_templates()

    def _load_default_templates(self) -> None:
        """Load all default database templates"""
        try:
            from ..config.templates import (
                MSSQL, POSTGRESQL, MYSQL, 
                SQLITE3, DUCKDB, PSYCOPG2
            )
            
            # Register default templates
            self.register_template("MSSQL", MSSQL)
            self.register_template("POSTGRESQL", POSTGRESQL)
            self.register_template("MYSQL", MYSQL)
            self.register_template("SQLITE3", SQLITE3)
            self.register_template("DUCKDB", DUCKDB)
            self.register_template("PSYCOPG2", PSYCOPG2)
            
        except ImportError as e:
            raise TemplateError(f"Failed to load default templates: {str(e)}")

    def register_template(self, name: str, config: Dict[str, Any]) -> None:
        """
        Register a new database template.

        Args:
            name: Template name (e.g., "MSSQL")
            config: Template configuration dictionary

        Raises:
            TemplateError: If template configuration is invalid
        """
        try:
            if name not in config:
                raise TemplateError(f"Invalid template structure for {name}")
                
            template_config = config[name]
            
            # Create and store template
            self._templates[name] = DatabaseTemplate(
                name=name,
                module_name=template_config["CRUDBASIC"]["IMPORT"],
                requires_auth=template_config["CRUDBASIC"]["IS_USERNAME_AND_PASSWORD_REQUIRED"],
                supports_dsn=template_config["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["IS_DSN_NAME_SUPPORTED"],
                default_params=template_config["DEFAULT_PARAMETERS"],
                connection_format=template_config["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]
            )
            
            # Create and store connection string builder
            self._builders[name] = self._create_builder(template_config)
            
        except KeyError as e:
            raise TemplateError(f"Missing required configuration key for {name}: {str(e)}")
        except Exception as e:
            raise TemplateError(f"Failed to register template {name}: {str(e)}")

    def _create_builder(self, config: Dict[str, Any]) -> ConnectionStringBuilder:
        """Create connection string builder from template configuration"""
        base_format = config["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]
        
        class Builder(ConnectionStringBuilder):
            def build_connection_string(self, params: Dict[str, Any]) -> str:
                # Format base connection string
                if "BASE_CONNECTION_STRING" in base_format:
                    return base_format["BASE_CONNECTION_STRING"].format(**params)
                return ""

            def build_dsn_string(self, params: Dict[str, Any]) -> str:
                # Format DSN connection string
                if "BASE_ODBC_DSN_CONNECTION_STRING" in base_format:
                    return base_format["BASE_ODBC_DSN_CONNECTION_STRING"].format(**params)
                return ""
                
        return Builder()

    def get_template(self, name: str) -> DatabaseTemplate:
        """
        Get a registered database template.

        Args:
            name: Template name to retrieve

        Returns:
            DatabaseTemplate: The requested template

        Raises:
            TemplateError: If template not found
        """
        if name not in self._templates:
            raise TemplateError(f"Template not found: {name}")
        return self._templates[name]

    def get_connection_string(self, name: str, params: Dict[str, Any], use_dsn: bool = False) -> str:
        """
        Build connection string for specified template.

        Args:
            name: Template name
            params: Connection parameters
            use_dsn: Whether to use DSN connection string

        Returns:
            str: Formatted connection string

        Raises:
            TemplateError: If builder not found or connection string generation fails
        """
        if name not in self._builders:
            raise TemplateError(f"No connection string builder found for {name}")
            
        builder = self._builders[name]
        try:
            if use_dsn:
                return builder.build_dsn_string(params)
            return builder.build_connection_string(params)
        except Exception as e:
            raise TemplateError(f"Failed to build connection string: {str(e)}")

    def import_db_module(self, name: str) -> Any:
        """
        Import database module for specified template.

        Args:
            name: Template name

        Returns:
            Any: Imported database module

        Raises:
            TemplateError: If module import fails
        """
        template = self.get_template(name)
        try:
            return importlib.import_module(template.module_name)
        except ImportError as e:
            raise TemplateError(f"Failed to import module {template.module_name}: {str(e)}")

    def validate_params(self, name: str, params: Dict[str, Any]) -> None:
        """
        Validate connection parameters against template requirements.

        Args:
            name: Template name
            params: Parameters to validate

        Raises:
            TemplateError: If parameters are invalid
        """
        template = self.get_template(name)
        required_params = set(template.default_params.get("LOAD_DEFAULT_PARAMETER_KEYS", []))
        
        missing_params = required_params - set(params.keys())
        if missing_params:
            raise TemplateError(f"Missing required parameters for {name}: {missing_params}")

    def get_parameter_placeholder(self, name: str) -> str:
        """Get SQL parameter placeholder for template"""
        template = self.get_template(name)
        return template.get_crudbasic_config().get("PARAMETER_PLACEHOLDER", "?")

    def requires_authentication(self, name: str) -> bool:
        """Check if template requires authentication"""
        template = self.get_template(name)
        return template.requires_auth

    def supports_dsn(self, name: str) -> bool:
        """Check if template supports DSN connections"""
        template = self.get_template(name)
        return template.supports_dsn