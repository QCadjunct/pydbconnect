# In tests/example_poc modules/etl_usage_example.py
from core.connector import DatabaseConnector
from core.etl import DatabaseETL
from templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
    FileFormat,
)


def main():
    """Example ETL usage."""
    try:
        # Initialize source database
        source_db = DatabaseConnector(
            target_database_engine=TargetDatabaseEngine.MSSQL,
            target_database_engine_connect_option=TargetDatabaseConnectionStringOption.CustomizeFormatAndDefaultUserPwd,
        )

        # Initialize target database
        target_db = DatabaseConnector(
            target_database_engine=TargetDatabaseEngine.DUCKDB,
            target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
        )

        # Create ETL handler
        etl = DatabaseETL(
            source_db=source_db,
            target_db=target_db,
            temp_dir="./temp_files",
            file_format=FileFormat.PARQUET,
        )

        # Execute transfer using proper method chain
        with (
            source_db.set_credentials_based_on_connect_option()
            .finalization_of_connection_parameters(DATABASE_NAME="AdventureWorksDW2019")
            .connect_to_database()
        ), (
            target_db.set_credentials_based_on_connect_option()
            .finalization_of_connection_parameters(DATABASE_NAME="AdventureWorksDW2019")
            .connect_to_database()
        ):

            total_tables, total_rows = etl.transfer_tables(
                database_name="AdventureWorksDW2019"
            )
            print(f"Processed {total_tables} tables with {total_rows} total rows")

    except Exception as e:
        print(f"ETL process failed: {e}")


if __name__ == "__main__":
    main()
