# 📘 Using UV - Upgrading to psycopg3 with uv: Complete Migration Guide with Async Support

## Table of Contents

- [📘 Upgrading to psycopg3 with uv: Complete Migration Guide with Async Support](#-upgrading-to-psycopg3-with-uv-complete-migration-guide-with-async-support)

  - [Table of Contents](#table-of-contents)
  - [🚀 Introduction](#-introduction)
  - [📋 Prerequisites](#-prerequisites)
  - [⚡ Step 1: Installing uv](#-step-1-installing-uv)
  - [🔄 Step 2: Understanding Key Differences Between psycopg2 and psycopg3](#-step-2-understanding-key-differences-between-psycopg2-and-psycopg3)
  - [🏗️ Step 3: Creating a Virtual Environment with uv](#️-step-3-creating-a-virtual-environment-with-uv)
  - [📦 Step 4: Installing psycopg3 with uv](#-step-4-installing-psycopg3-with-uv)
  - [📝 Step 5: Creating the New psycopg3 Dictionary Structure](#-step-5-creating-the-new-psycopg3-dictionary-structure)
  - [⚙️ Step 6: Adding Asynchronous Extensions](#️-step-6-adding-asynchronous-extensions)
  - [🔌 Step 7: Connection Pooling Support](#-step-7-connection-pooling-support)
  - [📊 Step 8: Usage Examples](#-step-8-usage-examples)
    - [Synchronous Operations](#synchronous-operations)
    - [Asynchronous Operations](#asynchronous-operations)
    - [Using Connection Pools](#using-connection-pools)
  - [🧪 Step 9: Testing Your Implementation](#-step-9-testing-your-implementation)
  - [📚 Complete psycopg3 Dictionary](#-complete-psycopg3-dictionary)
  - [📄 Dictionary Documentation](#-dictionary-documentation)
  - [📌 Conclusion](#-conclusion)

## 🚀 Introduction

This guide provides a step-by-step approach to upgrade your PostgreSQL database connection configuration from psycopg2 to psycopg3 using uv, with a focus on adding asynchronous capabilities. uv is an extremely fast Python package installer and resolver written in Rust that can significantly speed up your Python development workflow.

uv is designed as a drop-in replacement for pip and pip-tools, and is ready for production use. Using uv for this migration will ensure faster, more reliable package installation while setting up psycopg3 with its advanced async features.

[🔝 Back to TOC](#table-of-contents)

## 📋 Prerequisites

Before proceeding with the upgrade, ensure you have:

- Python 3.7+ (for full async support, Python 3.8+ is recommended)
- Basic understanding of async/await patterns in Python
- PostgreSQL server (version 10+)

Note: You don't need to pre-install pip or other tools as uv will handle everything.

[🔝 Back to TOC](#table-of-contents)

## ⚡ Step 1: Installing uv

First, let's install uv, the modern Python package manager we'll use throughout this guide:

```bash
# Install using pip (if you already have Python installed)
pip install uv

# Or use the standalone installer from the official website
# For Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# For Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex
```

If your Python installation is in the system PATH, you can invoke uv by just typing uv at the command line. Verify the installation by running:

```bash
uv --version
```

[🔝 Back to TOC](#table-of-contents)

## 🔄 Step 2: Understanding Key Differences Between psycopg2 and psycopg3

Before diving into the migration, it's important to understand the main differences between psycopg2 and psycopg3:

1. **Package Name**: Changed from `psycopg2` to `psycopg`
2. **Connection Parameters**: Slight syntax changes in connection strings
3. **Async Support**: Built-in support for async database operations
4. **Connection Pooling**: Integrated through the `psycopg_pool` module
5. **Type Annotations**: Better support for Python type hints
6. **Error Handling**: Improved exception hierarchy
7. **Context Managers**: Enhanced support for `with` and `async with` statements

There is no psycopg3 package, only psycopg! This is an important detail to remember when setting up your imports and dependencies.

[🔝 Back to TOC](#table-of-contents)

## 🏗️ Step 3: Creating a Virtual Environment with uv

Let's create a dedicated virtual environment for our project using uv:

```bash
# Navigate to your project directory
cd your-project-directory

# Create a virtual environment
uv venv
```

uv handles this automatically, creating a virtual environment in a .venv folder in your project directory.

Activate the virtual environment:

```bash
# On Linux/macOS
source .venv/bin/activate

# On Windows
.venv\Scripts\activate
```

[🔝 Back to TOC](#table-of-contents)

## 📦 Step 4: Installing psycopg3 with uv

Now let's install psycopg3 and its dependencies using uv:

```bash
# Install the basic psycopg3 package
uv pip install "psycopg[binary]"

# Install with pool support for connection pooling
uv pip install "psycopg[binary,pool]"
```

The binary installation provides a self-contained package with all the libraries needed. If you need a pure Python installation or have specific system requirements, you can install without the binary extra.

For asynchronous support and connection pooling (which we'll use later in this guide), make sure to install the pool extra as shown above.

[🔝 Back to TOC](#table-of-contents)

## 📝 Step 5: Creating the New psycopg3 Dictionary Structure

Now let's create the base structure for our psycopg3 dictionary:

```python
PSYCOPG3: Dict[str, Dict[str, Any]] = {
    "PSYCOPG3": {
        "DEFAULT_PARAMETERS": {
            "DATABASE_NAME": "NorthwindOrderSubsystem",
            "SERVER": "localhost",
            "PORT_NUMBER": 20301,
            "USERNAME": "postgres",
            "PASSWORD": "Password",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DATABASE_NAME","SERVER","PORT_NUMBER"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": "N",
                "BASE_CONNECTION_STRING": "host={0} port={1} dbname={2} user={3} password={4}",
                "BASE_ODBC_DSN_CONNECTION_STRING": None
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["SERVER"],
                d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["PORT_NUMBER"],
                d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
                d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["PASSWORD"]
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["DSN_NAME"]
            ) if d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["IS_DSN_NAME_SUPPORTED"] == "Y" else None
        },
        "CRUDBASIC": {
            "IMPORT": "psycopg",
            "PARAMETER_PLACEHOLDER": "%s",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        },
        "CREATE_DATABASE_CONNECTION": {
            "CONNECTION_NOTES": "Use psycopg.connect with the appropriate connection string for synchronous operations.",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('psycopg').connect(finalized_parameter_connection_string)
        }
    }
}
```

Key changes from the psycopg2 dictionary:

1. Renamed the main key from "PSYCOPG2" to "PSYCOPG3"
2. Updated the IMPORT value from "psycopg2" to "psycopg"
3. Modified the BASE_CONNECTION_STRING format to match psycopg3's requirements (removed semicolons between parameters)
4. Changed "database" to "dbname" in the connection string
5. Updated CONNECTION_NOTES to reference psycopg instead of pyodbc

[🔝 Back to TOC](#table-of-contents)

## ⚙️ Step 6: Adding Asynchronous Extensions

Now let's add the asynchronous capabilities by creating a new "ASYNC_EXTENSIONS" section:

```python
"ASYNC_EXTENSIONS": {
    "IMPORT": "psycopg.AsyncConnection",
    "IS_SUPPORTED": "Y",
    "CONNECTION_NOTES": "Use psycopg.AsyncConnection.connect with the appropriate connection string for asynchronous operations.",
    "LAMBDA_FINALIZED_PARAMETER_ASYNC_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('psycopg.AsyncConnection').connect(finalized_parameter_connection_string),
    "ASYNC_CURSOR": {
        "IMPORT": "psycopg.AsyncCursor",
        "USAGE_NOTES": "Use 'async with conn.cursor() as cur:' pattern for cursor operations."
    },
    "ASYNC_EXECUTE": {
        "EXECUTE_PATTERN": "await cursor.execute(query, params)",
        "FETCH_PATTERN": {
            "FETCHONE": "await cursor.fetchone()",
            "FETCHMANY": "await cursor.fetchmany(size)",
            "FETCHALL": "await cursor.fetchall()"
        }
    },
    "ASYNC_TRANSACTION": {
        "BEGIN_PATTERN": "async with conn.transaction():",
        "USAGE_NOTES": "Transactions are managed using context managers in psycopg3."
    }
}
```

This section includes:

1. Async connection setup and import details
2. Async cursor management
3. Async query execution and result fetching patterns
4. Async transaction management

[🔝 Back to TOC](#table-of-contents)

## 🔌 Step 7: Connection Pooling Support

Next, let's add connection pooling support for more efficient connection management:

```python
"CONNECTION_POOL": {
    "IMPORT": "psycopg_pool.AsyncConnectionPool",
    "USAGE_NOTES": "Use AsyncConnectionPool for connection pooling with async operations.",
    "LAMBDA_CREATE_POOL": lambda finalized_parameter_connection_string, min_size=1, max_size=10: lambda: get_db_target_engine_module('psycopg_pool').AsyncConnectionPool(finalized_parameter_connection_string, min_size=min_size, max_size=max_size)
}
```

This component provides:

1. Import information for the connection pool
2. Usage notes for implementers
3. A lambda function for creating connection pools with configurable sizes

[🔝 Back to TOC](#table-of-contents)

## 📊 Step 8: Usage Examples

Let's create usage examples to demonstrate how to work with our new dictionary.

### Synchronous Operations

```python
# Create a synchronous connection
base_conn_string = PSYCOPG3["PSYCOPG3"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](PSYCOPG3)
connection_func = PSYCOPG3["PSYCOPG3"]["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](base_conn_string)
db_connection = connection_func()

# Execute a query synchronously
with db_connection.cursor() as cursor:
    cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
    result = cursor.fetchall()
```

### Asynchronous Operations

```python
# Create an asynchronous connection
base_conn_string = PSYCOPG3["PSYCOPG3"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](PSYCOPG3)
async_connection_func = PSYCOPG3["PSYCOPG3"]["ASYNC_EXTENSIONS"]["LAMBDA_FINALIZED_PARAMETER_ASYNC_CONNECTION_STRING"](base_conn_string)
db_connection = await async_connection_func()

# Execute a query asynchronously
async with db_connection.cursor() as cursor:
    await cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
    result = await cursor.fetchall()
```

### Using Connection Pools

```python
# Create a connection pool
base_conn_string = PSYCOPG3["PSYCOPG3"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](PSYCOPG3)
pool_creator = PSYCOPG3["PSYCOPG3"]["ASYNC_EXTENSIONS"]["CONNECTION_POOL"]["LAMBDA_CREATE_POOL"](base_conn_string, min_size=2, max_size=20)
pool = await pool_creator()

# Use a connection from the pool
async with pool.connection() as conn:
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM users WHERE id = %s", [user_id])
        result = await cur.fetchall()
```

[🔝 Back to TOC](#table-of-contents)

## 🧪 Step 9: Testing Your Implementation

Before implementing the new dictionary in production, follow these testing steps:

1. **Basic Connection Test**: Verify that synchronous connections work as expected
2. **Async Connection Test**: Test asynchronous connection establishment
3. **Simple Query Execution**: Run basic SELECT queries with both sync and async methods
4. **Transaction Management**: Test transaction commit and rollback functionality
5. **Connection Pool Test**: Verify pool creation and connection acquisition
6. **Error Handling**: Ensure proper error propagation in async context
7. **Performance Benchmark**: Compare performance between psycopg2 and psycopg3

Use uv to manage your test environment:

```bash
# Create a dedicated test environment
uv venv test_env
source test_env/bin/activate  # or test_env\Scripts\activate on Windows

# Install test dependencies
uv pip install "psycopg[binary,pool]" pytest pytest-asyncio
```

[🔝 Back to TOC](#table-of-contents)

## 📚 Complete psycopg3 Dictionary

```python
PSYCOPG3: Dict[str, Dict[str, Any]] = {
    "PSYCOPG3": {
        "DEFAULT_PARAMETERS": {
            "DATABASE_NAME": "NorthwindOrderSubsystem",
            "SERVER": "localhost",
            "PORT_NUMBER": 20301,
            "USERNAME": "postgres",
            "PASSWORD": "Password",
            "FORMAT_CONNECTION_STRING": {
                "LOAD_DEFAULT_PARAMETER_KEYS": ["DATABASE_NAME","SERVER","PORT_NUMBER"],
                "METHOD_LOAD_DEFAULT_PARAMETER_KEYS_DICT": load_default_parameter_keys_dict,
                "IS_DSN_NAME_SUPPORTED": "N",
                "BASE_CONNECTION_STRING": "host={0} port={1} dbname={2} user={3} password={4}",
                "BASE_ODBC_DSN_CONNECTION_STRING": None
            }
        },
        "FINALIZED_CONNECTION_PARAMS": {
            "LAMBDA_FINALIZED_BASE_CONNECTION_STRING": lambda d: d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_CONNECTION_STRING"].format(
                d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["SERVER"],
                d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["PORT_NUMBER"],
                d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["DATABASE_NAME"],
                d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["USERNAME"],
                d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["PASSWORD"]
            ),
            "LAMBDA_FINALIZED_DSN_CONNECTION_STRING": lambda d: d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["BASE_ODBC_DSN_CONNECTION_STRING"].format(
                d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["DSN_NAME"]
            ) if d["PSYCOPG3"]["DEFAULT_PARAMETERS"]["FORMAT_CONNECTION_STRING"]["IS_DSN_NAME_SUPPORTED"] == "Y" else None
        },
        "CRUDBASIC": {
            "IMPORT": "psycopg",
            "PARAMETER_PLACEHOLDER": "%s",
            "IS_USERNAME_AND_PASSWORD_REQUIRED": True
        },
        "CREATE_DATABASE_CONNECTION": {
            "CONNECTION_NOTES": "Use psycopg.connect with the appropriate connection string for synchronous operations.",
            "LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('psycopg').connect(finalized_parameter_connection_string)
        },
        "ASYNC_EXTENSIONS": {
            "IMPORT": "psycopg.AsyncConnection",
            "IS_SUPPORTED": "Y",
            "CONNECTION_NOTES": "Use psycopg.AsyncConnection.connect with the appropriate connection string for asynchronous operations.",
            "LAMBDA_FINALIZED_PARAMETER_ASYNC_CONNECTION_STRING": lambda finalized_parameter_connection_string: lambda: get_db_target_engine_module('psycopg.AsyncConnection').connect(finalized_parameter_connection_string),
            "ASYNC_CURSOR": {
                "IMPORT": "psycopg.AsyncCursor",
                "USAGE_NOTES": "Use 'async with conn.cursor() as cur:' pattern for cursor operations."
            },
            "ASYNC_EXECUTE": {
                "EXECUTE_PATTERN": "await cursor.execute(query, params)",
                "FETCH_PATTERN": {
                    "FETCHONE": "await cursor.fetchone()",
                    "FETCHMANY": "await cursor.fetchmany(size)",
                    "FETCHALL": "await cursor.fetchall()"
                }
            },
            "ASYNC_TRANSACTION": {
                "BEGIN_PATTERN": "async with conn.transaction():",
                "USAGE_NOTES": "Transactions are managed using context managers in psycopg3."
            },
            "CONNECTION_POOL": {
                "IMPORT": "psycopg_pool.AsyncConnectionPool",
                "USAGE_NOTES": "Use AsyncConnectionPool for connection pooling with async operations.",
                "LAMBDA_CREATE_POOL": lambda finalized_parameter_connection_string, min_size=1, max_size=10: lambda: get_db_target_engine_module('psycopg_pool').AsyncConnectionPool(finalized_parameter_connection_string, min_size=min_size, max_size=max_size)
            }
        }
    }
}
```

[🔝 Back to TOC](#table-of-contents)

## 📄 Dictionary Documentation

```
PSYCOPG3 Dictionary Structure and Usage

This dictionary contains configuration and connection details for PostgreSQL database operations using the psycopg3 library, with support for both synchronous and asynchronous operations.

Structure:
1. DEFAULT_PARAMETERS:
   - Contains default connection parameters such as database name, server, port, username, and password.
   - Includes FORMAT_CONNECTION_STRING subdictionary with configuration for connection string formatting.
   - Note: ODBC DSN is not supported for this configuration (IS_DSN_NAME_SUPPORTED: "N").

2. FINALIZED_CONNECTION_PARAMS:
   - LAMBDA_FINALIZED_BASE_CONNECTION_STRING: Lambda function to format the base connection string using default parameters.
   - LAMBDA_FINALIZED_DSN_CONNECTION_STRING: Lambda function for DSN connection string (returns None as DSN is not supported by default).

3. CRUDBASIC:
   - Specifies the import module (psycopg) and parameter placeholder ("%s") for SQL queries.

4. CREATE_DATABASE_CONNECTION:
   - CONNECTION_NOTES: Provides guidance on using psycopg.connect with the appropriate connection string.
   - LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING: Lambda function to create a synchronous database connection using psycopg.

5. ASYNC_EXTENSIONS (New in PSYCOPG3):
   - IMPORT: Specifies the import module for asynchronous connections.
   - IS_SUPPORTED: Indicates whether async operations are supported ("Y").
   - CONNECTION_NOTES: Provides guidance on using psycopg.AsyncConnection.connect.
   - LAMBDA_FINALIZED_PARAMETER_ASYNC_CONNECTION_STRING: Lambda function to create an asynchronous database connection.
   - ASYNC_CURSOR: Details for working with asynchronous cursors.
   - ASYNC_EXECUTE: Patterns for executing queries and fetching results asynchronously.
   - ASYNC_TRANSACTION: Patterns for managing transactions asynchronously.
   - CONNECTION_POOL: Configuration for asynchronous connection pooling.

Usage Examples:
1. Synchronous Connection:
   ```python
   base_conn_string = PSYCOPG3["PSYCOPG3"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](PSYCOPG3)
   connection_func = PSYCOPG3["PSYCOPG3"]["CREATE_DATABASE_CONNECTION"]["LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING"](base_conn_string)
   db_connection = connection_func()
   ```

2. Asynchronous Connection:
   ```python
   base_conn_string = PSYCOPG3["PSYCOPG3"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](PSYCOPG3)
   async_connection_func = PSYCOPG3["PSYCOPG3"]["ASYNC_EXTENSIONS"]["LAMBDA_FINALIZED_PARAMETER_ASYNC_CONNECTION_STRING"](base_conn_string)
   async_db_connection = await async_connection_func()
   ```

3. Using Asynchronous Connection Pool:
   ```python
   base_conn_string = PSYCOPG3["PSYCOPG3"]["FINALIZED_CONNECTION_PARAMS"]["LAMBDA_FINALIZED_BASE_CONNECTION_STRING"](PSYCOPG3)
   pool_creator = PSYCOPG3["PSYCOPG3"]["ASYNC_EXTENSIONS"]["CONNECTION_POOL"]["LAMBDA_CREATE_POOL"](base_conn_string, min_size=2, max_size=20)
   async_pool = await pool_creator()
   async with async_pool.connection() as conn:
       async with conn.cursor() as cur:
           await cur.execute("SELECT * FROM table WHERE id = %s", [id_value])
           result = await cur.fetchall()
   ```

Key Differences from PSYCOPG2:
1. Import changed from 'psycopg2' to 'psycopg'.
2. Connection string format has slight differences.
3. Added comprehensive async support through the ASYNC_EXTENSIONS section.
4. Support for connection pooling with both sync and async operations.
5. Transaction management using context managers.

Note: Ensure that both 'psycopg' and 'psycopg-pool' packages are installed in your environment before using this configuration.

This configuration supports both traditional synchronous database operations and modern asynchronous patterns, allowing for more efficient handling of database connections in high-concurrency environments.
```

[🔝 Back to TOC](#table-of-contents)

## 📌 Conclusion

By following this guide, you have successfully upgraded your PostgreSQL connection configuration from psycopg2 to psycopg3 using uv, adding robust asynchronous support. The new structure maintains backward compatibility while enabling modern async patterns for improved performance and resource utilization.

The key benefits of this upgrade include:
- Native async/await support for better concurrency
- Improved connection management through pooling
- Enhanced transaction handling with context managers
- Better error reporting and diagnostics
- Support for both synchronous and asynchronous operations from a single configuration
- Faster development workflow using uv's optimized package management

Remember to thoroughly test your implementation in a staging environment before deploying to production.

[🔝 Back to TOC](#table-of-contents)