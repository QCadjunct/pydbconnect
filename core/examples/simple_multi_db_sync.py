"""Simple example of synchronizing data between two databases."""

from db_connector.core.multi_connector import MultiDatabaseConnector
from db_connector.templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
)


def main():
    """Demonstrate two-database synchronization."""
    try:
        # Initialize multi-database connector
        multi_db = MultiDatabaseConnector()

        # Attach source database (SQLite3 for example)
        multi_db.attach_database(
            alias="source_db",
            engine_type=TargetDatabaseEngine.SQLITE3,
            connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
        ).prepare_connection("source_db", database="source.db").connect("source_db")

        # Attach target database (PostgreSQL for example)
        multi_db.attach_database(
            alias="target_db",
            engine_type=TargetDatabaseEngine.POSTGRESQL,
            connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndChangeUserPwd,
        ).set_credentials("target_db").prepare_connection(
            "target_db", database="target_db", host="localhost", port=5432
        ).connect(
            "target_db"
        )

        # Get source data
        source_data = multi_db.execute_query("SELECT id, name, value FROM source_table", alias="source_db")

        # Update target database
        for _, row in source_data.iterrows():
            # Check if record exists
            check_query = "SELECT id FROM target_table WHERE id = %s"
            exists = multi_db.execute_query(check_query, alias="target_db", params=(row["id"],))

            with multi_db.transaction("target_db"):
                if exists.empty:
                    # Insert new record
                    insert_query = """
                        INSERT INTO target_table (id, name, value)
                        VALUES (%s, %s, %s)
                    """
                    with multi_db.cursor("target_db") as cursor:
                        cursor.execute(insert_query, (row["id"], row["name"], row["value"]))
                else:
                    # Update existing record
                    update_query = """
                        UPDATE target_table 
                        SET name = %s, value = %s
                        WHERE id = %s
                    """
                    with multi_db.cursor("target_db") as cursor:
                        cursor.execute(update_query, (row["name"], row["value"], row["id"]))

        print("Data synchronization completed successfully")

    except Exception as e:
        print(f"Error during synchronization: {e}")
    finally:
        multi_db.close()


if __name__ == "__main__":
    main()
