# pydatabaseconnection/formats/sql.py
from typing import Dict, Any, Optional, List
from pathlib import Path
import sqlalchemy as sa
from .base import FormatHandler

class SQLHandler(FormatHandler):
    """Handler for SQL format operations"""
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.default_options = {
            "include_schema": True,
            "include_data": True,
            "include_indexes": True,
            "batch_size": 5000,
            "transaction_size": 1000
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
        """Extract data to SQL format"""
        output_path = output_dir / f"{table_name}.sql"
        
        with output_path.open('w') as f:
            # Write schema if requested
            if self.options["include_schema"]:
                schema_sql = self._get_schema_sql(connection, table_name)
                f.write(f"{schema_sql}\n\n")
            
            # Write data if requested
            if self.options["include_data"]:
                self._write_data_sql(
                    f,
                    connection,
                    table_name,
                    key_column,
                    batch_size or self.options["batch_size"]
                )
            
            # Write indexes if requested
            if self.options["include_indexes"]:
                index_sql = self._get_index_sql(connection, table_name)
                f.write(f"\n{index_sql}\n")
        
        return output_path

    def load(
        self,
        connection: 'DatabaseConnection',
        table_name: str,
        source_path: Path,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Load data from SQL format"""
        rows_transferred = 0
        
        # Read SQL file in chunks to avoid memory issues
        with source_path.open('r') as f:
            current_statement = []
            
            for line in f:
                line = line.strip()
                
                if not line or line.startswith('--'):
                    continue
                
                current_statement.append(line)
                
                if line.endswith(';'):
                    # Execute complete statement
                    sql = ' '.join(current_statement)
                    connection.execute(sql)
                    current_statement = []
                    
                    # Count inserted rows if this was an INSERT statement
                    if sql.upper().startswith('INSERT'):
                        rows_transferred += 1
        
        return {"rows_transferred": rows_transferred}

    def cleanup(self, path: Path) -> None:
        """Clean up SQL files"""
        if path.exists():
            path.unlink()

    def _get_schema_sql(
        self,
        connection: 'DatabaseConnection',
        table_name: str
    ) -> str:
        """Get CREATE TABLE SQL"""
        return connection.execute(
            f"SHOW CREATE TABLE {table_name}"
        ).fetchone()[1]

    def _write_data_sql(
        self,
        file,
        connection: 'DatabaseConnection',
        table_name: str,
        key_column: str,
        batch_size: int
    ) -> None:
        """Write INSERT statements in batches"""
        query = f"SELECT * FROM {table_name} ORDER BY {key_column}"
        
        for chunk in connection.execute_sql_in_chunks(query, batch_size):
            insert_sql = self._get_insert_sql(table_name, chunk)
            file.write(f"{insert_sql}\n")

    def _get_insert_sql(
        self,
        table_name: str,
        df: 'pd.DataFrame'
    ) -> str:
        """Generate INSERT statement for DataFrame"""
        columns = df.columns.tolist()
        values_template = ','.join(['%s'] * len(columns))
        
        return f"INSERT INTO {table_name} ({','.join(columns)}) VALUES {values_template};"

    def _get_index_sql(
        self,
        connection: 'DatabaseConnection',
        table_name: str
    ) -> str:
        """Get CREATE INDEX statements"""
        return connection.execute(
            f"SHOW INDEXES FROM {table_name}"
        ).fetchall()
