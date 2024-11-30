from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, Union
from datetime import datetime
import pandas as pd
from getpass import getpass
import os
from pathlib import Path
from .exceptions import CredentialsError, ValidationError
from src.db_templates.database_target_engine_modules_enum_contraints import (
    ChangeDefaultUsernameAndPassword,
    TargetDatabaseConnectionStringOption,
    TargetDatabaseEngine,
)
import src.db_templates.database_target_engine_template_modules as template


class BaseDescriptor(ABC):
    """Base descriptor for all database connection attributes."""

    def __init__(self, name: str):
        self.name = name
        self.private_name = f"_{name}"

    @abstractmethod
    def __get__(self, instance: Any, owner: Type[Any]) -> Any:
        pass

    @abstractmethod
    def __set__(self, instance: Any, value: Any) -> None:
        pass

    def __delete__(self, instance: Any) -> None:
        """Remove attribute if it exists."""
        if hasattr(instance, self.private_name):
            delattr(instance, self.private_name)


class ConnectionParametersDescriptor(BaseDescriptor):
    """
    Manages database connection parameters.

    Handles the storage and validation of connection parameters
    like host, port, database name, etc.
    """

    def __get__(
        self, instance: Any, owner: Type[Any]
    ) -> Union[Dict[str, Any], "ConnectionParametersDescriptor"]:
        """Get current connection parameters."""
        if instance is None:
            return self
        return getattr(instance, self.private_name, {})

    def __set__(self, instance: Any, value: Dict[str, Any]) -> None:
        """
        Set connection parameters with validation.

        Args:
            value: Dictionary of connection parameters

        Raises:
            ValidationError: If parameters format is invalid
        """
        if not isinstance(value, dict):
            raise ValidationError("Parameters must be a dictionary")

        # Store parameters
        setattr(instance, self.private_name, value.copy())


class QueryResultDescriptor(BaseDescriptor):
    """
    Manages database query results with DataFrame support.

    Handles the storage and conversion of query results to pandas DataFrame,
    supporting both direct DataFrame assignment and list conversion.
    """

    def __get__(
        self, instance: Any, owner: Type[Any]
    ) -> Union[Optional[pd.DataFrame], "QueryResultDescriptor"]:
        """Get query results as DataFrame."""
        if instance is None:
            return self
        return getattr(instance, self.private_name, None)

    def __set__(self, instance: Any, value: Union[pd.DataFrame, list]) -> None:
        """
        Set query results, converting to DataFrame if needed.

        Args:
            value: DataFrame or list of records

        Raises:
            TypeError: If value cannot be converted to DataFrame
        """
        if isinstance(value, list):
            value = pd.DataFrame(value)
        elif not isinstance(value, pd.DataFrame):
            raise TypeError("Query results must be DataFrame or list")

        setattr(instance, self.private_name, value)


class EngineConfigDescriptor(BaseDescriptor):
    """
    Manages database engine configuration.

    Handles the storage and access of engine-specific configuration
    loaded from templates.
    """

    def __get__(
        self, instance: Any, owner: Type[Any]
    ) -> Union[Dict[str, Any], "EngineConfigDescriptor"]:
        """Get engine configuration."""
        if instance is None:
            return self
        return getattr(instance, self.private_name, {})

    def __set__(self, instance: Any, value: Dict[str, Any]) -> None:
        """
        Set engine configuration.

        Args:
            value: Dictionary of engine configuration

        Raises:
            ValidationError: If configuration format is invalid
        """
        if not isinstance(value, dict):
            raise ValidationError("Engine configuration must be a dictionary")

        setattr(instance, self.private_name, value.copy())


class ParameterDescriptor(BaseDescriptor):
    """Descriptor for database connection parameters."""

    def __get__(self, instance: Any, owner: Type[Any]) -> Any:
        if instance is None:
            return self
        # Get parameter from customized params, fallback to defaults
        return instance._get_connection_param(
            self.name,
            instance._customized_target_parameters,
            instance._default_target_parameters,
        )

    def __set__(self, instance: Any, value: Any) -> None:
        # Store parameter in customized parameters
        instance._customized_target_parameters[self.name] = value


class CredentialsDescriptor(BaseDescriptor):
    """Descriptor for database credentials."""

    def __get__(
        self, instance: Any, owner: Type[Any]
    ) -> Union[Dict[str, Any], "CredentialsDescriptor"]:
        if instance is None:
            return self
        if not hasattr(instance, self.private_name):
            # Initialize default credentials
            setattr(
                instance,
                self.private_name,
                {
                    "username": None,
                    "password": None,
                    "is_default": True,
                    "requires_auth": True,
                },
            )
        return getattr(instance, self.private_name)

    def __set__(self, instance: Any, value: Dict[str, Any]) -> None:
        if not isinstance(value, dict):
            raise ValueError("Credentials must be a dictionary")
        if not all(k in value for k in ("username", "password")):
            raise ValueError("Credentials must contain 'username' and 'password'")
        setattr(instance, self.private_name, value)


class PandaDataFrameDescriptor(BaseDescriptor):
    """Descriptor for pandas DataFrame results."""

    def __get__(
        self, instance: Any, owner: Type[Any]
    ) -> Union[pd.DataFrame, "PandaDataFrameDescriptor"]:
        if instance is None:
            return self
        if not hasattr(instance, self.private_name):
            raise AttributeError(f"No DataFrame available for '{self.name}'")
        return getattr(instance, self.private_name)

    def __set__(self, instance: Any, value: pd.DataFrame) -> None:
        if not isinstance(value, pd.DataFrame):
            raise TypeError(f"'{self.name}' must be a pandas DataFrame")
        setattr(instance, self.private_name, value)


from src.db_templates.database_target_engine_modules_enum_contraints import (
    ChangeDefaultUsernameAndPassword,
)


class ConnectionManager:
    """Handles database connection credentials and environment settings."""

    def _load_environment(self) -> None:
        """Load environment variables from file."""
        env_path = Path(self.env_file)
        if env_path.exists():
            # Load environment variables from file
            for line in env_path.read_text().splitlines():
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

    def __init__(self, env_file: Optional[str] = None):
        self.env_file = env_file or os.getenv("DEFAULT_KEY_MANAGEMENT_ENV_FILE", ".env")
        # Initialize with default credentials
        self._credentials = {
            "username": None,
            "password": None,
            "is_default": True,
            "requires_auth": True,
        }
        self._load_environment()

    def set_credentials(self, show_password: bool = False) -> Dict[str, str]:
        """Set database credentials via user input."""
        username = input("Enter username: ").strip()
        if show_password:
            password = input("Enter password: ").strip()
        else:
            password = getpass("Enter password: ").strip()

        self._credentials.update(
            {
                "username": username,
                "password": password,
                "is_default": False,
                "requires_auth": True,
            }
        )
        return self._credentials

    def get_credentials(self) -> Dict[str, str]:
        return self._credentials

    @property
    def username(self) -> Optional[str]:
        """Get current username."""
        return self._credentials["username"]

    @property
    def password(self) -> Optional[str]:
        """Get current password."""
        return self._credentials["password"]  # Fixed: was returning username
