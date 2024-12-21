"""Database ETL Implementation."""

from typing import Optional, Tuple, List
import os
from pathlib import Path
import pandas as pd

from templates.constraints import (
    FileFormat,
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
)
from core.connector import DatabaseConnector, DatabaseError


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

    def get_metadata_query(self, excluded_tables: Optional[List[str]] = None) -> str:
        """Get metadata query from engine template."""
        engine_config = self.source_db.engine_config[self.source_db.target_database_engine_name]
        metadata_config = engine_config.get("METADATA_QUERIES", {})

        # Handle None case explicitly
        tables = []
        if self.source_db.target_database_engine_connect_option.uses_custom_format:
            tables = excluded_tables if excluded_tables else []
        else:
            tables = metadata_config.get("DEFAULT_EXCLUDED_TABLES", [])

        excluded_list = ", ".join(f"'{table}'" for table in tables)
        query = metadata_config.get("GET_TABLE_METADATA", "")

        return query.format(excluded_tables=excluded_list)

    def _transfer_table_duckdb(self, table_name: str, key_column: str) -> Tuple[bool, int]:
        """Transfer single table with cleanup for DuckDB target."""
        temp_file = self.temp_path / f"{table_name}.{self.file_format.extension}"

        try:
            # Extract data
            df = self.source_db.execute_query_to_dataframe(f"SELECT * FROM {table_name} ORDER BY {key_column}")

            # Save using format-specific writer
            self.file_format.write_dataframe(df, str(temp_file))

            # Create target table
            self.target_db.execute_statement(f"CREATE TABLE {table_name} AS SELECT * FROM '{temp_file}'")

            return True, df.shape[0]

        except Exception as e:
            print(f"Transfer failed for {table_name}: {e}")
            return False, 0
        finally:
            if temp_file.exists():
                temp_file.unlink()

    def _transfer_table(self, table_name: str, key_column: str) -> Tuple[bool, int]:
        """Transfer single table with cleanup."""
        temp_file = self.temp_path / f"{table_name}.{self.file_format.value}"

        try:
            df = self.source_db.execute_query_to_dataframe(f"SELECT * FROM {table_name} ORDER BY {key_column}")

            if self.file_format == FileFormat.PARQUET:
                df.to_parquet(str(temp_file))
            elif self.file_format == FileFormat.CSV:
                df.to_csv(str(temp_file))
            elif self.file_format == FileFormat.JSON:
                df.to_json(str(temp_file))

            self.target_db.execute_statement(f"CREATE TABLE {table_name} AS SELECT * FROM '{temp_file}'")

            return True, df.shape[0]

        except Exception as e:
            print(f"Transfer failed for {table_name}: {e}")
            return False, 0
        finally:
            if temp_file.exists():
                temp_file.unlink()

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
