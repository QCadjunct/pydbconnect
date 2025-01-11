# examples/transactions/adventure_works_transaction.py
"""Enhanced transaction example with DatabaseConnector using AdventureWorks2019."""

from core.connector import DatabaseConnector
from templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
    IsolationLevel,
    TransactionType,  # Added this import though not directly used in the example
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

        # The transaction_scope usage remains the same, but now uses the enhanced TransactionManager internally
        with db.transaction_manager.transaction_scope(IsolationLevel.SERIALIZABLE):
            print("\nStarting transaction with SERIALIZABLE isolation...")

            # Rest of the code remains identical since the changes were to internal implementation
            # 1. First verify product availability
            product_id = 776  # Specific Mountain Bike
            location_id = 7  # Main warehouse

            # Check current inventory
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
            customer_id = 29825  # Adventure Works customer

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
                0,  # RevisionNumber
                current_date,  # OrderDate
                current_date,  # DueDate
                1,  # Status (In Process)
                1,  # OnlineOrderFlag
                customer_id,  # CustomerID
                4,  # BillToAddressID
                4,  # ShipToAddressID
                1,  # ShipMethodID
                1000.00,  # SubTotal
                80.00,  # TaxAmt
                12.00,  # Freight
            )

            db.execute_query_to_dataframe(header_query, header_params)
            sales_order_id = int(db.to_dataframe()["SalesOrderID"].iloc[0])  # Convert to Python int

            print(f"\nCreated Sales Order Header ID: {sales_order_id}")

            # 3. Create Sales Order Detail
            detail_query = """
            INSERT INTO Sales.SalesOrderDetail 
                (SalesOrderID, OrderQty, ProductID, SpecialOfferID,
                UnitPrice, UnitPriceDiscount)
            VALUES (?, ?, ?, ?, ?, ?)
            """

            detail_params = (
                int(sales_order_id),  # Convert to int
                1,  # OrderQty
                int(product_id),  # Convert to int
                1,  # SpecialOfferID
                1000.00,  # UnitPrice
                0.00,  # UnitPriceDiscount
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
