"""Complex example of data transfer using MultiDatabaseConnector."""

from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

from db_connector.core.multi_connector import MultiDatabaseConnector, DatabaseError
from db_connector.templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
)


def create_target_table(
    db: MultiDatabaseConnector,
    target_alias: str,
    table_name: str,
    columns: Dict[str, str],
) -> None:
    """Create target table if it doesn't exist."""
    columns_def = [f"{name} {dtype}" for name, dtype in columns.items()]
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join(columns_def)}
    )"""

    with db.transaction(target_alias):
        with db.cursor(target_alias) as cursor:
            cursor.execute(create_query)


def validate_source_data(data: pd.DataFrame, required_columns: List[str]) -> bool:
    """Validate source data meets requirements."""
    missing = set(required_columns) - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    null_counts = data[required_columns].isnull().sum()
    if null_counts.any():
        raise ValueError(f"Null values found in columns: {null_counts[null_counts > 0]}")

    return True


def process_data_batch(
    db: MultiDatabaseConnector,
    target_alias: str,
    table_name: str,
    data: pd.DataFrame,
    batch_size: int = 1000,
) -> int:
    """Process data in batches to target database."""
    total_processed = 0

    for start_idx in range(0, len(data), batch_size):
        batch = data.iloc[start_idx : start_idx + batch_size]

        placeholder = "?" if target_alias == "sqlite_target" else "%s"
        columns = ",".join(data.columns)
        placeholders = ",".join([placeholder] * len(data.columns))

        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        with db.transaction(target_alias):
            with db.cursor(target_alias) as cursor:
                cursor.executemany(insert_query, batch.values.tolist())

        total_processed += len(batch)
        print(f"Processed {total_processed} rows...")

    return total_processed


def transfer_data(
    db: MultiDatabaseConnector,
    source_alias: str,
    target_alias: str,
    source_query: str,
    target_table: str,
    column_mapping: Dict[str, str],
    batch_size: int = 1000,
) -> Dict[str, Any]:
    """Transfer data between databases using multi-connector."""
    stats = {
        "start_time": datetime.now(),
        "total_rows": 0,
        "processed_rows": 0,
        "errors": [],
        "status": "started",
    }

    try:
        # Get source data
        print(f"Fetching source data...")
        source_data = db.execute_query(source_query, source_alias)
        stats["total_rows"] = len(source_data)

        # Validate data
        print("Validating data...")
        validate_source_data(source_data, list(column_mapping.keys()))

        # Create target table
        print("Creating target table...")
        create_target_table(db, target_alias, target_table, column_mapping)

        # Transfer data
        print("Starting data transfer...")
        stats["processed_rows"] = process_data_batch(db, target_alias, target_table, source_data, batch_size)

        stats["status"] = "completed"

    except Exception as e:
        stats["status"] = "failed"
        stats["errors"].append(str(e))
        raise

    finally:
        stats["end_time"] = datetime.now()

    return stats


def main():
    """Demonstrate multi-database data transfer."""
    try:
        # Initialize multi-database connector
        multi_db = MultiDatabaseConnector()

        # Example column mapping
        column_mapping = {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT",
            "value": "TEXT",
            "created_at": "TIMESTAMP",
        }

        # Attach and connect databases
        with multi_db as db:
            # Attach source database (SQLite)
            db.attach_database(
                "sqlite_source",
                TargetDatabaseEngine.SQLITE3,
                TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
            ).prepare_connection("sqlite_source", database="source.db").connect("sqlite_source")

            # Attach target database (PostgreSQL)
            db.attach_database(
                "postgres_target",
                TargetDatabaseEngine.POSTGRESQL,
                TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
            ).prepare_connection("postgres_target", host="localhost", port=5432, database="target_db").set_credentials(
                "postgres_target"
            ).connect(
                "postgres_target"
            )

            # Transfer data
            stats = transfer_data(
                db=db,
                source_alias="sqlite_source",
                target_alias="postgres_target",
                source_query="SELECT * FROM source_table",
                target_table="target_table",
                column_mapping=column_mapping,
                batch_size=1000,
            )

            # Print summary
            print("\nTransfer Summary:")
            print(f"Status: {stats['status']}")
            print(f"Rows Processed: {stats['processed_rows']} of {stats['total_rows']}")
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
