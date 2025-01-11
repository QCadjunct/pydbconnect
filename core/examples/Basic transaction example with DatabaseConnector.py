"""Basic Transaction Example with DatabaseConnector using AdventureWorks2019."""

from core.connector import DatabaseConnector
from templates.constraints import TargetDatabaseEngine, TargetDatabaseConnectionStringOption, IsolationLevel
from datetime import datetime


def demonstrate_basic_transaction():
    """Demonstrate basic transaction operations with explicit transaction control."""
    print("\n=== Starting Basic Transaction Demo ===")

    # Constants for the transaction
    PRODUCT_ID = 707
    LOCATION_ID = 7  # Changed from 1 to 7
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

        print("Connected to AdventureWorks2019 database")

        # First verify product exists and get details
        product_check_query = """
        SELECT p.ProductID, 
               p.Name AS ProductName,
               pi.LocationID,
               pi.Quantity AS CurrentStock
        FROM Production.Product p
        INNER JOIN Production.ProductInventory pi 
            ON p.ProductID = pi.ProductID
        WHERE p.ProductID = ? AND pi.LocationID = ?
        """

        print("\nVerifying product exists:")
        db.execute_query_to_prettytable(product_check_query, (PRODUCT_ID, LOCATION_ID), print_result=True)

        # Explicitly begin transaction
        print("\nExplicitly beginning transaction...")
        db.transaction_manager.begin_transaction(IsolationLevel.READ_COMMITTED)

        try:
            # 1. Insert a new work order
            work_order_insert = """
            INSERT INTO Production.WorkOrder 
                (ProductID, OrderQty, ScrappedQty, StartDate, DueDate, ModifiedDate)
            VALUES 
                (?, ?, 0, SYSDATETIME(), DATEADD(day, 7, SYSDATETIME()), SYSDATETIME())
            """
            db.execute(work_order_insert, (PRODUCT_ID, ORDER_QTY))

            # Get the ID using a separate query
            get_id_query = "SELECT IDENT_CURRENT('Production.WorkOrder') AS WorkOrderID"
            db.execute_query_to_dataframe(get_id_query)
            df = db.to_dataframe()
            work_order_id = int(df["WorkOrderID"].iloc[0])
            print(f"\nCreated Work Order ID: {work_order_id}")

            # 2. Insert work order routing
            routing_query = """
            INSERT INTO Production.WorkOrderRouting
                (WorkOrderID, ProductID, OperationSequence, LocationID, 
                 ScheduledStartDate, ScheduledEndDate, ModifiedDate, PlannedCost)
            VALUES 
                (?, ?, 1, ?, SYSDATETIME(), 
                 DATEADD(day, 7, SYSDATETIME()), SYSDATETIME(), 100.00)
            """
            db.execute(routing_query, (work_order_id, PRODUCT_ID, LOCATION_ID))
            print(f"Created Work Order Routing for Order {work_order_id}")

            # 3. Get current inventory
            get_inventory_query = """
            SELECT p.ProductID, 
                   p.Name AS ProductName,
                   pi.LocationID,
                   pi.Quantity AS CurrentStock
            FROM Production.Product p
            INNER JOIN Production.ProductInventory pi 
                ON p.ProductID = pi.ProductID
            WHERE p.ProductID = ? AND pi.LocationID = ?
            """
            db.execute_query_to_dataframe(get_inventory_query, (PRODUCT_ID, LOCATION_ID))
            df = db.to_dataframe()

            if len(df) == 0:
                raise Exception(f"No inventory found for ProductID {PRODUCT_ID} at LocationID {LOCATION_ID}")

            old_quantity = int(df["CurrentStock"].iloc[0])

            # 4. Update inventory
            update_inventory_query = """
            UPDATE Production.ProductInventory
            SET Quantity = Quantity - ?
            WHERE ProductID = ? AND LocationID = ?
            """
            db.execute(update_inventory_query, (ORDER_QTY, PRODUCT_ID, LOCATION_ID))

            # 5. Get updated inventory
            db.execute_query_to_dataframe(get_inventory_query, (PRODUCT_ID, LOCATION_ID))
            df = db.to_dataframe()
            new_quantity = int(df["CurrentStock"].iloc[0])

            print("\nInventory Update Results:")
            print(f"Product ID: {PRODUCT_ID}")
            print(f"Location ID: {LOCATION_ID}")
            print(f"Old Quantity: {old_quantity}")
            print(f"New Quantity: {new_quantity}")

            # 6. Verify changes
            verification_query = """
            SELECT 
                wo.WorkOrderID,
                wo.ProductID,
                wo.OrderQty,
                wor.OperationSequence,
                wor.LocationID,
                pi.Quantity as CurrentInventory,
                p.Name as ProductName
            FROM Production.WorkOrder wo
            JOIN Production.WorkOrderRouting wor 
                ON wo.WorkOrderID = wor.WorkOrderID
            JOIN Production.ProductInventory pi 
                ON wo.ProductID = pi.ProductID
                AND wor.LocationID = pi.LocationID
            JOIN Production.Product p
                ON wo.ProductID = p.ProductID
            WHERE wo.WorkOrderID = ?
            """
            print("\nVerifying Changes:")
            db.execute_query_to_prettytable(verification_query, (work_order_id,), print_result=True)

            # Explicitly commit transaction
            print("\nExplicitly committing transaction...")
            db.transaction_manager.commit()
            print("Transaction committed successfully!")

        except Exception as e:
            # Explicitly rollback transaction
            print(f"\nError occurred: {str(e)}")
            print("Explicitly rolling back transaction...")
            db.transaction_manager.rollback()
            raise

    except Exception as e:
        print(f"\nOuter error occurred: {str(e)}")
        raise
    finally:
        db.close()
        print("\n=== Transaction Demo Completed ===")


if __name__ == "__main__":
    demonstrate_basic_transaction()
