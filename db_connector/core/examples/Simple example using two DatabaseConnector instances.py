"""Example of using two DatabaseConnector instances for data transfer."""

from db_connector.core.connector import DatabaseConnector
from db_connector.templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
)


def main():
    """Demonstrate using two database instances for data transfer."""
    try:
        # Source database connector
        source_db = DatabaseConnector(
            target_database_engine=TargetDatabaseEngine.SQLITE3,
            target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
        )

        # Target database connector
        target_db = DatabaseConnector(
            target_database_engine=TargetDatabaseEngine.POSTGRESQL,
            target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
        )

        # Connect to source database
        with source_db.finalization_of_connection_parameters(
            database="source.db"
        ).connect_to_database() as source:

            # Connect to target database
            with (
                target_db.finalization_of_connection_parameters(
                    host="localhost", port=5432, database="target_db"
                )
                .set_credentials_based_on_connect_option()
                .connect_to_database() as target
            ):

                # Read data from source
                source_data = source.execute_query_to_dataframe(
                    "SELECT id, name, value FROM source_table"
                )

                # Insert into target
                for _, row in source_data.iterrows():
                    with target.transaction():
                        target.insert(
                            "target_table",
                            {
                                "id": row["id"],
                                "name": row["name"],
                                "value": row["value"],
                            },
                        )

    except DatabaseError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
