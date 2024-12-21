"""Database ETL Implementation."""

from typing import Optional, Tuple, List
from datetime import datetime
from pathlib import Path
import pandas as pd

from templates.constraints import (
    FileFormat,
    TransferMetrics,
)
from core.connector import DatabaseConnector


class DatabaseETL:
    """Database ETL operations using DatabaseConnector."""

    def __init__(
        self,
        source_db: DatabaseConnector,
        target_db: DatabaseConnector,
        temp_dir: str = "./temp_files",
        file_format: FileFormat = FileFormat.PARQUET,
    ):
        """Initialize ETL configuration."""
        self.source_db = source_db
        self.target_db = target_db
        self.temp_path = Path(temp_dir)
        self.file_format = file_format
        self.temp_path.mkdir(parents=True, exist_ok=True)

    def get_column_metadata(self, table_name: str) -> pd.DataFrame:
        """Get column metadata for table."""
        query = f"""
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
        """
        return self.source_db.execute_query_to_dataframe(query)

    def _transfer_table_duckdb(
        self, table_name: str, key_column: str
    ) -> Tuple[bool, int, TransferMetrics]:
        """Transfer single table with cleanup for DuckDB target."""
        start_time = datetime.now()
        temp_file = self.temp_path / f"{table_name}.{self.file_format.value}"

        try:
            # Get column metadata
            columns_df = self.get_column_metadata(table_name)

            # Extract data
            df = self.source_db.execute_query_to_dataframe(
                f"SELECT * FROM {table_name} ORDER BY {key_column}"
            )

            # Save using format-specific writer
            self.file_format.write_dataframe(df, str(temp_file))

            # Create target table
            self.target_db.execute_statement(
                f"CREATE TABLE {table_name} AS SELECT * FROM '{temp_file}'"
            )

            end_time = datetime.now()

            metrics = TransferMetrics(
                table_name=table_name,
                start_time=start_time,
                end_time=end_time,
                row_count=df.shape[0],
                duration_seconds=(end_time - start_time).total_seconds(),
                source_columns=len(columns_df),
                target_columns=len(columns_df),  # Same for DuckDB
                source_data_types=columns_df["DATA_TYPE"].tolist(),
                target_data_types=columns_df["DATA_TYPE"].tolist(),  # DuckDB preserves types
            )

            return True, df.shape[0], metrics

        except Exception as e:
            print(f"Transfer failed for {table_name}: {e}")
            metrics = TransferMetrics(
                table_name=table_name,
                start_time=start_time,
                end_time=datetime.now(),
                row_count=0,
                duration_seconds=0,
                source_columns=0,
                target_columns=0,
                source_data_types=[],
                target_data_types=[],
            )
            return False, 0, metrics
        finally:
            if temp_file.exists():
                temp_file.unlink()

    def transfer_tables(
        self, database_name: str, excluded_tables: Optional[List[str]] = None
    ) -> Tuple[int, int, List[TransferMetrics]]:
        """Transfer all tables with metrics."""
        total_tables = 0
        total_rows = 0
        metrics = []

        try:
            metadata_query = self.get_metadata_query(excluded_tables)
            metadata_df = self.source_db.execute_query_to_dataframe(metadata_query)

            for _, row in metadata_df.iterrows():
                success, rows, metric = self._transfer_table_duckdb(
                    row["TABLE_NAME"], row["table_name_key"]
                )
                if success:
                    total_tables += 1
                    total_rows += rows
                    if metric:
                        metrics.append(metric)

            return total_tables, total_rows, metrics

        finally:
            self._cleanup_temp_files()

    def get_metadata_query(self, excluded_tables: Optional[List[str]] = None) -> str:
        """Generate metadata query to get table information."""
        excluded_tables_clause = ""
        if excluded_tables:
            excluded_tables_list = ", ".join(f"'{table}'" for table in excluded_tables)
            excluded_tables_clause = f"AND TABLE_NAME NOT IN ({excluded_tables_list})"

        query = f"""
        SELECT
            TABLE_NAME,
            COLUMN_NAME AS table_name_key
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        {excluded_tables_clause}
        """
        return query

    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files."""
        for file in self.temp_path.glob(f"*.{self.file_format.value}"):
            try:
                file.unlink()
            except Exception:
                pass
        try:
            self.temp_path.rmdir()
        except Exception:
            pass
