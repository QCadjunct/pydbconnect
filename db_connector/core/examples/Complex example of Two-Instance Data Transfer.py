"""Example of data transfer between two database instances."""

from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

from db_connector.core.connector import DatabaseConnector, DatabaseError
from db_connector.templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
)


def create_target_table(
    db: DatabaseConnector, table_name: str, columns: Dict[str, str]
) -> None:
    """Create target table if doesn't exist."""
    columns_def = [f"{name} {dtype}" for name, dtype in columns.items()]
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join(columns_def)}
    )"""

    # Using execute_ddl instead of direct cursor access
    db.execute_ddl(create_query)


def validate_data(data: pd.DataFrame, required_columns: List[str]) -> bool:
    """Simple data validation."""
    # Check required columns exist
    if not all(col in data.columns for col in required_columns):
        missing = set(required_columns) - set(data.columns)
        raise ValueError(f"Missing required columns: {missing}")

    # Check for null values in required columns
    null_counts = data[required_columns].isnull().sum()
    if null_counts.any():
        raise ValueError(
            f"Null values found in columns: {null_counts[null_counts > 0]}"
        )

    return True


def process_batch(
    target_db: DatabaseConnector,
    table_name: str,
    data: pd.DataFrame,
    batch_size: int = 1000,
) -> int:
    """Process data in batches."""
    total_processed = 0

    for start_idx in range(0, len(data), batch_size):
        batch = data.iloc[start_idx : start_idx + batch_size]

        # Process each row in the batch
        for _, row in batch.iterrows():
            target_db.insert(table_name, row.to_dict())

        total_processed += len(batch)
        print(f"Processed {total_processed} rows...")

    return total_processed


def transfer_data(
    source_db: DatabaseConnector,
    target_db: DatabaseConnector,
    source_query: str,
    target_table: str,
    column_mapping: Dict[str, str],
    batch_size: int = 1000,
) -> Dict[str, Any]:
    """Transfer data between databases with progress tracking."""
    start_time = datetime.now()
    stats = {
        "total_rows": 0,
        "processed_rows": 0,
        "errors": [],
        "start_time": start_time,
        "end_time": None,
        "status": "started",
    }

    try:
        # Get source data
        print(f"Fetching source data at {datetime.now()}")
        source_data = source_db.execute_query_to_dataframe(source_query)
        stats["total_rows"] = len(source_data)

        # Create target table
        print(f"Creating target table at {datetime.now()}")
        create_target_table(target_db, target_table, column_mapping)

        # Validate data
        print(f"Validating data at {datetime.now()}")
        validate_data(source_data, list(column_mapping.keys()))

        # Process in batches
        print(f"Starting batch processing at {datetime.now()}")
        stats["processed_rows"] = process_batch(
            target_db, target_table, source_data, batch_size
        )

        stats["status"] = "completed"
        print(f"Processed {stats['processed_rows']} of {stats['total_rows']} rows")

    except Exception as e:
        stats["status"] = "failed"
        stats["errors"].append(str(e))
        print(f"Error during transfer: {e}")
        raise

    finally:
        stats["end_time"] = datetime.now()
        duration = stats["end_time"] - stats["start_time"]
        print(f"Transfer {stats['status']} in {duration}")

    return stats


def main():
    """Demonstrate data transfer between two database instances."""
    try:
        # Initialize database connectors
        source_db = DatabaseConnector(
            target_database_engine=TargetDatabaseEngine.SQLITE3,
            target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
        )

        target_db = DatabaseConnector(
            target_database_engine=TargetDatabaseEngine.POSTGRESQL,
            target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
        )

        # Example column mapping
        column_mapping = {
            "id": "INTEGER PRIMARY KEY",
            "name": "VARCHAR(100)",
            "value": "TEXT",
            "created_at": "TIMESTAMP",
        }

        # Connect and transfer
        with source_db.finalization_of_connection_parameters(
            database="source.db"
        ).connect_to_database() as source:

            with (
                target_db.finalization_of_connection_parameters(
                    host="localhost", port=5432, database="target_db"
                )
                .set_credentials_based_on_connect_option()
                .connect_to_database() as target
            ):

                # Transfer data
                stats = transfer_data(
                    source_db=source,
                    target_db=target,
                    source_query="SELECT * FROM source_table",
                    target_table="target_table",
                    column_mapping=column_mapping,
                    batch_size=1000,
                )

                # Print summary
                print("\nTransfer Summary:")
                print(f"Status: {stats['status']}")
                print(f"Total Rows: {stats['total_rows']}")
                print(f"Processed Rows: {stats['processed_rows']}")
                print(f"Duration: {stats['end_time'] - stats['start_time']}")
                if stats["errors"]:
                    print("\nErrors:")
                    for error in stats["errors"]:
                        print(f"- {error}")

    except DatabaseError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
