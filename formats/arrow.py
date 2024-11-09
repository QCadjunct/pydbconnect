# pydatabaseconnection/formats/arrow.py
import pyarrow as pa
from pyarrow import ipc
from typing import Dict, Any, Optional
from pathlib import Path
from .base import FormatHandler

class ArrowHandler(FormatHandler):
    """Handler for Apache Arrow format operations"""
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.default_options = {
            "use_memory_map": True,
            "compression": "lz4",
            "batch_size": 100000,
            "use_threads": True
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
        """Extract data to Arrow format"""
        output_path = output_dir / f"{table_name}.arrow"
        
        # Get data as pandas DataFrame
        df = connection.execute_sql_to_panda_dataframe(
            f"SELECT * FROM {table_name} ORDER BY {key_column}"
        )
        
        # Convert to Arrow Table
        table = pa.Table.from_pandas(df)
        
        # Write to Arrow file
        with pa.OSFile(str(output_path), 'wb') as sink:
            with ipc.new_file(sink, table.schema) as writer:
                writer.write_table(table)
        
        return output_path

    def load(
        self,
        connection: 'DatabaseConnection',
        table_name: str,
        source_path: Path,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Load data from Arrow format"""
        # Read Arrow file
        with pa.memory_map(str(source_path), 'rb') as source:
            reader = ipc.open_file(source)
            table = reader.read_all()
        
        # Convert to pandas and load to database
        df = table.to_pandas()
        connection.dataframe_to_table(df, table_name)
        
        return {"rows_transferred": len(df)}

    def cleanup(self, path: Path) -> None:
        """Clean up Arrow files"""
        if path.exists():
            path.unlink()
