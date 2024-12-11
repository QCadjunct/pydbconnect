# PyDBConnect

## TOC

- [Overview](#overview)
- [Structure](#structure)
- [Usage](#usage)
- [Development](#dev)

<a name="overview"></a>

## 🎯 Overview

Database connector with fluent interface design and template-based engine configuration.

<a name="structure"></a>

## 📁 Structure

```
core/          # Connector implementation
templates/     # Engine templates & constraints
utils/         # Support decorators
tests/         # Proof of concept examples
docs/          # Implementation guides
```

<a name="usage"></a>

## 💻 Usage

```python
from core.connector import DatabaseConnector
from templates.constraints import TargetDatabaseEngine, TargetDatabaseConnectionStringOption

# Initialize
db = DatabaseConnector(
    target_database_engine=TargetDatabaseEngine.MSSQL,
    target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
)

# Connect with fluent pattern
with (db.set_credentials_based_on_connect_option()
      .finalization_of_connection_parameters(
          DRIVER="{ODBC Driver 17 for SQL Server}",
          SERVER="127.0.0.1",
          PORT_NUMBER=13001,
          DATABASE_NAME="AdventureWorks2019"
      )
      .connect_to_database()) as conn:
    
    # Execute query
    conn.execute_query_to_prettytable(
        "SELECT @@VERSION as Version",
        print_result=True
    )
```

<a name="dev"></a>

## ⚡ Development

- Strict adherence to template-based architecture
- Fluent pattern implementation
- KISS principle
- Parameters must be UPPERCASE
- Engine templates (templates/engines.py) define behavior
- Constraints (templates/constraints.py) define interfaces

---
© 2024
