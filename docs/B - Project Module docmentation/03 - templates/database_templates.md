# Database Templates Documentation

## Overview
The database templates module provides standardized configuration templates for different database engines. Each template defines the connection parameters, formatting rules, and basic CRUD operations specific to each database engine.

## Template Structure

Each database template follows this standard structure:
```python
{
    "ENGINE_NAME": {
        "DEFAULT_PARAMETERS": {
            # Default connection parameters
        },
        "FINALIZED_CONNECTION_PARAMS": {
            # Connection string formatters
        },
        "CRUDBASIC": {
            # Basic CRUD operation settings
        }
    }
}
```

### Default Parameters
Contains the default connection settings:
- DRIVER: Database driver name
- DSN_NAME: Data Source Name
- DATABASE_NAME: Default database name
- SERVER: Server hostname
- PORT_NUMBER: Server port
- FORMAT_CONNECTION_STRING: Connection string formatting rules

### Finalized Connection Parameters
Contains lambda functions for generating connection strings:
- LAMBDA_FINALIZED_BASE_CONNECTION_STRING: Direct connection string formatter
- LAMBDA_FINALIZED_DSN_CONNECTION_STRING: DSN connection string formatter

### CRUD Basic
Contains basic CRUD operation settings:
- IMPORT: Required Python module
- PARAMETER_PLACEHOLDER: SQL parameter placeholder
- IS_USERNAME_AND_PASSWORD_REQUIRED: Authentication requirement

## Supported Databases

### 1. Microsoft SQL Server (MSSQL)
```python
# Connection string example:
"DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=Northwind;"

# Features:
- Uses pyodbc
- Supports DSN connections
- Uses "?" parameter placeholder
- Requires authentication
```

### 2. PostgreSQL
```python
# Connection string example:
"host=localhost port=5432 dbname=postgres"

# Features:
- Uses psycopg2
- No DSN support
- Uses "%s" parameter placeholder
- Requires authentication
```

### 3. MySQL
```python
# Connection string example:
"DRIVER={MySQL ODBC 8.0 ANSI Driver};SERVER=localhost;PORT=3306;DATABASE=mysql;"

# Features:
- Uses pyodbc
- Supports DSN connections
- Uses "?" parameter placeholder
- Requires authentication
```

### 4. SQLite
```python
# Connection string example:
"/path/to/database/database.db"

# Features:
- Uses sqlite3
- No DSN support
- Uses "?" parameter placeholder
- No authentication required
```

### 5. DuckDB
```python
# Connection string example:
"/path/to/database/database.duckdb"

# Features:
- Uses duckdb
- No DSN support
- Uses "?" parameter placeholder
- No authentication required
```

### 6. PSYCOPG2 (PostgreSQL)
```python
# Connection string example:
"host=localhost port=5432 dbname=postgres"

# Features:
- Uses psycopg2
- No DSN support
- Uses "%s" parameter placeholder
- Requires authentication
```

## Usage Examples

### 1. Basic Template Usage
```python
from pydatabaseconnection.templates import get_template

# Get template configuration
mssql_template = get_template("MSSQL")

# Access default parameters
default_params = mssql_template["MSSQL"]["DEFAULT_PARAMETERS"]

# Create connection string
connection_string = mssql_template["MSSQL"]["FINALIZED_CONNECTION_PARAMS"][
    "LAMBDA_FINALIZED_BASE_CONNECTION_STRING"
](default_params)
```

### 2. Custom Parameters
```python
custom_params = {
    "DRIVER": "{ODBC Driver 17 for SQL Server}",
    "SERVER": "custom.server",
    "PORT_NUMBER": 1433,
    "DATABASE_NAME": "custom_db"
}

template = get_template("MSSQL")
connection_string = template["MSSQL"]["FINALIZED_CONNECTION_PARAMS"][
    "LAMBDA_FINALIZED_BASE_CONNECTION_STRING"
](custom_params)
```

### 3. DSN Connection
```python
dsn_params = {
    "DSN_NAME": "MyCustomDSN"
}

template = get_template("MSSQL")
dsn_string = template["MSSQL"]["FINALIZED_CONNECTION_PARAMS"][
    "LAMBDA_FINALIZED_DSN_CONNECTION_STRING"
](dsn_params)
```

## Template Customization

### Adding New Templates
To add a new database template:

1. Create template dictionary:
```python
NEW_DB_TEMPLATE = {
    "NEW_DB": {
        "DEFAULT_PARAMETERS": {
            # Define default parameters
        },
        "FINALIZED_CONNECTION_PARAMS": {
            # Define connection string formatters
        },
        "CRUDBASIC": {
            # Define CRUD settings
        }
    }
}
```

2. Add to TEMPLATES registry:
```python
TEMPLATES["NEW_DB"] = NEW_DB_TEMPLATE
```

### Modifying Existing Templates
To modify an existing template:

```python
template = get_template("MSSQL")
template["MSSQL"]["DEFAULT_PARAMETERS"].update({
    "PORT_NUMBER": 1435,
    "DATABASE_NAME": "custom_default_db"
})
```

## Best Practices

1. **Connection String Formatting**
   - Use parameterized strings for consistency
   - Include all required parameters
   - Handle optional parameters gracefully

2. **Security**
   - Never hardcode credentials in templates
   - Use environment variables for sensitive data
   - Always use secure connection options when available

3. **Validation**
   - Validate all parameters before use
   - Check for required driver availability
   - Verify connection string format

## Error Handling

Common template-related errors:

1. **Template Not Found**
```python
try:
    template = get_template("UNKNOWN_DB")
except KeyError as e:
    print(f"Template not found: {e}")
```

2. **Invalid Parameters**
```python
def validate_template_params(params: Dict[str, Any], template: Dict) -> bool:
    required_params = template["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"][
        "LOAD_DEFAULT_PARAMETER_KEYS"
    ]
    return all(param in params for param in required_params)
```

Would you like me to add more specific examples or elaborate on any particular aspect of the templates?