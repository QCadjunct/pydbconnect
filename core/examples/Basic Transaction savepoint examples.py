"""Basic Transaction Example with Savepoints using DatabaseConnector and AdventureWorks2019."""

from core.connector import DatabaseConnector
from core.transaction_manager import IsolationLevel, TransactionManager
from utils.decorators import log_operation, ensure_connected, transactional, retry_on_failure
from templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
    IsolationLevel,
    TransactionType,
)


def demonstrate_transaction_with_savepoints():
    """Demonstrate transaction operations with savepoints for granular control."""
    print("\n=== Starting Transaction with Savepoints Demo ===")

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

        print("Connected to AdventureWorks2019 database")

        # Begin transaction with context manager
        with db.transaction_manager.transaction_scope(IsolationLevel.READ_COMMITTED) as transaction:
            try:
                # 1. Create work order
                work_order_insert = """
                INSERT INTO Production.WorkOrder 
                    (ProductID, OrderQty, ScrappedQty, StartDate, DueDate, ModifiedDate)
                VALUES 
                    (?, ?, 0, SYSDATETIME(), DATEADD(day, 7, SYSDATETIME()), SYSDATETIME())
                """
                sql_parameters = (PRODUCT_ID, ORDER_QTY)
                db.execute(work_order_insert, sql_parameters)

                # Get work order ID
                get_id_query = "SELECT IDENT_CURRENT('Production.WorkOrder') AS WorkOrderID"
                db.execute_query_to_dataframe(get_id_query)
                work_order_id = int(db.to_dataframe()["WorkOrderID"].iloc[0])
                print(f"\nCreated Work Order ID: {work_order_id}")

                # Create savepoint after work order creation
                transaction.create_savepoint("after_work_order")
                print("Created savepoint: after_work_order")

                # 2. Create work order routing
                routing_query = """
                INSERT INTO Production.WorkOrderRouting
                    (WorkOrderID, ProductID, OperationSequence, LocationID, 
                     ScheduledStartDate, ScheduledEndDate, ModifiedDate, PlannedCost)
                VALUES 
                    (?, ?, 1, ?, SYSDATETIME(), 
                     DATEADD(day, 7, SYSDATETIME()), SYSDATETIME(), 100.00)
                """
                sql_parameters = (work_order_id, PRODUCT_ID, LOCATION_ID)
                db.execute(routing_query, sql_parameters)
                print(f"Created Work Order Routing for Order {work_order_id}")

                # Create savepoint after routing creation
                transaction.create_savepoint("after_routing")
                print("Created savepoint: after_routing")

                # 3. Update inventory
                update_inventory_query = """
                UPDATE Production.ProductInventory
                SET Quantity = Quantity - ?
                WHERE ProductID = ? AND LocationID = ?
                """
                sql_parameters = (ORDER_QTY, PRODUCT_ID, LOCATION_ID)
                db.execute(update_inventory_query, sql_parameters)

                # Verify final state
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
                print("\nVerifying Final State:")
                sql_parameters = (work_order_id,)
                db.execute_query_to_prettytable(verification_query, sql_parameters, print_result=True)

                # Simulate error after all operations
                if ORDER_QTY > 10:  # Example condition
                    raise ValueError("Order quantity exceeds threshold")

            except Exception as e:
                print(f"\nError occurred: {str(e)}")
                # Rollback to last savepoint
                if "after_routing" in transaction._savepoints:
                    print("Rolling back to after_routing savepoint...")
                    transaction.rollback_to_savepoint("after_routing")
                elif "after_work_order" in transaction._savepoints:
                    print("Rolling back to after_work_order savepoint...")
                    transaction.rollback_to_savepoint("after_work_order")
                raise

    except Exception as e:
        print(f"\nOuter error occurred: {str(e)}")
        raise
    finally:
        db.close()
        print("\n=== Transaction with Savepoints Demo Completed ===")


if __name__ == "__main__":
    demonstrate_transaction_with_savepoints()
