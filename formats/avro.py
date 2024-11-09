# pydatabaseconnection/formats/avro.py
import fastavro
import pandas as pd
from typing import Dict, Any, Optional, List
from pathlib import Path
from .base import FormatHandler

class AvroHandler(FormatHandler):
    """Handler for Apache Avro format operations"""
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.default_options = {
            "compression": "snappy",
            "sync_interval": 16000,
            "codec": "null"
        }
        self.options = {**self.default_options, **(options or {})}

    def _create_avro_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create Avro schema from DataFrame"""
        type_mapping = {
            'int64': 'long',
            'float64': 'double',
            'object': 'string',
            'bool': 'boolean',
            'datetime64[ns]': {'type': 'long', 'logicalType': 'timestamp-millis'}
        }
        
        fields = []
        for column, dtype in df.dtypes.items():
            avro_type = type_mapping.get(str(dtype), 'string')
            fields.append({
                'name': column,
                'type': ['null', avro_type] if df[column].isnull().any() else avro_type
            })
        
        return {
            'type': 'record',
            'name': 'DataTransfer',
            'fields': fields
        }

    def extract(
        self,
        connection: 'DatabaseConnection',
        table_name: str,
        key_column: str,
        output_dir: Path,
        batch_size: Optional[int] = None
    ) -> Path:
        """Extract data to Avro format"""
        output_path = output_dir / f"{table_name}.avro"
        
        # Get data
        df = connection.execute_sql_to_panda_dataframe(
            f"SELECT * FROM {table_name} ORDER BY {key_column}"
        )
        
        # Create schema
        schema = self._create_avro_schema(df)
        
        # Write to Avro file
        with open(output_path, 'wb') as out:
            fastavro.writer(
                out,
                schema,
                df.to_dict('records'),
                codec=self.options["codec"]
            )
        
        return output_path

    def load(
        self,
        connection: 'DatabaseConnection',
        table_name: str,
        source_path: Path,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Load data from Avro format"""
        records = []
        
        # Read Avro file
        with open(source_path, 'rb') as fo:
            avro_reader = fastavro.reader(fo)
            for record in avro_reader:
                records.append(record)
        
        # Convert to pandas and load to database
        df = pd.DataFrame.from_records(records)
        connection.dataframe_to_table(df, table_name)
        
        return {"rows_transferred": len(df)}

    def cleanup(self, path: Path) -> None:
        """Clean up Avro files"""
        if path.exists():
            path.unlink()
