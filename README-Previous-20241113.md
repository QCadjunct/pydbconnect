# PyDBConnect

A modern, type-safe database connectivity library with support for multiple engines and advanced features.

## Table of Contents
1. [Features](#features)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Basic Usage](#basic-usage)
5. [Advanced Features](#advanced-features)
6. [Environment Setup](#environment-setup)
7. [Contributing](#contributing)
8. [License](#license)
9. [Acknowledgments](#acknowledgments)
10. [Support](#support)

## Features

- [🔌 Multiple Database Engines](#multiple-database-engines) (MSSQL, MySQL, PostgreSQL, SQLite, DuckDB)
- [🔒 Secure Credential Management](#secure-credential-management)
- [🔄 Fluent Interface](#fluent-interface) with method chaining
- [📊 Pandas Integration](#pandas-integration) for data analysis
- [🎯 Type Safety](#type-safety) with runtime validation
- [🔧 Extensible Design](#extensible-design) for adding new database engines
- [🔍 Advanced Query Building](#advanced-query-building) and optimization
- [📈 Performance Monitoring](#performance-monitoring) and metrics
- [🛡️ Data Masking](#data-masking) and encryption capabilities
- [🔄 Transaction Management](#transaction-management) with savepoints
- [📝 Comprehensive Audit Logging](#audit-logging)
- [⚡ Connection Pooling](#connection-pooling) for better performance
- [🔍 Query Caching](#query-caching) and optimization
- [🚨 Automatic Retry Mechanisms](#retry-mechanisms)
- [📊 Pretty Table Formatting](#table-formatting) for results
- [🔗 Framework Integration](#framework-integration) (FastAPI, Flask, Django)
- [🛠️ Administrative Operations](#administrative-operations) (backup, restore, analyze, vacuum)
- [📊 Database Optimization](#database-optimization)
- [🔄 Cross-Database Operations](#cross-database-operations)
- [🎯 Template Administration](#template-administration)
- [🔍 Schema Analysis](#schema-analysis)
- [🛡️ Engine-Specific Security](#engine-specific-security)
- [📈 Advanced Statistics](#advanced-statistics)
- [🔧 Custom Engine Configuration](#custom-engine-configuration)

### Multiple Database Engines
Support for MSSQL, MySQL, PostgreSQL, SQLite, and DuckDB with unified interface.

[Back to Features](#features)

### Secure Credential Management
Environment variable-based credential management for enhanced security.

[Back to Features](#features)

### Fluent Interface
Method chaining for intuitive and readable database operations.

[Back to Features](#features)

### Pandas Integration
Built-in support for DataFrames and Pandas operations.

[Back to Features](#features)

### Type Safety
Runtime type validation and checking.

[Back to Features](#features)

### Extensible Design
Plugin architecture for adding new database engines.

[Back to Features](#features)

### Advanced Query Building
Sophisticated query construction and optimization.

[Back to Features](#features)

### Performance Monitoring
Real-time metrics and performance tracking.

[Back to Features](#features)

### Data Masking
Advanced data protection and encryption features.

[Back to Features](#features)

### Transaction Management
Robust transaction handling with savepoint support.

[Back to Features](#features)

### Audit Logging
Comprehensive operation logging and tracking.

[Back to Features](#features)

### Connection Pooling
Efficient connection management and reuse.

[Back to Features](#features)

### Query Caching
Smart query result caching for improved performance.

[Back to Features](#features)

### Retry Mechanisms
Automatic retry handling for failed operations.

[Back to Features](#features)

### Table Formatting
Pretty printing of query results.

[Back to Features](#features)

### Framework Integration
Seamless integration with popular Python frameworks.

[Back to Features](#features)

### Administrative Operations
Database administration and maintenance features.

[Back to Features](#features)

### Database Optimization
Performance tuning and query optimization.

[Back to Features](#features)

### Cross-Database Operations
Operations across multiple database engines.

[Back to Features](#features)

### Template Administration
Template-based database administration.

[Back to Features](#features)

### Schema Analysis
Database schema analysis and optimization.

[Back to Features](#features)

### Engine-Specific Security
Security features tailored to each database engine.

[Back to Features](#features)

### Advanced Statistics
Detailed database statistics and metrics.

[Back to Features](#features)

### Custom Engine Configuration
Flexible engine-specific configurations.

[Back to Features](#features)

## Quick Start

```python
from pydbconnect import DatabaseConnection, TargetDatabaseEngine

# Create connection
db = DatabaseConnection(
    TargetDatabaseEngine.POSTGRESQL,
    TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd
).finalization_of_connection_parameters(
    host="localhost",
    database="myapp"
).connect_to_database()

# Execute queries with Pandas integration
df = db.execute_sql_to_dataframe("SELECT * FROM users")
```

[Back to Table of Contents](#table-of-contents)

## Installation

```bash
# Basic installation
pip install pydbconnect

# With all optional dependencies
pip install pydbconnect[all]

# Database specific installations
pip install pydbconnect[mssql]    # For MSSQL support
pip install pydbconnect[postgres] # For PostgreSQL support
pip install pydbconnect[mysql]    # For MySQL support
```

[Back to Table of Contents](#table-of-contents)

