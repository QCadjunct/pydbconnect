"""Example ETL transfer from AdventureWorksDW2019 to DuckDB."""

from datetime import datetime
from pathlib import Path
import sys
from typing import List, Tuple

sys.path.append(str(Path(__file__).parent.parent))

from templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
    FileFormat,
    TransferMetrics,
)
from core.connector import DatabaseConnector
from utils.decorators import etl_transfer


def initialize_source_db() -> DatabaseConnector:
    """Initialize MSSQL source connection."""
    return (
        DatabaseConnector(
            target_database_engine=TargetDatabaseEngine.MSSQL,
            target_database_engine_connect_option=TargetDatabaseConnectionStringOption.CustomizeFormatAndDefaultUserPwd,
        )
        .set_credentials_based_on_connect_option()
        .finalization_of_connection_parameters(
            SERVER="127.0.0.1", PORT_NUMBER=13001, DATABASE_NAME="AdventureWorksDW2019"
        )
        .connect_to_database()
    )


def initialize_target_db() -> DatabaseConnector:
    """Initialize DuckDB target connection."""
    return (
        DatabaseConnector(
            target_database_engine=TargetDatabaseEngine.DUCKDB,
            target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
        )
        .finalization_of_connection_parameters(
            FULLY_QUALIFIED_PATH="Q:\\Database\\AdventureWorksDW",
            DATABASE_NAME="AdventureWorksDW2019.duckdb",
        )
        .connect_to_database()
    )


@etl_transfer(
    source_db=initialize_source_db(),
    target_db=initialize_target_db(),
    temp_dir="./temp_etl_files",
    file_format=FileFormat.PARQUET,
)
def transfer_adventureworks(
    source: DatabaseConnector,
    target: DatabaseConnector,
    temp_path: Path,
    file_format: FileFormat,
    process_start: datetime,
) -> Tuple[int, int, List[TransferMetrics]]:
    """Transfer AdventureWorksDW tables to DuckDB."""
    metadata_df = source.execute_query_to_dataframe(
        source.engine_config[source.target_database_engine_name]["METADATA_QUERIES"][
            "GET_TABLE_METADATA"
        ]
    )

    metrics: List[TransferMetrics] = []
    total_tables = total_rows = 0

    for _, row in metadata_df.iterrows():
        table_start = datetime.now()

        df = source.execute_query_to_dataframe(f"SELECT * FROM {row['TABLE_NAME']}")
        file_path = temp_path / f"{row['TABLE_NAME']}.{file_format.value}"
        df.to_parquet(str(file_path), index=False)

        target.execute_ddl(f"CREATE TABLE {row['TABLE_NAME']} AS SELECT * FROM '{str(file_path)}'")

        table_end = datetime.now()
        metrics.append(
            TransferMetrics(
                row["TABLE_NAME"],
                table_start,
                table_end,
                df.shape[0],
                (table_end - table_start).total_seconds(),
            )
        )

        total_tables += 1
        total_rows += df.shape[0]

    return total_tables, total_rows, metrics


def main():
    """Execute ETL transfer."""
    try:
        print("Starting AdventureWorksDW2019 to DuckDB transfer...")
        total_tables, total_rows, metrics = transfer_adventureworks()

        print("\nTransfer Results:")
        print(f"Total Tables: {total_tables:,}")
        print(f"Total Rows: {total_rows:,}")
        print("\nDetailed Metrics:")
        for metric in metrics:
            print(str(metric))

    except Exception as e:
        print(f"Transfer failed: {e}")


if __name__ == "__main__":
    main()
