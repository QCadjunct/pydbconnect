# ⚙️ Advanced Configuration Examples

## Table of Contents

- [Engine Configurations](#engine-config)
- [Custom Configurations](#custom-config)
- [Security Considerations](#security)
- [Environmental Setup](#env-setup)

<a name="engine-config"></a>

## 🔧 Engine Configurations [↑](#table-of-contents)

### MSSQL Advanced Configuration

```python
# Advanced MSSQL Configuration Example
db = DatabaseConnector(
    target_database_engine=TargetDatabaseEngine.MSSQL,
    target_database_engine_connect_option=TargetDatabaseConnectionStringOption.CustomizeFormatAndDefaultUserPwd
)

# Extended Parameter Configuration
db.finalization_of_connection_parameters(
    DRIVER="{ODBC Driver 17 for SQL Server}",
    SERVER="127.0.0.1",
    PORT_NUMBER=13001,
    DATABASE_NAME="AdventureWorks2019",
    ENCRYPT="yes",
    TRUST_SERVER_CERTIFICATE="yes",
    CONNECTION_TIMEOUT=30,
    PACKET_SIZE=4096
)
```

### Multi-Engine Template Example

```python
# Engine-specific configurations
ENGINE_CONFIGS = {
    "MSSQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{ODBC Driver 17 for SQL Server}",
            "SERVER": "localhost",
            "PORT_NUMBER": 13001,
            "DATABASE_NAME": "AdventureWorks2019",
            "ENCRYPT": "yes",
            "TRUST_SERVER_CERTIFICATE": "yes"
        }
    },
    "POSTGRESQL": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "{PostgreSQL ANSI}",
            "SERVER": "localhost",
            "PORT_NUMBER": 5432,
            "DATABASE_NAME": "postgres",
            "SSL_MODE": "require"
        }
    }
}
```

<a name="custom-config"></a>

## 🛠️ Custom Configurations [↑](#table-of-contents)

### Custom Connection String Builder

```python
def build_custom_connection_string(
    self,
    template: str,
    params: Dict[str, Any],
    **kwargs
) -> str:
    """Build a custom connection string using template."""
    try:
        # Base parameters
        connection_params = {
            "DRIVER": params.get("DRIVER", self.default_driver),
            "SERVER": f"{params['SERVER']},{params['PORT_NUMBER']}",
            "DATABASE": params["DATABASE_NAME"],
        }
        
        # Add authentication if required
        if self.requires_auth:
            connection_params.update({
                "UID": params["USERNAME"],
                "PWD": params["PASSWORD"]
            })
            
        # Add custom parameters
        connection_params.update(kwargs)
        
        # Build string from template
        return template.format(**connection_params)
        
    except KeyError as e:
        raise DatabaseError(f"Missing required parameter: {e}")
```

### Usage Example

```python
# Custom connection with specific requirements
custom_conn = db.finalization_of_connection_parameters(
    DRIVER="{SQL Server}",
    SERVER="custom-server",
    PORT_NUMBER=1433,
    DATABASE_NAME="custom-db",
    ENCRYPT="yes",
    APP_NAME="CustomApp",
    WORKSTATION_ID="WORK1"
)
```

<a name="security"></a>

## 🔒 Security Considerations [↑](#table-of-contents)

### Credential Management

```python
class SecureCredentialManager:
    """Secure credential management."""
    
    @staticmethod
    def encrypt_credentials(username: str, password: str) -> Dict[str, str]:
        """Encrypt credentials for storage."""
        # Implementation using cryptography library
        pass
    
    @staticmethod
    def decrypt_credentials(encrypted_data: Dict[str, str]) -> Tuple[str, str]:
        """Decrypt stored credentials."""
        # Implementation using cryptography library
        pass

# Usage in connector
def _secure_credentials(self):
    """Secure credential handling."""
    if self._credentials["is_default"]:
        encrypted = SecureCredentialManager.encrypt_credentials(
            self._credentials["username"],
            self._credentials["password"]
        )
        # Store securely
```

### Connection Security

```python
def _configure_connection_security(self):
    """Configure connection security options."""
    security_params = {
        "ENCRYPT": "yes",
        "TRUST_SERVER_CERTIFICATE": "no",
        "SSL_MODE": "verify-full",
        "SSL_CERT_FILE": "path/to/cert.pem"
    }
    
    # Update connection parameters
    self._connection_params.update(security_params)
```

<a name="env-setup"></a>

## 🌍 Environmental Setup [↑](#table-of-contents)

### Advanced Environment Configuration

```python
# .env configuration with extended options
MSSQL_USERNAME=sa
MSSQL_PASSWORD=YourPassword
MSSQL_DEFAULT_DRIVER={ODBC Driver 17 for SQL Server}
MSSQL_ENCRYPT=yes
MSSQL_TRUST_SERVER_CERT=no
MSSQL_CONN_TIMEOUT=30
MSSQL_APP_NAME=MyApp
MSSQL_WORKSTATION_ID=DESKTOP1
```

### Configuration Loading

```python
def load_advanced_configuration(self):
    """Load advanced configuration from environment."""
    config = {
        "basic": {
            "username": os.getenv(f"{self.engine_name}_USERNAME"),
            "password": os.getenv(f"{self.engine_name}_PASSWORD")
        },
        "connection": {
            "driver": os.getenv(f"{self.engine_name}_DEFAULT_DRIVER"),
            "encrypt": os.getenv(f"{self.engine_name}_ENCRYPT"),
            "trust_cert": os.getenv(f"{self.engine_name}_TRUST_SERVER_CERT")
        },
        "timeout": {
            "connection": int(os.getenv(f"{self.engine_name}_CONN_TIMEOUT", "30")),
            "command": int(os.getenv(f"{self.engine_name}_CMD_TIMEOUT", "30"))
        },
        "application": {
            "name": os.getenv(f"{self.engine_name}_APP_NAME"),
            "workstation": os.getenv(f"{self.engine_name}_WORKSTATION_ID")
        }
    }
    return config
```
