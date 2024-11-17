# 🏗️ Database Connector Project Structure

## Table of Contents
1. [📋 Overview](#overview)
2. [🌳 Directory Structure](#directory-structure)
3. [📦 Core Components](#core)
4. [🔌 Connectors](#connectors)
5. [📝 Templates](#templates)
6. [🛠️ Utilities](#utilities)
7. [⚙️ Configuration](#config)
8. [📚 Usage Examples](#usage)

## 📋 Overview <a name="overview"></a>
[↑ Back to Top](#table-of-contents)

The Database Connector project follows a modular architecture with clear separation of concerns. Each directory serves a specific purpose and contains related functionality.

## 🌳 Directory Structure <a name="directory-structure"></a>
[↑ Back to Top](#table-of-contents)

```
database_connector/
│
├── core/                          # Core Framework
│   ├── __init__.py
│   ├── base.py                    
│   ├── exceptions.py              
│   └── descriptors/               
│       ├── __init__.py
│       ├── credentials.py         
│       ├── connection.py          
│       └── results.py            
│
├── connectors/                    # Implementation
│   ├── __init__.py
│   ├── database_connector.py      
│   └── multi_database_connector.py 
│
├── templates/                     # Template System
│   ├── __init__.py
│   ├── engine_templates.py        
│   └── connection_templates.py    
│
├── utils/                         # Utilities
│   ├── __init__.py
│   ├── connection_manager.py      
│   └── validation.py             
│
└── config/                        # Configuration
    ├── __init__.py
    ├── engine_types.py           
    └── connection_options.py      
```

## 📦 Core Components <a name="core"></a>
[↑ Back to Top](#table-of-contents)

### base.py
Contains the `BaseDatabaseConnector` abstract base class that defines the core interface.
```python
from abc import ABC, abstractmethod

class BaseDatabaseConnector(ABC):
    """Abstract base class for all database connectors."""
    @abstractmethod
    def connect(self) -> 'BaseDatabaseConnector':
        pass
```

### descriptors/
Directory containing descriptor classes for attribute management:

#### credentials.py
```python
class CredentialsDescriptor(BaseDescriptor):
    """Manages database credentials securely."""
    def __init__(self, name: str):
        self.name = f"_{name}"
```

#### connection.py
```python
class ConnectionParametersDescriptor(BaseDescriptor):
    """Manages connection parameters."""
    def __init__(self, name: str):
        self.name = f"_{name}"
```

#### results.py
```python
class QueryResultDescriptor(BaseDescriptor):
    """Manages query results."""
    def __init__(self, name: str):
        self.name = f"_{name}"
```

## 🔌 Connectors <a name="connectors"></a>
[↑ Back to Top](#table-of-contents)

### database_connector.py
Single database connection implementation:
```python
class DatabaseConnector(BaseDatabaseConnector):
    """Single database connection implementation."""
    def __init__(self, engine_type: TargetDatabaseEngine,
                 connect_option: TargetDatabaseConnectionStringOption):
        super().__init__()
```

### multi_database_connector.py
Multi-database connection implementation:
```python
class MultiDatabaseConnector(BaseDatabaseConnector):
    """Multi-database connection implementation."""
    def __init__(self):
        super().__init__()
        self.instances: Dict[str, DatabaseInstance] = {}
```

## 📝 Templates <a name="templates"></a>
[↑ Back to Top](#table-of-contents)

### engine_templates.py
Database engine configuration templates:
```python
class EngineTemplate:
    """Database engine configuration templates."""
    MSSQL = {
        'MODULE': 'pyodbc',
        'DSN_TEMPLATE': 'DRIVER={SQL Server};SERVER={server}'
    }
```

### connection_templates.py
Connection string templates:
```python
class ConnectionTemplate:
    """Connection string templates."""
    DSN = 'DSN={dsn};UID={username};PWD={password}'
    DIRECT = 'DRIVER={driver};SERVER={server};DATABASE={database}'
```

## 🛠️ Utilities <a name="utilities"></a>
[↑ Back to Top](#table-of-contents)

### connection_manager.py
Connection management utilities:
```python
class ConnectionManager:
    """Manages database connections."""
    def __init__(self):
        self._pool = ConnectionPool()
        self._active_connections = {}
```

### validation.py
Input validation utilities:
```python
class ValidationUtils:
    """Validation utility functions."""
    @staticmethod
    def validate_connection_params(params: Dict[str, Any]) -> bool:
        return all(required in params for required in ['server', 'database'])
```

## ⚙️ Configuration <a name="config"></a>
[↑ Back to Top](#table-of-contents)

### engine_types.py
Engine type enumerations:
```python
class TargetDatabaseEngine(Enum):
    """Supported database engines."""
    MSSQL = auto()
    MYSQL = auto()
    POSTGRESQL = auto()
```

### connection_options.py
Connection option enumerations:
```python
class TargetDatabaseConnectionStringOption(Enum):
    """Connection string options."""
    Default_DSN = auto()
    Customize_DSN = auto()
    Default_ConnectionString = auto()
```

## 📚 Usage Examples <a name="usage"></a>
[↑ Back to Top](#table-of-contents)

### Single Database Connection
```python
from database_connector.connectors import DatabaseConnector
from database_connector.config.engine_types import TargetDatabaseEngine
from database_connector.config.connection_options import TargetDatabaseConnectionStringOption

# Create connector
connector = DatabaseConnector(
    engine_type=TargetDatabaseEngine.MSSQL,
    connect_option=TargetDatabaseConnectionStringOption.Customize_DSN
)

# Establish connection
connector.connect_to_database()
```

### Multi-Database Connection
```python
from database_connector.connectors import MultiDatabaseConnector

# Create multi-database connector
multi_db = MultiDatabaseConnector()

# Attach multiple databases
multi_db.attach(
    "mssql_db",
    TargetDatabaseEngine.MSSQL,
    TargetDatabaseConnectionStringOption.Customize_DSN
).attach(
    "mysql_db",
    TargetDatabaseEngine.MYSQL,
    TargetDatabaseConnectionStringOption.Customize_DSN
)
```

### Using Connection Manager
```python
from database_connector.utils.connection_manager import ConnectionManager

manager = ConnectionManager()
credentials = manager.set_credentials()
```

This structure provides:
- 📦 Clear module organization
- 🔍 Easy code navigation
- ♻️ Reusable components
- 🛡️ Type safety
- 📝 Template-based configuration
- 🔒 Secure credential management

[↑ Back to Top](#table-of-contents)
