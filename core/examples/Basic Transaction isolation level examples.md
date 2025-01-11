# 📚 Transaction Isolation Levels Documentation

## Table of Contents 📑
1. [Introduction](#introduction)
2. [Decorators Implementation](#decorators)
3. [Transaction Manager & Constraints](#constraints)
4. [Basic Examples](#examples)
5. [Code Explanations](#explanations)

[⬆️ Back to TOC](#table-of-contents-)

## Introduction {#introduction}

This document provides a comprehensive overview of transaction isolation levels implementation in Python, including decorators, constraints, and practical examples. The code demonstrates how to manage database transactions with different isolation levels while ensuring proper error handling and connection management.

[⬆️ Back to TOC](#table-of-contents-)

## Decorators Implementation {#decorators}

```python
def with_isolation_level(isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED):
    """Decorator for setting isolation level with process awareness."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            import os

            pid = os.getpid()
            session_id = getattr(self._connection, "spid", None)  # For SQL Server

            original_level = self._current_isolation
            try:
                if session_id:
                    # Log the session info
                    logging.info(f"Setting isolation level for PID {pid}, Session {session_id}")
                self._current_isolation = isolation_level
                return func(self, *args, **kwargs)
            finally:
                self._current_isolation = original_level

        return wrapper

    return decorator

def transactional(nested: bool = False):
    """Decorator for transaction control."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @ensure_connected
        def wrapper(self, *args, **kwargs):
            if not nested and self._transaction_active:
                raise DatabaseError("Transaction already active and nested=False")

            try:
                self.begin_transaction()
                result = func(self, *args, **kwargs)
                self.commit()
                return result
            except Exception:
                self.rollback()
                raise

        return wrapper

    return decorator
```

[⬆️ Back to TOC](#table-of-contents-)

## Transaction Manager & Constraints {#constraints}

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
```

[⬆️ Back to TOC](#table-of-contents-)

## Basic Examples {#examples}

```python
# Basic Transaction Isolation Level Examples

from decorators import with_isolation_level, transactional
from constraints import IsolationLevel
from connector import DatabaseConnector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class TransactionExample:
    def __init__(self, connector: DatabaseConnector):
        self.connector = connector
        self._current_isolation = IsolationLevel.READ_COMMITTED

    @with_isolation_level(IsolationLevel.READ_COMMITTED)
    @transactional()
    def safe_update_balance(self, account_id: int, amount: float) -> None:
        """Update account balance with READ COMMITTED isolation."""
        query = """
        UPDATE accounts 
        SET balance = balance + ?
        WHERE account_id = ?
        """
        self.connector.execute(query, (amount, account_id))

    @with_isolation_level(IsolationLevel.SERIALIZABLE)
    @transactional()
    def transfer_funds(self, from_account: int, to_account: int, amount: float) -> None:
        """Transfer funds between accounts with SERIALIZABLE isolation."""
        # Deduct from source account
        debit_query = """
        UPDATE accounts 
        SET balance = balance - ?
        WHERE account_id = ? AND balance >= ?
        """
        self.connector.execute(debit_query, (amount, from_account, amount))

        # Add to destination account
        credit_query = """
        UPDATE accounts 
        SET balance = balance + ?
        WHERE account_id = ?
        """
        self.connector.execute(credit_query, (amount, to_account))

    @with_isolation_level(IsolationLevel.REPEATABLE_READ)
    @transactional()
    def get_account_summary(self, account_id: int) -> dict:
        """Get account summary with REPEATABLE READ isolation."""
        query = """
        SELECT account_id, balance, last_updated
        FROM accounts
        WHERE account_id = ?
        """
        result = self.connector.execute_query_to_dataframe(query, (account_id,))
        return result.to_dict('records')[0] if not result.empty else None

# Usage example
if __name__ == "__main__":
    # Initialize database connector
    connector = DatabaseConnector(
        target_database_engine=TargetDatabaseEngine.POSTGRESQL,
        target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
    )
    
    # Create transaction example instance
    tx_example = TransactionExample(connector)
    
    try:
        # Perform safe balance update
        tx_example.safe_update_balance(1001, 500.00)
        
        # Transfer funds between accounts
        tx_example.transfer_funds(1001, 1002, 200.00)
        
        # Get account summary
        summary = tx_example.get_account_summary(1001)
        print(f"Account Summary: {summary}")
        
    except Exception as e:
        logging.error(f"Transaction failed: {str(e)}")
    finally:
        connector.close()
```

[⬆️ Back to TOC](#table-of-contents-)

## Code Explanations {#explanations}

### 1. Decorators

The implementation includes two key decorators:

- `with_isolation_level`: Sets the transaction isolation level for a specific operation
  - Takes an IsolationLevel enum value as parameter
  - Preserves the original isolation level using try/finally
  - Logs session information for debugging
  - Process-aware with PID tracking

- `transactional`: Manages transaction boundaries
  - Supports nested transactions through the `nested` parameter
  - Ensures database connection exists through `@ensure_connected`
  - Handles commit/rollback automatically
  - Maintains proper exception propagation

### 2. Isolation Levels

The `IsolationLevel` enum defines standard SQL isolation levels with additional properties:

- Tracks dirty reads, non-repeatable reads, and phantom reads
- Supports snapshot isolation modes
- Provides SQL statement generation
- Includes string conversion and default level selection

### 3. Example Implementation

The example code demonstrates three common transaction scenarios:

1. Safe Balance Updates
   - Uses READ_COMMITTED isolation
   - Single table update with basic concurrency control

2. Fund Transfers
   - Uses SERIALIZABLE isolation for maximum consistency
   - Handles multi-table updates atomically
   - Includes balance validation

3. Account Summaries
   - Uses REPEATABLE_READ isolation
   - Ensures consistent reads during report generation
   - Returns formatted dictionary results

### Key Features

- Process and session awareness
- Automatic connection management
- Proper error handling and logging
- Support for different isolation levels
- Clean API design with decorators
- Type hints for better IDE support

[⬆️ Back to TOC](#table-of-contents-)