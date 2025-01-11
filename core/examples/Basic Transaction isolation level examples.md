# 🔄 Transaction Management Implementation Guide

## Table of Contents 
- [Overview](#overview)
- [Code Changes](#changes)
  - [Decorator Updates](#decorator)
  - [Transaction Manager Updates](#transaction-manager)
  - [Final Implementation](#implementation)
- [Best Practices](#best-practices)
- [Testing](#testing)

## Overview <a name="overview"></a> [↑](#table-of-contents)

This guide documents the implementation of transaction management in the database connector framework. The example demonstrates proper transaction handling with SERIALIZABLE isolation level, parameter handling, and type conversions while maintaining a fluent interface design pattern.

## Code Changes <a name="changes"></a> [↑](#table-of-contents)

### Decorator Updates <a name="decorator"></a> [↑](#table-of-contents)

```python
def ensure_connected(f: Callable) -> Callable:
    """
    Decorator to ensure database connection exists before executing a method.
    """
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        # Check for direct connection
        if hasattr(self, "_connection") and self._connection is not None:
            return f(self, *args, **kwargs)
        # Check for connector
        if hasattr(self, "connector") and self.connector.is_database_active:
            return f(self, *args, **kwargs)
        raise RuntimeError("Database connection not established")  # Generic error
    return wrapper
```

### Transaction Manager Updates <a name="transaction-manager"></a> [↑](#table-of-contents)

In `constraints.py`:
```python
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

    @classmethod
    def get_default_type(cls) -> "TransactionType":
        """Get default transaction type."""
        return cls.BEGIN

    @classmethod
    def from_string(cls, value: str) -> "TransactionType":
        """Convert string to transaction type enum."""
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"Invalid transaction type: {value}")
```

### Final Implementation <a name="implementation"></a> [↑](#table-of-contents)

```python
# examples/transactions/adventure_works_transaction.py
"""Enhanced transaction example with DatabaseConnector using AdventureWorks2019."""

from core.connector import DatabaseConnector
from templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
    IsolationLevel,
    TransactionType
)
from datetime import datetime


def demonstrate_order_processing():
    """Show transaction usage with order processing and inventory update."""
    print("\n=== Starting Order Processing Transaction Demo ===")

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

        print("Connected to AdventureWorks2019 database")

        # Transaction scope with SERIALIZABLE isolation
        with db.transaction_manager.transaction_scope(IsolationLevel.SERIALIZABLE):
            print("\nStarting transaction with SERIALIZABLE isolation...")

            # 1. Verify product availability
            product_id = 776  # Mountain Bike
            location_id = 7   # Main warehouse

            inventory_query = """
            SELECT Quantity 
            FROM Production.ProductInventory 
            WHERE ProductID = ? AND LocationID = ?
            """

            db.execute_query_to_dataframe(inventory_query, (product_id, location_id))
            initial_qty = db.to_dataframe()["Quantity"].iloc[0]
            print(f"\nCurrent inventory for ProductID {product_id}: {initial_qty} units")

            if initial_qty < 1:
                raise Exception("Insufficient inventory")

            # 2. Create Sales Order Header
            current_date = datetime.now()
            customer_id = 29825

            header_query = """
            INSERT INTO Sales.SalesOrderHeader 
                (RevisionNumber, OrderDate, DueDate, Status, OnlineOrderFlag,
                CustomerID, BillToAddressID, ShipToAddressID, ShipMethodID,
                SubTotal, TaxAmt, Freight)
            OUTPUT 
                INSERTED.SalesOrderID AS SalesOrderID
            VALUES 
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            header_params = (
                0,             # RevisionNumber
                current_date,  # OrderDate
                current_date,  # DueDate
                1,            # Status (In Process)
                1,            # OnlineOrderFlag
                customer_id,  # CustomerID
                4,            # BillToAddressID
                4,            # ShipToAddressID
                1,            # ShipMethodID
                1000.00,      # SubTotal
                80.00,        # TaxAmt
                12.00,        # Freight
            )

            db.execute_query_to_dataframe(header_query, header_params)
            sales_order_id = int(db.to_dataframe()["SalesOrderID"].iloc[0])

            print(f"\nCreated Sales Order Header ID: {sales_order_id}")

            # 3. Create Sales Order Detail
            detail_query = """
            INSERT INTO Sales.SalesOrderDetail 
                (SalesOrderID, OrderQty, ProductID, SpecialOfferID,
                UnitPrice, UnitPriceDiscount)
            VALUES (?, ?, ?, ?, ?, ?)
            """

            detail_params = (
                int(sales_order_id),  # SalesOrderID
                1,                    # OrderQty
                int(product_id),      # ProductID
                1,                    # SpecialOfferID
                1000.00,              # UnitPrice
                0.00,                 # UnitPriceDiscount
            )

            db.execute(detail_query, detail_params)
            print(f"Created Sales Order Detail for order {sales_order_id}")

            # 4. Update Inventory
            update_inventory_query = """
            UPDATE Production.ProductInventory
            SET Quantity = Quantity - 1
            WHERE ProductID = ? AND LocationID = ?
            """

            db.execute(update_inventory_query, (product_id, location_id))
            print(f"\nUpdated inventory for ProductID {product_id}")

            # Verify final inventory
            db.execute_query_to_dataframe(inventory_query, (product_id, location_id))
            final_qty = db.to_dataframe()["Quantity"].iloc[0]
            print(f"New inventory quantity: {final_qty} units")

            print("\nTransaction completed successfully!")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("Transaction rolled back")
        raise
    finally:
        db.close()
        print("\n=== Transaction Demo Completed ===")


if __name__ == "__main__":
    demonstrate_order_processing()
```

## Best Practices <a name="best-practices"></a> [↑](#table-of-contents)

1. 🔒 **Transaction Isolation**
   - Use appropriate isolation levels for your use case
   - SERIALIZABLE provides strongest isolation but may impact concurrency
   - Consider READ COMMITTED for better performance when full isolation not needed

2. 📊 **Parameter Handling**
   - Always use parameterized queries to prevent SQL injection
   - Convert numpy types to Python native types for SQL parameters
   - Use proper type hints and documentation

3. 🔄 **Transaction Management**
   - Use context managers for automatic transaction handling
   - Implement proper rollback on exceptions
   - Verify transaction state before and after operations

4. 🧪 **Error Handling**
   - Implement comprehensive error handling
   - Provide clear error messages
   - Ensure proper cleanup on errors

## Testing <a name="testing"></a> [↑](#table-of-contents)

1. Run the example with different isolation levels
2. Test error conditions and rollback scenarios
3. Verify proper cleanup of resources
4. Test concurrent transactions for race conditions

[↑ Back to Top](#table-of-contents)