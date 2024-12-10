from core.connector import DatabaseConnector
from templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
)
from core.exceptions import ConnectionError, DatabaseError


def main():
    """MSSQL connection demonstration."""
    try:
        # Initialize connector
        db = DatabaseConnector(
            target_database_engine=TargetDatabaseEngine.MSSQL,
            target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
        )

        # Set up connection using template parameters
        db.set_credentials_based_on_connect_option().finalization_of_connection_parameters(
            DRIVER="{ODBC Driver 17 for SQL Server}",
            SERVER="127.0.0.1",
            PORT_NUMBER=13001,
            DATABASE_NAME="AdventureWorks2019",
        ).connect_to_database()

        print("\nSQL Server Version:")
        db.execute_query_to_prettytable(
            "SELECT @@VERSION as Version", print_result=True
        )

        print("\nQuerying Product Inventory:")
        db.execute_query_to_prettytable(
            """
            SELECT *
            FROM [AdventureWorks2019].[Production].[ProductInventory]
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
        print("\nTest completed and connection closed.")


if __name__ == "__main__":
    main()
