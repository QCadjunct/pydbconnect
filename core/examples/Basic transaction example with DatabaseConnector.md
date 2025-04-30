# 📚 Database Transaction Management Implementation Guide

## Basic transaction example with DatabaseConnector.py 

[🔗 Back to Top](#)

## Table of Contents
- [Overview](#overview)
- [Implementation Components](#implementation-components)
  - [Decorators](#decorators)
  - [Transaction Management Constraints](#transaction-management-constraints)
  - [Basic Transaction Example](#basic-transaction-example)
- [Detailed Code Analysis](#detailed-code-analysis)
  - [Decorator Implementation](#decorator-implementation)
  - [Transaction Management Classes](#transaction-management-classes)
  - [Example Implementation Analysis](#example-implementation-analysis)

## Overview
This documentation covers the implementation of database transaction management in Python, including decorators, constraint definitions, and practical examples using the AdventureWorks2019 database.

## Implementation Components

### Decorators

```python
"""Utility decorators."""

from typing import Any, Callable, Optional
from functools import wraps
import time
import logging
from datetime import datetime
from templates.constraints import IsolationLevel

def preload_parameters(preload_method: Callable) -> Callable:
    """
    Decorator that preloads default parameters and merges them with custom parameters.
    """
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self, **params: Any) -> Any:
            if not callable(preload_method):
                raise ValueError("preload_method must be callable")

            default_params = preload_method(self)
            if not isinstance(default_params, dict):
                raise TypeError("preload_method must return a dictionary")

            merged_params = default_params.copy()
            merged_params.update(params)

            return method(self, **merged_params)
        return wrapper
    return decorator

def ensure_connected(f: Callable) -> Callable:
    """
    Decorator to ensure database connection exists before executing a method.
    """
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if hasattr(self, "_connection") and self._connection is not None:
            return f(self, *args, **kwargs)
        if hasattr(self, "connector") and self.connector.is_database_active:
            return f(self, *args, **kwargs)
        raise RuntimeError("Database connection not established")
    return wrapper

def with_isolation_level(isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED):
    """Decorator for setting isolation level with process awareness."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            import os
            pid = os.getpid()
            session_id = getattr(self._connection, "spid", None)

            original_level = self._current_isolation
            try:
                if session_id:
                    logging.info(f"Setting isolation level for PID {pid}, Session {session_id}")
                self._current_isolation = isolation_level
                return func(self, *args, **kwargs)
            finally:
                self._current_isolation = original_level
        return wrapper
    return decorator
```

### Transaction Management Constraints
```python
class IsolationLevel(Enum):
    """SQL Standard Isolation Levels with properties."""
    UNSPECIFIED = "UNSPECIFIED"
    READ_UNCOMMITTED = "READ UNCOMMITTED"
    READ_COMMITTED = "READ COMMITTED"
    REPEATABLE_READ = "REPEATABLE READ"
    SERIALIZABLE = "SERIALIZABLE"
    SNAPSHOT = "SNAPSHOT"
    READ_COMMITTED_SNAPSHOT = "READ COMMITTED SNAPSHOT"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_string(cls, value: str) -> "IsolationLevel":
        """Convert string to isolation level enum."""
        try:
            return cls(value.upper())
        except ValueError:
            return cls.UNKNOWN

    @property
    def dirty_reads(self) -> bool:
        return self == IsolationLevel.READ_UNCOMMITTED

    @property
    def non_repeatable_reads(self) -> bool:
        return self in [IsolationLevel.READ_UNCOMMITTED, IsolationLevel.READ_COMMITTED]

    @property
    def phantom_reads(self) -> bool:
        return self in [
            IsolationLevel.READ_UNCOMMITTED,
            IsolationLevel.READ_COMMITTED,
            IsolationLevel.REPEATABLE_READ,
        ]

    @property
    def is_snapshot_based(self) -> bool:
        return self in [IsolationLevel.SNAPSHOT, IsolationLevel.READ_COMMITTED_SNAPSHOT]

    @classmethod
    def get_default_level(cls) -> "IsolationLevel":
        """Get default isolation level."""
        return cls.READ_COMMITTED

    def get_sql_statement(self) -> str:
        """Get SQL to set this isolation level."""
        return f"SET TRANSACTION ISOLATION LEVEL {self.value}"

class TransactionType(Enum):
    """Transaction Types for database transaction management."""
    BEGIN = "BEGIN"
    COMMIT = "COMMIT"
    ROLLBACK = "ROLLBACK"

    @property
    def sql_statement(self) -> str:
        """Get the SQL statement for this transaction type."""
        if self == TransactionType.BEGIN:
            return "BEGIN TRANSACTION"
        return self.value

    @property
    def requires_isolation_level(self) -> bool:
        """Check if this transaction type requires isolation level."""
        return self == TransactionType.BEGIN

    @property
    def can_nest(self) -> bool:
        """Check if this transaction type supports nesting."""
        return self == TransactionType.BEGIN
```

### Basic Transaction Example

```python
def demonstrate_basic_transaction():
    """Demonstrate basic transaction operations with explicit transaction control."""
    print("\n=== Starting Basic Transaction Demo ===")

    # Constants for the transaction
    PRODUCT_ID = 707
    LOCATION_ID = 7
    ORDER_QTY = 5

    db = DatabaseConnector(
        target_database_engine=TargetDatabaseEngine.MSSQL,
        target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
    )

    try:
        # Connect to database
        db = (
            db.set_credentials_based_on_connect_option()
            .finalization_of_connection_parameters(
                DRIVER="{ODBC Driver 17 for SQL Server}",
                SERVER="127.0.0.1",
                PORT_NUMBER=13001,
                DATABASE_NAME="AdventureWorks2019",
            )
            .connect_to_database()
        )

        # Begin transaction with READ_COMMITTED isolation level
        db.transaction_manager.begin_transaction(IsolationLevel.READ_COMMITTED)

        try:
            # Transaction operations...
            work_order_insert = """
            INSERT INTO Production.WorkOrder 
                (ProductID, OrderQty, ScrappedQty, StartDate, DueDate, ModifiedDate)
            VALUES 
                (?, ?, 0, SYSDATETIME(), DATEADD(day, 7, SYSDATETIME()), SYSDATETIME())
            """
            db.execute(work_order_insert, (PRODUCT_ID, ORDER_QTY))

            # Commit if successful
            db.transaction_manager.commit()
            print("Transaction committed successfully!")

        except Exception as e:
            # Rollback on error
            db.transaction_manager.rollback()
            raise

    finally:
        db.close()
```

## Detailed Code Analysis

### Decorator Implementation
The decorators serve several key purposes in the transaction management system:

1. `preload_parameters`: 
   - Handles parameter initialization and merging
   - Ensures consistent parameter handling across database operations
   - Provides type safety through validation

2. `ensure_connected`:
   - Acts as a connection guard
   - Validates connection state before operations
   - Prevents operations on closed connections

3. `with_isolation_level`:
   - Manages transaction isolation levels
   - Provides process-aware isolation control
   - Ensures proper cleanup of isolation settings

### Transaction Management Classes
The transaction management system is built around two key enums:

1. `IsolationLevel`:
   - Defines standard SQL isolation levels
   - Provides properties for transaction characteristics
   - Includes helper methods for SQL generation

2. `TransactionType`:
   - Defines core transaction operations
   - Handles SQL statement generation
   - Manages transaction nesting capabilities

### Example Implementation Analysis
The basic transaction example demonstrates:

1. Connection Setup:
   - Database engine selection
   - Credential management
   - Connection parameter configuration

2. Transaction Flow:
   - Explicit transaction control
   - Error handling with rollback
   - Resource cleanup
   - Proper isolation level setting

3. Best Practices:
   - Use of context managers
   - Proper error handling
   - Resource cleanup in finally blocks
   - Explicit transaction boundaries

[🔗 Back to Top](#)