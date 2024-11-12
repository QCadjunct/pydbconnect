# Database Connection Constants for pydbconnect

This module provides enums for database connection configuration in pydbconnect.

## TargetDatabaseEngine

Defines supported database engines with built-in validation and configuration.

```python
from pydbconnect.enum_connection_constants import TargetDatabaseEngine

# Create engine instance
engine = TargetDatabaseEngine.MSSQL

# Check authentication requirement
if engine.requires_authentication:
    # Handle credentials
    
# Check DSN support
if engine.supports_dsn:
    # Use DSN connection
    
# Get required module
module_name = engine.import_module
```

### Properties
- `requires_authentication`: Whether engine needs username/password
- `supports_dsn`: Whether engine supports DSN connections
- `import_module`: Required Python module name

## TargetDatabaseConnectionStringOption

Defines connection string options with validation.

```python
from pydbconnect.enum_connection_constants import TargetDatabaseConnectionStringOption

# Create option instance
option = TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd

# Validate with engine
if option.validate_for_engine(engine):
    # Use option
else:
    # Handle incompatibility
```

### Properties
- `uses_dsn`: Whether option uses DSN connection
- `changes_credentials`: Whether option requires credential changes
- `uses_custom_format`: Whether option uses custom connection string format

## Error Handling

```python
try:
    if not option.validate_for_engine(engine):
        raise InvalidConnectionOptionError(engine, option)
except InvalidConnectionOptionError as e:
    print(f"Error: {e}")
```

## Example Usage

```python
from pydbconnect.enum_connection_constants import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption
)

# Setup connection
engine = TargetDatabaseEngine.MSSQL
option = TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd

# Validate compatibility
if not engine.validate_connection_option(option):
    raise InvalidConnectionOptionError(engine, option)

# Use in database connection
db = DatabaseConnection(engine, option)
```

## Notes
- Always validate connection options against engine before use
- Handle InvalidConnectionOptionError for incompatible combinations
- Check authentication and DSN requirements before connecting