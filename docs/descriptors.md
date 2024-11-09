# Python Database Descriptors Documentation

## Table of Contents
1. [Overview](#overview)
2. [Descriptor Types](#descriptor-types)
3. [Base Descriptor](#base-descriptor)
4. [Type-Specific Descriptors](#type-specific-descriptors)
5. [Credential Management](#credential-management)
6. [Practical Examples](#practical-examples)

## Overview

The descriptors module provides a strongly-typed system for managing database connection attributes and parameters, ensuring type safety and proper encapsulation.

### Key Features
- Type enforcement for database parameters
- Secure credential management
- Environment variable integration
- Pandas DataFrame handling

## Base Descriptor

The `BaseDescriptor` class provides the foundation for all descriptor implementations:

```python
from abc import ABC, abstractmethod
from typing import Any, Type

class BaseDescriptor(ABC):
    def __init__(self, name: str):
        self.name: str = name

    @abstractmethod
    def __get__(self, instance: Any, owner: Type[Any]) -> Any:
        pass

    @abstractmethod
    def __set__(self, instance: Any, value: Any) -> None:
        pass
```

### Usage Example:
```python
# Creating a custom descriptor
class PortDescriptor(BaseDescriptor):
    def __get__(self, instance: Any, owner: Type[Any]) -> int:
        if instance is None:
            return self
        return instance._port

    def __set__(self, instance: Any, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError("Port must be a positive integer")
        instance._port = value
```

## Type-Specific Descriptors

### 1. Dictionary Descriptor

The `DictionaryDescriptor` ensures dictionary-type values:

```python
class DBConfig:
    parameters = DictionaryDescriptor("parameters")

# Usage
config = DBConfig()
config.parameters = {"host": "localhost", "port": 5432}  # Valid
try:
    config.parameters = "invalid"  # Raises ValueError
except ValueError as e:
    print(f"Error: {e}")
```

### 2. String Descriptor

For string validation:

```python
class DatabaseConnection:
    host = StringDescriptor("host")
    database = StringDescriptor("database")

# Usage example
db = DatabaseConnection()
db.host = "localhost"      # Valid
db.database = "users_db"   # Valid

try:
    db.host = 123  # Raises ValueError
except ValueError as e:
    print(f"Error: {e}")
```

### 3. Number Descriptor

For numeric parameters:

```python
class ServerConfig:
    port = NumberDescriptor("port")
    timeout = NumberDescriptor("timeout")

# Usage
server = ServerConfig()
server.port = 5432        # Valid
server.timeout = 30.5     # Valid

try:
    server.port = "5432"  # Raises ValueError
except ValueError as e:
    print(f"Error: {e}")
```

## Credential Management

The `CredentialsDescriptor` provides secure credential handling:

```python
class DatabaseAuth:
    credentials = CredentialsDescriptor("db_credentials")

    def connect(self):
        creds = self.credentials
        if creds["is_default"]:
            print("Using default credentials")
        return connect_db(
            username=creds["username"],
            password=creds["password"]
        )

# Usage with environment variables
import os
os.environ["DB_USERNAME"] = "admin"
os.environ["DB_PASSWORD"] = "secure_pass"

db = DatabaseAuth()
db.credentials = {
    "username": os.getenv("DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD"),
    "is_default": False
}
```

## Practical Examples

### 1. Complete Database Configuration

```python
class DatabaseConfig:
    connection_params = DictionaryDescriptor("connection_params")
    credentials = CredentialsDescriptor("credentials")
    max_connections = NumberDescriptor("max_connections")
    database_name = StringDescriptor("database_name")

    def __init__(self):
        self.connection_params = {
            "host": "localhost",
            "port": 5432,
            "timeout": 30
        }
        self.max_connections = 100
        self.database_name = "myapp_db"

# Usage
config = DatabaseConfig()

# Modify connection parameters
config.connection_params.update({
    "host": "db.example.com",
    "port": 5433
})

# Set credentials
config.credentials = {
    "username": "app_user",
    "password": "secret",
    "is_default": False
}
```

### 2. Environment Variable Integration

```python
class EnvConfig:
    def __init__(self):
        self.key_management = KeyManagementEnvironmentVariablesSettings()
        self.key_management.load_env()

    def setup_from_env(self, env_file: str = '.env'):
        """Load configuration from environment file"""
        self.key_management.load_env_from_file(env_file)
        return self

# Usage with .env file
"""
# .env file content:
POSTGRES_USERNAME=admin
POSTGRES_PASSWORD=secret
"""

config = EnvConfig()
config.setup_from_env()
```

### 3. Pandas DataFrame Handling

```python
class DataAnalysis:
    results = PandaDataFrameDescriptor("results")

    def load_data(self, data: pd.DataFrame):
        self.results = data

    def process(self):
        if self.results is not None:
            return self.results.describe()

# Usage
analysis = DataAnalysis()
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
analysis.load_data(df)

try:
    analysis.results = [1, 2, 3]  # Raises TypeError
except TypeError as e:
    print(f"Error: {e}")
```

### 4. Security Best Practices

```python
class SecureConnection:
    credentials = CredentialsDescriptor("credentials")
    
    def __init__(self):
        self._key_management = KeyManagementEnvironmentVariablesSettings()
        self._key_management.load_env()

    def prompt_credentials(self, show_password: bool = False):
        """Securely prompt for credentials"""
        return self._key_management._set_credentials(show_password)

    def validate_credentials(self):
        """Validate stored credentials"""
        return self._key_management._get_credentials()

# Usage
connection = SecureConnection()
connection.prompt_credentials(show_password=False)
connection.validate_credentials()
```

## Best Practices

1. **Type Safety**
   ```python
   # Always use appropriate descriptors for type safety
   class DBConfig:
       port = NumberDescriptor("port")
       host = StringDescriptor("host")
       params = DictionaryDescriptor("params")
   ```

2. **Credential Security**
   ```python
   # Never hardcode credentials
   class SecureDB:
       def __init__(self):
           self.key_management = KeyManagementEnvironmentVariablesSettings()
           self.key_management.load_env()
   ```

3. **Error Handling**
   ```python
   try:
       config.set_port("invalid")
   except ValueError as e:
       logging.error(f"Configuration error: {e}")
       # Handle error appropriately
   ```

Would you like me to expand on any particular section or add more specific examples?