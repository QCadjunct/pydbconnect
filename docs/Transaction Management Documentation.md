# 💼 Transaction Management Implementation Guide

## Table of Contents

- [Transaction Basics](#trans-basics)
- [Isolation Levels](#isolation)
- [Transaction Patterns](#transaction-patterns-)
- [Error Handling](#error-handling)

## 🔄 Transaction Basics [↑](#table-of-contents) {#trans-basics}

### Basic Transaction Structure

```python
def begin_transaction(self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED) -> None:
    """Begin a database transaction with specified isolation level."""
    if not self._connection:
        raise ConnectionError("No database connection")

    try:
        # Set isolation level
        if isolation_level != self._current_isolation:
            self._set_isolation_level(isolation_level)
            
        # Begin transaction
        self._connection.autocommit = False
        self._transaction_active = True
    except Exception as e:
        raise DatabaseError(f"Failed to begin transaction: {str(e)}")
```

### Transaction Usage Example

```python
def transfer_inventory(product_from: int, product_to: int, quantity: int):
    try:
        # Begin transaction
        db.begin_transaction(IsolationLevel.SERIALIZABLE)
        
        # Deduct from source
        db.execute_query("""
            UPDATE Production.ProductInventory 
            SET Quantity = Quantity - ? 
            WHERE ProductID = ?
        """, (quantity, product_from))
        
        # Add to destination
        db.execute_query("""
            UPDATE Production.ProductInventory 
            SET Quantity = Quantity + ? 
            WHERE ProductID = ?
        """, (quantity, product_to))
        
        # Commit if all successful
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise
```

## 🔒 Isolation Levels [↑](#table-of-contents) {#isolation}

### Isolation Level Implementation

```python
def _set_isolation_level(self, level: IsolationLevel) -> None:
    """Set transaction isolation level."""
    with self._cursor() as cursor:
        cursor.execute(level.get_sql_statement())
        self._current_isolation = level

def get_current_isolation_level(self) -> IsolationLevel:
    """Get current transaction isolation level."""
    query = self.engine_config[self.target_database_engine_name][
        "TRANSACTION_MANAGEMENT"
    ]["GET_ISOLATION_LEVEL_QUERY"]
    
    with self._cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()
        return IsolationLevel.from_string(result[0])
```

### Usage in Different Scenarios

```python
# Read operations (default)
db.begin_transaction(IsolationLevel.READ_COMMITTED)

# Critical inventory updates
db.begin_transaction(IsolationLevel.SERIALIZABLE)

# Reporting queries
db.begin_transaction(IsolationLevel.READ_UNCOMMITTED)
```

## Transaction Patterns [↑](#table-of-contents)

## 📋 Transaction Patterns [↑](#table-of-contents)

### Nested Transactions

```python
def handle_nested_transactions(self):
    """Support for nested transactions using savepoints."""
    
    def create_savepoint(name: str) -> None:
        if not self._transaction_active:
            raise DatabaseError("No active transaction")
        
        with self._cursor() as cursor:
            cursor.execute(f"SAVE TRANSACTION {name}")
            self._savepoints.append(name)
    
    def rollback_to_savepoint(name: str) -> None:
        if not self._transaction_active:
            raise DatabaseError("No active transaction")
        
        with self._cursor() as cursor:
            cursor.execute(f"ROLLBACK TRANSACTION {name}")
```

### Decorator-Based Transactions

```python
def transactional(isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED):
    """Decorator for automatic transaction management."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.begin_transaction(isolation_level)
            try:
                result = func(self, *args, **kwargs)
                self.commit()
                return result
            except Exception:
                self.rollback()
                raise
        return wrapper
    return decorator

# Usage
@transactional(IsolationLevel.SERIALIZABLE)
def critical_operation(self, data):
    # Operation runs in transaction automatically
    pass
```

## ⚠️ Error Handling [↑](#table-of-contents) {#error-handling}

### Transaction Error Management

```python
def handle_transaction_error(self, e: Exception) -> None:
    """Handle transaction-related errors."""
    try:
        if self._transaction_active:
            self.rollback()
    except Exception as rollback_error:
        raise DatabaseError(
            f"Failed to rollback transaction after error: {str(e)}. "
            f"Rollback error: {str(rollback_error)}"
        )
    finally:
        self._transaction_active = False
        self._savepoints.clear()
```

### Deadlock Retry Pattern

```python
def with_deadlock_retry(max_retries: int = 3):
    """Decorator for handling deadlock scenarios."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(self, *args, **kwargs)
                except DatabaseError as e:
                    if "deadlock" in str(e).lower() and retries < max_retries - 1:
                        retries += 1
                        time.sleep(0.5 * retries)  # Exponential backoff
                        continue
                    raise
        return wrapper
    return decorator
```
