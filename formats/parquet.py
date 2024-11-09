# pydatabaseconnection/formats/parquet.py
import pyarrow as pa
import pyarrow.parquet as pq
from typing import Dict, Any, Optional
from pathlib import Path
from .base import FormatHandler

class ParquetHandler(FormatHandler):
    """Handler for Parquet format operations"""
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.default_options = {
            "compression": "snappy",
            "row_group_size": 100000,
            "use_dictionary": True,
            "write_statistics": True
        }
        self.options = {**self.default_options, **(options or {})}

    def extract(
        self,
        connection: 'DatabaseConnection',
        table_name: str,
        key_column: str,
        output_dir: Path,
        batch_size: Optional[int] = None
    ) -> Path:
        """Extract data to Parquet format"""
        output_path = output_dir / f"{table_name}.parquet"
        
        # Get data from source
        df = connection.execute_sql_to_panda_dataframe(
            f"SELECT * FROM {table_name} ORDER BY {key_column}"
        )
        
        # Convert to Arrow table
        table = pa.Table.from_pandas(df)
        
        # Write to Parquet
        pq.write_table(
            table,
            str(output_path),
            compression=self.options["compression"],
            row_group_size=self.options["row_group_size"],
            use_dictionary=self.options["use_dictionary"],
            write_statistics=self.options["write_statistics"]
        )
        
        return output_path

    def load(
        self,
        connection: 'DatabaseConnection',
        table_name: str,
        source_path: Path,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Load data from Parquet format"""
        # Read Parquet metadata
        parquet_file = pq.ParquetFile(source_path)
        num_rows = parquet_file.metadata.num_rows
        
        if connection.template_manager.target_engine == "DUCKDB":
            # DuckDB can directly query Parquet files
            connection.execute(
                f"CREATE TABLE {table_name} AS SELECT * FROM '{source_path}'"
            )
        else:
            # For other databases, load through pandas
            table = pq.read_table(source_path)
            df = table.to_pandas()
            connection.dataframe_to_table(df, table_name)
        
        return {"rows_transferred": num_rows}

    def cleanup(self, path: Path) -> None:
        """Clean up Parquet files"""
        if path.exists():
            path.unlink()
