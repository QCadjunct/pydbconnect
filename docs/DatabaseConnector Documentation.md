# 📚 DatabaseConnector Implementation Guide

## Table of Contents

- [🎯 Core Setup](#core-setup)
- [🏗️ Class Initialization](#class-init)
- [🔌 Connection Management](#connection-mgmt)
- [📋 Query Execution](#query-exec)
- [🧪 Working Example](#example)
- [🔄 Design Patterns Used](#patterns)

<a name="core-setup"></a>

## 🎯 Core Setup [↑](#table-of-contents)

### Exception Hierarchy

```python
class DatabaseError(Exception):
    """Base exception for database operations."""
    pass

class ConnectionError(DatabaseError):
    """Connection failure errors."""
    pass

class CredentialsError(DatabaseError):
    """Credential-related issues."""
    pass
```

> 🔑 **Key Point**: Exceptions are defined first to prevent circular imports

### Import Structure

```python
# Standard library imports
from typing import Dict, Any, Optional
from contextlib import contextmanager
import importlib

# Third-party imports
import pandas as pd
from dotenv import load_dotenv

# Local imports
from utils.decorators import preload_parameters, ensure_connected
from templates.constraints import TargetDatabaseEngine
```

<a name="class-init"></a>

## 🏗️ Class Initialization [↑](#table-of-contents)

### Constructor

```python
def __init__(
    self,
    target_database_engine: TargetDatabaseEngine,
    target_database_engine_connect_option: TargetDatabaseConnectionStringOption,
):
```

> 💡 **Important Features**:
>
> - Engine configuration loading
> - Credential management
> - Connection state tracking
> - Environment variable handling

Would you like me to continue with the rest of the documentation sections? Each section will include detailed explanations, code examples, and practical usage notes.# 📚 DatabaseConnector Implementation Guide

## Table of Contents

- [🎯 Core Setup](#core-setup)
- [🏗️ Class Initialization](#class-init)
- [🔌 Connection Management](#connection-mgmt)
- [📋 Query Execution](#query-exec)
- [🧪 Working Example](#example)
- [🔄 Design Patterns Used](#patterns)

<a name="core-setup"></a>

## 🎯 Core Setup [↑](#table-of-contents)

### Exception Hierarchy

```python
class DatabaseError(Exception):
    """Base exception for database operations."""
    pass

class ConnectionError(DatabaseError):
    """Connection failure errors."""
    pass

class CredentialsError(DatabaseError):
    """Credential-related issues."""
    pass
```

> 🔑 **Key Point**: Exceptions are defined first to prevent circular imports

### Import Structure

```python
# Standard library imports
from typing import Dict, Any, Optional
from contextlib import contextmanager
import importlib

# Third-party imports
import pandas as pd
from dotenv import load_dotenv

# Local imports
from utils.decorators import preload_parameters, ensure_connected
from templates.constraints import TargetDatabaseEngine
```

<a name="class-init"></a>

## 🏗️ Class Initialization [↑](#table-of-contents)

### Constructor

```python
def __init__(
    self,
    target_database_engine: TargetDatabaseEngine,
    target_database_engine_connect_option: TargetDatabaseConnectionStringOption,
):
```

> 💡 **Important Features**:
>
> - Engine configuration loading
> - Credential management
> - Connection state tracking
> - Environment variable handling

Would you like me to continue with the rest of the documentation sections? Each section will include detailed explanations, code examples, and practical usage notes.# 📚 DatabaseConnector Implementation Guide

## Table of Contents

- [🎯 Core Setup](#core-setup)
- [🏗️ Class Initialization](#class-init)
- [🔌 Connection Management](#connection-mgmt)
- [📋 Query Execution](#query-exec)
- [🧪 Working Example](#example)
- [🔄 Design Patterns Used](#patterns)

<a name="core-setup"></a>

## 🎯 Core Setup [↑](#table-of-contents)

### Exception Hierarchy

```python
class DatabaseError(Exception):
    """Base exception for database operations."""
    pass

class ConnectionError(DatabaseError):
    """Connection failure errors."""
    pass

class CredentialsError(DatabaseError):
    """Credential-related issues."""
    pass
```

> 🔑 **Key Point**: Exceptions are defined first to prevent circular imports

### Import Structure

```python
# Standard library imports
from typing import Dict, Any, Optional
from contextlib import contextmanager
import importlib

# Third-party imports
import pandas as pd
from dotenv import load_dotenv

# Local imports
from utils.decorators import preload_parameters, ensure_connected
from templates.constraints import TargetDatabaseEngine
```

<a name="class-init"></a>

## 🏗️ Class Initialization [↑](#table-of-contents)

### Constructor

```python
def __init__(
    self,
    target_database_engine: TargetDatabaseEngine,
    target_database_engine_connect_option: TargetDatabaseConnectionStringOption,
):
```

> 💡 **Important Features**:
>
> - Engine configuration loading
> - Credential management
> - Connection state tracking
> - Environment variable handling

<a name="example"></a>

## 🧪 Working Examples [↑](#table-of-contents)

### Basic Connection Example

```python
try:
    db = DatabaseConnector(
        target_database_engine=TargetDatabaseEngine.MSSQL,
        target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
    )

    with db.set_credentials_based_on_connect_option() \
           .finalization_of_connection_parameters(
                DRIVER="{ODBC Driver 17 for SQL Server}",
                SERVER="127.0.0.1",
                PORT_NUMBER=13001,
                DATABASE_NAME="AdventureWorks2019"
            ) \
           .connect_to_database() as conn:
        
        # Your queries here
        print("\nConnection successful!")
```

> 🎯 **Key Points**:
>
> - Automatic resource management
> - Error handling
> - Connection cleanup

### Query Examples

```python
# PrettyTable Output
conn.execute_query_to_prettytable(
    "SELECT @@VERSION as Version",
    print_result=True
)

# DataFrame Output
df = conn.execute_query_to_dataframe(
    """
    SELECT ProductID, Name, ListPrice 
    FROM Production.Product 
    WHERE ListPrice > 0
    """,
    index_col="ProductID"
)
```

<a name="patterns"></a>

## 🔄 Design Patterns Used [↑](#table-of-contents)

### 1. Fluent Interface Pattern

```python
# Method chaining for configuration
db.method1().method2().method3()
```

> 🔑 **Benefits**:
>
> - Readable configuration
> - Natural progression of setup
> - Self-documenting code

### 2. Template Method Pattern

```python
# Engine templates define behavior
MSSQL: Dict[str, Dict[str, Any]] = {
    "MSSQL": {
        "DEFAULT_PARAMETERS": {...},
        "FINALIZED_CONNECTION_PARAMS": {...}
    }
}
```

> 🏗️ **Structure**:
>
> - Standard interface across engines
> - Customizable behavior
> - Reusable components

### 3. Context Manager Pattern

```python
with db.connect_to_database() as conn:
    # Automatic resource management
    pass
```

> 🔄 **Lifecycle**:
>
> 1. Resource acquisition
> 2. Resource usage
> 3. Automatic cleanup

### 4. Decorator Pattern

```python
@ensure_connected
@preload_parameters(_get_default_parameters)
def method(self):
    pass
```

> 🎨 **Used For**:
>
> - Connection validation
> - Parameter preprocessing
> - Error handling

## 📝 Usage Guidelines [↑](#table-of-contents)

### Best Practices

1. Always use with context manager
2. Use uppercase for parameter names
3. Handle exceptions appropriately
4. Check connection state before operations

### Common Pitfalls

❌ Don't:

- Skip error handling
- Ignore connection cleanup
- Mix parameter case (use uppercase)
- Forget to close connections

✅ Do:

- Use context managers
- Follow the fluent pattern
- Check template parameters
- Handle all exceptions

### Configuration Tips

```python
# Environment Variables (.env)
MSSQL_USERNAME=sa
MSSQL_PASSWORD=yourpassword

# Launch Configuration (launch.json)
{
    "env": {
        "PYTHONPATH": "${workspaceFolder}"
    }
}
```
