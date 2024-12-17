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
        print("\nInitializing connector...")
        db = DatabaseConnector(
            target_database_engine=TargetDatabaseEngine.MSSQL,
            target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
        )

        # Test connection
        print("\nTesting connection...")
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
            print("\nExecuting queries...")

            # Version check
            print("\n1. SQL Server Version:")
            conn.execute_query_to_prettytable(
                "SELECT @@VERSION as Version", print_result=True
            )

            # Product query
            print("\n2. Sample Products:")
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

    except ConnectionError as e:
        print(f"\nConnection error: {e}")
    except DatabaseError as e:
        print(f"\nDatabase error: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        if "db" in locals():
            db.close()
        print("\nDemo completed.")


if __name__ == "__main__":
    main()
