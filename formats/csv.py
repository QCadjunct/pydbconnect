# pydatabaseconnection/formats/csv.py
import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path
from .base import FormatHandler

class CSVHandler(FormatHandler):
    """Handler for CSV format operations"""
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.default_options = {
            "sep": ",",
            "encoding": "utf-8",
            "quoting": 1,  # csv.QUOTE_ALL
            "compression": None,
            "chunksize": 100000
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
        """Extract data to CSV format"""
        output_path = output_dir / f"{table_name}.csv"
        
        query = f"SELECT * FROM {table_name} ORDER BY {key_column}"
        
        if batch_size:
            # Batch processing for large tables
            with pd.io.sql.get_handle(
                str(output_path),
                'w',
                encoding=self.options["encoding"],
                compression=self.options["compression"]
            ) as handle:
                first_chunk = True
                for chunk in connection.execute_sql_in_chunks(query, batch_size):
                    chunk.to_csv(
                        handle,
                        index=False,
                        header=first_chunk,
                        sep=self.options["sep"],
                        quoting=self.options["quoting"]
                    )
                    first_chunk = False
        else:
            # Single operation for smaller tables
            df = connection.execute_sql_to_panda_dataframe(query)
            df.to_csv(
                output_path,
                index=False,
                sep=self.options["sep"],
                encoding=self.options["encoding"],
                compression=self.options["compression"],
                quoting=self.options["quoting"]
            )
        
        return output_path

    def load(
        self,
        connection: 'DatabaseConnection',
        table_name: str,
        source_path: Path,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Load data from CSV format"""
        rows_transferred = 0
        
        # Read CSV in chunks
        for chunk in pd.read_csv(
            source_path,
            sep=self.options["sep"],
            encoding=self.options["encoding"],
            compression=self.options["compression"],
            chunksize=self.options["chunksize"]
        ):
            if rows_transferred == 0:
                # Create table on first chunk
                connection.dataframe_to_table(
                    chunk,
                    table_name,
                    if_exists="replace"
                )
            else:
                # Append subsequent chunks
                connection.dataframe_to_table(
                    chunk,
                    table_name,
                    if_exists="append"
                )
            
            rows_transferred += len(chunk)
        
        return {"rows_transferred": rows_transferred}

    def cleanup(self, path: Path) -> None:
        """Clean up CSV files"""
        if path.exists():
            path.unlink()
