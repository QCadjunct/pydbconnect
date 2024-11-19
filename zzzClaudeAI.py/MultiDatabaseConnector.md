# 🔄 MultiDatabaseConnector Documentation

## Table of Contents
1. [📋 Overview](#overview)
2. [🏗️ Architecture](#architecture)
3. [⚙️ Core Components](#components)
4. [🔌 Implementation Details](#implementation)
5. [💾 Operations](#operations)
6. [📊 Examples](#examples)
7. [🔍 Best Practices](#practices)

## 📋 Overview <a name="overview"></a>
[↑ Back to Top](#table-of-contents)

The `MultiDatabaseConnector` extends `BaseDatabaseConnector` to provide:
- 🔗 Multiple simultaneous database connections
- 📝 Template-driven configuration
- 🔄 Dynamic parameter handling
- 🛡️ Type-safe operations

## 🏗️ Architecture <a name="architecture"></a>
[↑ Back to Top](#table-of-contents)

### Core Classes
```python
class DatabaseInstance:
    """Dynamic database instance based on template configuration."""
    
    def __init__(self, name: str, 
                 engine_type: TargetDatabaseEngine,
                 connect_option: TargetDatabaseConnectionStringOption):
        self.name = name
        self.engine_type = engine_type
        self.connect_option = connect_option
        self._template_config = None
        self._connection_params = {}
        self._finalized_params = {}
        self.is_active = True
        self.attached_at = datetime.now()
```

### Template Integration
```python
def _load_engine_config(self) -> Dict[str, Any]:
    """Load engine-specific configuration from templates."""
    try:
        return getattr(template, self.target_database_engine_name)
    except AttributeError as e:
        raise DatabaseError(f"Unsupported database engine: {self.target_database_engine_name}")
```

Would you like me to continue with the complete documentation?
