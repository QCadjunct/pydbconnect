# Template Manager Documentation

## Overview

The `TemplateManager` class is a central component of the database connection framework that manages database engine templates and configurations. It implements the singleton pattern to ensure consistent template management across the application.

## Core Features

1. Template Management
   - Loading default templates
   - Registering custom templates
   - Template validation
   - Connection string building

2. Module Management
   - Dynamic module importing
   - Module validation
   - Error handling

3. Parameter Management
   - Parameter validation
   - Default parameter handling
   - DSN support checking

## Usage Examples

### Basic Template Usage
```python
# Get template manager instance
manager = TemplateManager()

# Get template for specific database
template = manager.get_template("MSSQL")

# Build connection string
conn_string = manager.get_connection_string(
    "MSSQL",
    {
        "SERVER": "localhost",
        "PORT_NUMBER": 1433,
        "DATABASE_NAME": "master"
    }
)
```

### Custom Template Registration
```python
# Register custom template
custom_template = {
    "CUSTOM_DB": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "Custom Driver",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DRIVER", "SERVER"],
                "IS_DSN_NAME_SUPPORTED": False,
                "BASE_CONNECTION_STRING": "DRIVER={DRIVER};SERVER={SERVER}"
            }
        },
        "CRUDBASIC": {
            "IMPORT": "custom_module",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        }
    }
}

manager.register_template("CUSTOM_DB", custom_template)
```

## Template Structure

### Required Components

1. **DEFAULT_PARAMETERS**
   - Basic connection parameters
   - Connection string format settings
   - Parameter key definitions

2. **CRUDBASIC**
   - Module import information
   - Authentication requirements
   - Parameter placeholder style

3. **FORMAT_CONNECTION_STRING**
   - Base connection string format
   - DSN connection string format
   - Required parameter keys

### Example Template Structure
```python
{
    "TEMPLATE_NAME": {
        "DEFAULT_PARAMETERS": {
            "DRIVER": "...",
            "DSN_NAME": "...",
            "DATABASE_NAME": "...",
            "SERVER": "...",
            "PORT_NUMBER": 1234,
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": [...],
                "IS_DSN_NAME_SUPPORTED": True/False,
                "BASE_CONNECTION_STRING": "...",
                "BASE_ODBC_DSN_CONNECTION_STRING": "..."
            }
        },
        "CRUDBASIC": {
            "IMPORT": "module_name",
            "PARAMETER_PLACEHOLDER": "?",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True/False
        }
    }
}
```

## Error Handling

### Template Errors
```python
try:
    template = manager.get_template("UNKNOWN_DB")
except TemplateError as e:
    print(f"Template error: {e}")
```

### Parameter Validation
```python
try:
    manager.validate_params("MSSQL", {"SERVER": "localhost"})
except TemplateError as e:
    print(f"Parameter validation error: {e}")
```

## Best Practices

1. **Template Registration**
   - Register templates early in application startup
   - Validate templates before registration
   - Handle registration errors appropriately

2. **Parameter Management**
   - Always validate parameters before use
   - Provide all required parameters
   - Handle missing parameters gracefully

3. **Module Handling**
   - Check module availability before use
   - Handle import errors appropriately
   - Verify module compatibility

4. **Connection String Building**
   - Validate all required parameters
   - Handle DSN and non-DSN cases
   - Sanitize connection parameters

## Advanced Features

### Custom Connection String Builders
```python
class CustomBuilder(ConnectionStringBuilder):
    def build_connection_string(self, params: Dict[str, Any]) -> str:
        # Custom connection string building logic
        return "..."

    def build_dsn_string(self, params: Dict[str, Any]) -> str:
        # Custom DSN string building logic
        return "..."

# Register custom builder
manager._builders["CUSTOM_DB"] = CustomBuilder()
```

### Template Validation
```python
def validate_template(template: Dict[str, Any]) -> bool:
    """Validate template structure"""
    required_keys = {
        "DEFAULT_PARAMETERS",
        "CRUDBASIC",
        "FORMAT_CONNECTION_STRING"
    }
    
    if not all(key in template for key in required_keys):
        return False
        
    # Additional validation logic
    return True
```

## Common Issues and Solutions

1. **Missing Parameters**
   - Always check template requirements
   - Provide default values where appropriate
   - Validate parameters before use

2. **Module Import Failures**
   - Verify module installation
   - Check module compatibility
   - Handle import errors gracefully

3. **Connection String Errors**
   - Validate parameter types
   - Check format string compatibility
   - Handle special characters properly

Would you like me to add more specific examples or elaborate on any particular aspect?