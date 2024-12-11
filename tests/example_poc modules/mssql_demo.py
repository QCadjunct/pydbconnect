"""MSSQL Connection Demo."""

from core.connector import DatabaseConnector, DatabaseError, ConnectionError
from templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
)


def main():
    """MSSQL connection demonstration."""
    try:
        # Initialize connector
        db = DatabaseConnector(
            target_database_engine=TargetDatabaseEngine.MSSQL,
            target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
        )

        # Demonstrate fluent pattern with context manager
        with (
            db.set_credentials_based_on_connect_option()
            .finalization_of_connection_parameters(
                DRIVER="{ODBC Driver 17 for SQL Server}",
                SERVER="127.0.0.1",
                PORT_NUMBER=13001,
                DATABASE_NAME="AdventureWorks2019",
            )
            .connect_to_database()
        ) as conn:
            print("\nDemonstrating core functionality:")

            print("\n1. Version and Database Check:")
            conn.execute_query_to_prettytable(
                """
                SELECT @@VERSION as Version,
                       DB_NAME() as CurrentDatabase
                """,
                print_result=True,
            )

            print("\n2. Sample Product Query:")
            conn.execute_query_to_prettytable(
                """
                SELECT TOP 5
                    ProductID,
                    Name,
                    ProductNumber,
                    ListPrice
                FROM Production.Product
                ORDER BY ProductID
                """,
                print_result=True,
            )

            print("\n3. Sample Inventory Query:")
            conn.execute_query_to_prettytable(
                """
                SELECT TOP 5
                    ProductID,
                    LocationID,
                    Shelf,
                    Bin,
                    Quantity
                FROM Production.ProductInventory
                ORDER BY ProductID, LocationID
                """,
                print_result=True,
            )

    except ConnectionError as e:
        print(f"Connection error: {e}")
    except DatabaseError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if "db" in locals():
            db.close()
        print("\nDemo completed and connection closed.")


if __name__ == "__main__":
    main()
