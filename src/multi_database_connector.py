from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import pyodbc
import pandas as pd
from contextlib import contextmanager

@dataclass
class DatabaseInfo:
    """Information about an attached database."""
    name: str
    connection_string: str
    type: str
    is_active: bool = True
    attached_at: datetime = datetime.now()

class MultiDatabaseConnector:
    """
    Multi-database connector supporting different database types.
    Similar to DuckDB's ATTACH functionality.
    """
    
    def __init__(self):
        self.databases: Dict[str, DatabaseInfo] = {}
        self.connections: Dict[str, pyodbc.Connection] = {}
        self.active_database: Optional[str] = None
        self._transaction_db: Optional[str] = None
    
    def attach(self, connection_string: str, name: str, db_type: str) -> None:
        """
        Attach a new database to the system.
        
        Args:
            connection_string: Database connection string
            name: Alias for the database
            db_type: Type of database (mssql, mysql, etc.)
        """
        try:
            conn = pyodbc.connect(connection_string)
            self.databases[name] = DatabaseInfo(
                name=name,
                connection_string=connection_string,
                type=db_type
            )
            self.connections[name] = conn
            
            if not self.active_database:
                self.active_database = name
                
        except pyodbc.Error as e:
            raise ConnectionError(f"Failed to attach database {name}: {str(e)}")

    def use(self, database_name: str) -> None:
        """Switch active database, similar to DuckDB's USE command."""
        if database_name not in self.databases:
            raise ValueError(f"Database {database_name} not attached")
        self.active_database = database_name

    @contextmanager
    def transaction(self):
        """
        Transaction context manager supporting single-database writes.
        Similar to DuckDB's transaction management.
        """
        if not self.active_database:
            raise ValueError("No active database")
            
        conn = self.connections[self.active_database]
        
        try:
            if self._transaction_db and self._transaction_db != self.active_database:
                raise ValueError(
                    f"Attempting to write to database {self.active_database} in a "
                    f"transaction that has already modified database {self._transaction_db}"
                )
                
            conn.autocommit = False
            yield
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
            
        finally:
            conn.autocommit = True
            self._transaction_db = None

    def copy_table(self, 
                   source_db: str, 
                   target_db: str, 
                   table_name: str, 
                   batch_size: int = 1000) -> None:
        """
        Copy table between databases, similar to DuckDB's CREATE TABLE AS.
        
        Args:
            source_db: Source database name
            target_db: Target database name
            table_name: Table to copy
            batch_size: Number of rows to copy at once
        """
        # Get schema from source
        schema_query = f"""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name}'
        """
        
        schema_df = self.query(source_db, schema_query)
        
        # Create table in target
        columns = [f"{row['COLUMN_NAME']} {row['DATA_TYPE']}" 
                  for _, row in schema_df.iterrows()]
        create_query = f"CREATE TABLE {table_name} ({', '.join(columns)})"
        
        self.execute(target_db, create_query)
        
        # Copy data in batches
        offset = 0
        while True:
            data_query = f"""
                SELECT * FROM {table_name} 
                ORDER BY (SELECT NULL) 
                OFFSET {offset} ROWS FETCH NEXT {batch_size} ROWS ONLY
            """
            
            batch_df = self.query(source_db, data_query)
            if batch_df.empty:
                break
                
            # Insert batch
            placeholders = ','.join(['?'] * len(batch_df.columns))
            insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
            
            self.executemany(target_db, insert_query, batch_df.values.tolist())
            offset += batch_size

    def query(self, database_name: str, query: str) -> pd.DataFrame:
        """Execute query and return results as DataFrame."""
        if database_name not in self.connections:
            raise ValueError(f"Database {database_name} not attached")
            
        conn = self.connections[database_name]
        return pd.read_sql(query, conn)

    def execute(self, database_name: str, query: str) -> None:
        """Execute query without returning results."""
        if database_name not in self.connections:
            raise ValueError(f"Database {database_name} not attached")
            
        conn = self.connections[database_name]
        with conn.cursor() as cursor:
            cursor.execute(query)

    def executemany(self, database_name: str, query: str, 
                    parameters: List[Any]) -> None:
        """Execute query with multiple parameter sets."""
        if database_name not in self.connections:
            raise ValueError(f"Database {database_name} not attached")
            
        conn = self.connections[database_name]
        with conn.cursor() as cursor:
            cursor.executemany(query, parameters)

    def get_database_info(self) -> pd.DataFrame:
        """Get information about attached databases."""
        return pd.DataFrame([
            {
                'database_name': db.name,
                'type': db.type,
                'is_active': db.is_active,
                'attached_at': db.attached_at
            }
            for db in self.databases.values()
        ])

    def close(self) -> None:
        """Close all database connections."""
        for conn in self.connections.values():
            conn.close()
        self.connections.clear()
        self.databases.clear()
        self.active_database = None

# Usage Example
def main():
    # Create connector
    mdb = MultiDatabaseConnector()
    
    try:
        # Attach databases
        mdb.attach(
            "DRIVER={ODBC Driver 17 for SQL Server};SERVER=server1;DATABASE=db1;UID=user;PWD=pass",
            "mssql_db",
            "mssql"
        )
        
        mdb.attach(
            "DRIVER={MySQL ODBC 8.0 Driver};SERVER=server2;DATABASE=db2;UID=user;PWD=pass",
            "mysql_db",
            "mysql"
        )
        
        # Use specific database
        mdb.use("mssql_db")
        
        # Transaction example
        with mdb.transaction():
            # Create new table
            mdb.execute("mssql_db", """
                CREATE TABLE new_table (
                    id INT PRIMARY KEY,
                    name VARCHAR(100)
                )
            """)
            
            # Insert data
            mdb.execute("mssql_db", """
                INSERT INTO new_table (id, name) 
                VALUES (1, 'Test')
            """)
        
        # Copy table between databases
        mdb.copy_table("mysql_db", "mssql_db", "users")
        
        # Query across databases
        results = mdb.query("mssql_db", """
            SELECT m.name, y.email
            FROM mssql_db.dbo.users m
            JOIN mysql_db.dbo.profiles y ON m.id = y.user_id
        """)
        
        print(results)
        
    finally:
        mdb.close()

    """    
    if __name__ == "__main__":
        main()
    """