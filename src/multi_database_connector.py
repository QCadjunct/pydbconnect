# multi_database_connector.py
from getpass import getpass
import logging
from typing import Any, Dict, Optional, Union, List
from contextlib import contextmanager
import importlib
import pandas as pd
from pandas import DataFrame
from prettytable import PrettyTable
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from dataclasses import dataclass
from .base_database_connector import BaseDatabaseConnector, DatabaseError
from .db_templates.database_target_engine_template_modules import (
    MSSQL, MYSQL, POSTGRESQL, PSYCOPG2, SQLITE3, DUCKDB as template
)
from .db_templates.database_target_engine_modules_enum_contraints import (
    TargetDatabaseEngine, TargetDatabaseConnectionStringOption
)

@dataclass
class DatabaseInstance:
    """Information about an attached database instance."""
    name: str
    engine_type: TargetDatabaseEngine
    connection_options: TargetDatabaseConnectionStringOption
    is_active: bool = True
    attached_at: datetime = datetime.now()

class MultiDatabaseConnector(BaseDatabaseConnector):
    """
    Multi-database connector supporting different database types.
    Implements template-based connection management with multiple database support.
    """
    
    def __init__(self):
        """Initialize multi-database connector."""
        super().__init__()
        self.instances: Dict[str, DatabaseInstance] = {}
        self.connections: Dict[str, Any] = {}
        self.active_instance: Optional[str] = None
        self._transaction_instance: Optional[str] = None
        self._logger = logging.getLogger(__name__)

    def attach(self, 
               name: str,
               engine_type: TargetDatabaseEngine,
               connect_option: TargetDatabaseConnectionStringOption) -> 'MultiDatabaseConnector':
        """
        Attach a new database instance using template configuration.
        
        Args:
            name: Alias for the database instance
            engine_type: Type of database engine
            connect_option: Standardized connection options
            
        Returns:
            Self for method chaining
        """
        try:
            self.target_database_engine_name = engine_type.name
            self.connect_option = connect_option
            self.engine_config = self._load_engine_config()
            
            # Finalize connection parameters
            self.finalization_of_connection_parameters()
            
            # Create connection using template
            connection = self._create_database_connection()
            
            # Store instance information
            self.instances[name] = DatabaseInstance(
                name=name,
                engine_type=engine_type,
                connection_options=connect_option
            )
            self.connections[name] = connection
            
            # Set as active if first instance
            if not self.active_instance:
                self.active_instance = name
                self._connection = connection
            
            self._logger.info(f"Successfully attached database: {name}")
            return self
            
        except Exception as e:
            self._logger.error(f"Failed to attach database {name}: {str(e)}")
            raise DatabaseError(f"Failed to attach database {name}: {str(e)}")

    def _load_engine_config(self) -> Dict[str, Any]:
        """Load engine-specific configuration from templates."""
        try:
            return getattr(template, self.target_database_engine_name)
        except AttributeError as e:
            raise DatabaseError(f"Unsupported database engine: {self.target_database_engine_name}")

    def _create_database_connection(self) -> Any:
        """Create database connection using template configuration."""
        try:
            module_name = self.engine_config['MODULE']
            module = importlib.import_module(module_name)
            return module.connect(self._connection_string)
        except Exception as e:
            raise DatabaseError(f"Failed to create database connection: {str(e)}")

    def use(self, instance_name: str) -> 'MultiDatabaseConnector':
        """
        Switch active database instance.
        
        Args:
            instance_name: Name of the instance to make active
            
        Returns:
            Self for method chaining
        """
        if instance_name not in self.instances:
            raise DatabaseError(f"Instance {instance_name} not attached")
        
        self.active_instance = instance_name
        self._connection = self.connections[instance_name]
        instance = self.instances[instance_name]
        self.target_database_engine_name = instance.engine_type.name
        self.connect_option = instance.connection_options
        
        self._logger.info(f"Switched to database instance: {instance_name}")
        return self

    @contextmanager
    def transaction(self, instance_name: Optional[str] = None):
        """
        Transaction context manager for single-instance operations.
        
        Args:
            instance_name: Optional instance name, uses active instance if not specified
        """
        target_instance = instance_name or self.active_instance
        if not target_instance:
            raise DatabaseError("No active database instance")
            
        if target_instance not in self.connections:
            raise DatabaseError(f"Instance {target_instance} not attached")
            
        connection = self.connections[target_instance]
        
        try:
            if self._transaction_instance and self._transaction_instance != target_instance:
                raise DatabaseError(
                    f"Cannot start transaction on {target_instance} while transaction "
                    f"active on {self._transaction_instance}"
                )
                
            self._transaction_instance = target_instance
            connection.autocommit = False
            self._logger.debug(f"Starting transaction on instance: {target_instance}")
            yield
            connection.commit()
            self._logger.debug(f"Committed transaction on instance: {target_instance}")
            
        except Exception as e:
            self._logger.error(f"Transaction failed on instance {target_instance}: {str(e)}")
            connection.rollback()
            raise DatabaseError(f"Transaction failed: {str(e)}")
            
        finally:
            connection.autocommit = True
            self._transaction_instance = None

    def copy_table(self, 
                   source_instance: str, 
                   target_instance: str, 
                   table_name: str, 
                   batch_size: int = 1000) -> None:
        """
        Copy table between database instances.
        
        Args:
            source_instance: Source instance name
            target_instance: Target instance name
            table_name: Table to copy
            batch_size: Number of rows to copy at once
        """
        try:
            # Get schema from source
            schema_query = f"""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table_name}'
            """
            
            schema_df = self.query(schema_query, source_instance)
            
            # Create table in target
            columns = [f"{row['COLUMN_NAME']} {row['DATA_TYPE']}" 
                      for _, row in schema_df.iterrows()]
            create_query = f"CREATE TABLE {table_name} ({', '.join(columns)})"
            
            self.execute(create_query, target_instance)
            
            # Copy data in batches
            offset = 0
            total_rows = 0
            
            while True:
                data_query = f"""
                    SELECT * FROM {table_name} 
                    ORDER BY (SELECT NULL) 
                    OFFSET {offset} ROWS FETCH NEXT {batch_size} ROWS ONLY
                """
                
                batch_df = self.query(data_query, source_instance)
                if batch_df.empty:
                    break
                    
                # Insert batch
                placeholders = ','.join(['?'] * len(batch_df.columns))
                insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
                
                self.executemany(insert_query, batch_df.values.tolist(), target_instance)
                
                offset += batch_size
                total_rows += len(batch_df)
                self._logger.info(f"Copied {total_rows} rows to {target_instance}.{table_name}")
            
            self._logger.info(
                f"Successfully copied table {table_name} from {source_instance} to {target_instance}"
            )
            
        except Exception as e:
            self._logger.error(f"Failed to copy table {table_name}: {str(e)}")
            raise DatabaseError(f"Failed to copy table: {str(e)}")

    def query(self, query: str, instance_name: Optional[str] = None) -> pd.DataFrame:
        """
        Execute query and return results as DataFrame.
        
        Args:
            query: SQL query to execute
            instance_name: Optional instance name, uses active instance if not specified
            
        Returns:
            DataFrame containing query results
        """
        target = instance_name or self.active_instance
        if not target:
            raise DatabaseError("No active database instance")
        
        if target not in self.connections:
            raise DatabaseError(f"Instance {target} not attached")
            
        try:
            return pd.read_sql(query, self.connections[target])
        except Exception as e:
            self._logger.error(f"Query failed on instance {target}: {str(e)}")
            raise DatabaseError(f"Query failed: {str(e)}")

    def execute(self, query: str, instance_name: Optional[str] = None) -> None:
        """
        Execute query without returning results.
        
        Args:
            query: SQL query to execute
            instance_name: Optional instance name, uses active instance if not specified
        """
        target = instance_name or self.active_instance
        if not target:
            raise DatabaseError("No active database instance")
        
        if target not in self.connections:
            raise DatabaseError(f"Instance {target} not attached")
            
        try:
            with self.connections[target].cursor() as cursor:
                cursor.execute(query)
                self.connections[target].commit()
            self._logger.debug(f"Successfully executed query on instance: {target}")
        except Exception as e:
            self._logger.error(f"Query execution failed on instance {target}: {str(e)}")
            raise DatabaseError(f"Query execution failed: {str(e)}")

    def executemany(self, query: str, parameters: List[Any],
                    instance_name: Optional[str] = None) -> None:
        """
        Execute query with multiple parameter sets.
        
        Args:
            query: SQL query to execute
            parameters: List of parameter sets
            instance_name: Optional instance name, uses active instance if not specified
        """
        target = instance_name or self.active_instance
        if not target:
            raise DatabaseError("No active database instance")
        
        if target not in self.connections:
            raise DatabaseError(f"Instance {target} not attached")
            
        try:
            with self.connections[target].cursor() as cursor:
                cursor.executemany(query, parameters)
                self.connections[target].commit()
            self._logger.debug(
                f"Successfully executed batch query on instance: {target}"
            )
        except Exception as e:
            self._logger.error(
                f"Batch query execution failed on instance {target}: {str(e)}"
            )
            raise DatabaseError(f"Batch query execution failed: {str(e)}")

    def get_instances_info(self) -> pd.DataFrame:
        """
        Get information about attached database instances.
        
        Returns:
            DataFrame containing instance information
        """
        return pd.DataFrame([
            {
                'instance_name': inst.name,
                'engine_type': inst.engine_type.name,
                'is_active': inst.is_active,
                'attached_at': inst.attached_at
            }
            for inst in self.instances.values()
        ])

    def close(self) -> None:
        """Close all database connections."""
        try:
            for name, conn in self.connections.items():
                try:
                    conn.close()
                    self._logger.debug(f"Closed connection to instance: {name}")
                except Exception as e:
                    self._logger.warning(f"Error closing connection to {name}: {str(e)}")
                    
            self.connections.clear()
            self.instances.clear()
            self.active_instance = None
            self._connection = None
            self._logger.info("Closed all database connections")
            
        except Exception as e:
            self._logger.error(f"Error during connection cleanup: {str(e)}")
            raise DatabaseError(f"Failed to close connections: {str(e)}")

# Usage Example
def main():
    # Initialize multi-database connector
    multi_db = MultiDatabaseConnector()
    
    try:
        # Attach SQL Server database
        multi_db.attach(
            "mssql_db",
            TargetDatabaseEngine.MSSQL,
            TargetDatabaseConnectionStringOption.Customize_DSN_AndChangeUserPwd
        ).attach(
            "mysql_db",
            TargetDatabaseEngine.MYSQL,
            TargetDatabaseConnectionStringOption.Customize_DSN_AndChangeUserPwd
        ).use("mssql_db")
        
        # Perform operations
        with multi_db.transaction():
            multi_db.execute("""
                CREATE TABLE example (
                    id INT PRIMARY KEY,
                    name VARCHAR(100)
                )
            """)
            
            multi_db.execute("""
                INSERT INTO example (id, name) 
                VALUES (1, 'Test Data')
            """)
        
        # Query data
        results = multi_db.query("SELECT * FROM example")
        print("Query Results:", results)
        
        # Copy table between instances
        multi_db.copy_table("mssql_db", "mysql_db", "example")
        
    except DatabaseError as e:
        print(f"Database operation failed: {e}")
        raise
        
    finally:
        multi_db.close()

if __name__ == "__main__":
    main()