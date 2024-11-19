from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from contextlib import contextmanager
import importlib
import pandas as pd
from dataclasses import dataclass
from src.db_templates.base_database_connector import BaseDatabaseConnector, DatabaseError
from src.db_templates.database_target_engine_template_modules import (
    load_default_parameter_keys_dict,
    load_dsn_parameter_keys_dict,
    MSSQL, MYSQL, POSTGRESQL, PSYCOPG2, SQLITE3, DUCKDB as template
)
from src.db_templates.database_target_engine_modules_enum_contraints import (
    TargetDatabaseEngine, TargetDatabaseConnectionStringOption
)

class DatabaseInstance:
   """Dynamic database instance based on template configuration."""
   
   def __init__(self, name: str, 
                engine_type: TargetDatabaseEngine,
                connect_option: TargetDatabaseConnectionStringOption):
       self.name = name
       self.engine_type = engine_type
       self.connect_option = connect_option
       self._template_config = None
       self._connection_params = {}
       self._finalized_params = {}
       self.is_active = True
       self.attached_at = datetime.now()

   def load_template_config(self, template_config: Dict[str, Any]) -> None:
       """Load template configuration dynamically."""
       self._template_config = template_config
       self._connection_params = self._template_config[self.engine_type.name]['DEFAULT_PARAMETERS']

   @preload_default_parameters
   def update_connection_params(self, **params) -> None:
       """Update connection parameters using template structure."""
       self._finalized_params.update(params)

class MultiDatabaseConnector(BaseDatabaseConnector):
   """Multi-database connector with template-based configuration."""
   
   def __init__(self):
       """Initialize multi-database connector."""
       super().__init__()
       self.instances: Dict[str, DatabaseInstance] = {}
       self.connections: Dict[str, Any] = {}
       self.active_instance: Optional[str] = None
       self._transaction_instance: Optional[str] = None
       self._logger = logging.getLogger(__name__)

   def _load_engine_config(self) -> Dict[str, Any]:
       """Load engine-specific configuration from templates."""
       try:
           return getattr(template, self.target_database_engine_name)
       except AttributeError as e:
           raise DatabaseError(f"Unsupported database engine: {self.target_database_engine_name}")

   def attach(self, 
              name: str,
              engine_type: TargetDatabaseEngine,
              connect_option: TargetDatabaseConnectionStringOption) -> 'MultiDatabaseConnector':
       """Attach new database instance with template configuration."""
       try:
           self.target_database_engine_name = engine_type.name
           self.connect_option = connect_option
           self.engine_config = self._load_engine_config()
           
           instance = DatabaseInstance(name, engine_type, connect_option)
           instance.load_template_config(self.engine_config)
           
           self.instances[name] = instance
           if not self.active_instance:
               self.active_instance = name
           
           return self
       except Exception as e:
           raise DatabaseError(f"Failed to attach database {name}: {str(e)}")

   def finalization_of_connection_parameters(self, **params) -> 'MultiDatabaseConnector':
       """Finalize connection parameters using template structure."""
       if not self.active_instance:
           raise DatabaseError("No active instance")
           
       instance = self.instances[self.active_instance]
       
       try:
           # Load template parameters
           if self.connect_option.uses_dsn:
               template_params = load_dsn_parameter_keys_dict(
                   instance.engine_type.name,
                   {instance.engine_type.name: self.engine_config[instance.engine_type.name]}
               )
           else:
               template_params = load_default_parameter_keys_dict(
                   instance.engine_type.name,
                   {instance.engine_type.name: self.engine_config[instance.engine_type.name]}
               )
           
           # Update with provided params
           template_params.update(params)
           
           # Let parent handle finalization
           super().finalization_of_connection_parameters(**template_params)
           
           # Update instance with finalized parameters
           instance.update_connection_params(**template_params)
           
           return self
           
       except Exception as e:
           raise DatabaseError(f"Failed to finalize connection parameters: {str(e)}")

def connect_to_database(self) -> 'MultiDatabaseConnector':
        """Establish database connection using finalized parameters."""
        if not self.active_instance:
            raise DatabaseError("No active instance")
            
        instance = self.instances[self.active_instance]
        
        try:
            # Use template's connection creation method
            connection_creator = self.engine_config[instance.engine_type.name]['CREATE_DATABASE_CONNECTION'][
                'LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING'
            ]
            connection = connection_creator(self._connection_string)()
            
            self.connections[instance.name] = connection
            self._connection = connection
            
            self._logger.info(f"Successfully connected to database: {instance.name}")
            return self
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")

    @contextmanager
    def transaction(self, instance_name: Optional[str] = None):
        """Transaction context manager for single-instance operations."""
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

    def query(self, query: str, instance_name: Optional[str] = None) -> pd.DataFrame:
        """Execute query and return results as DataFrame."""
        target = instance_name or self.active_instance
        if not target:
            raise DatabaseError("No active database instance")
        
        if target not in self.connections:
            raise DatabaseError(f"Instance {target} not attached")
            
        try:
            placeholder = self.engine_config[self.instances[target].engine_type.name][
                'CRUDBASIC']['PARAMETER_PLACEHOLDER']
            return pd.read_sql(query.replace('?', placeholder), self.connections[target])
        except Exception as e:
            self._logger.error(f"Query failed on instance {target}: {str(e)}")
            raise DatabaseError(f"Query failed: {str(e)}")

    def execute(self, query: str, instance_name: Optional[str] = None) -> None:
        """Execute query without returning results."""
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

    def copy_table(self, 
                   source_instance: str, 
                   target_instance: str, 
                   table_name: str, 
                   batch_size: int = 1000) -> None:
        """Copy table between database instances."""
        try:
            # Get schema from source using template's information schema query
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
            
            # Copy data in batches using template's placeholder
            source_placeholder = self.engine_config[self.instances[source_instance].engine_type.name][
                'CRUDBASIC']['PARAMETER_PLACEHOLDER']
            target_placeholder = self.engine_config[self.instances[target_instance].engine_type.name][
                'CRUDBASIC']['PARAMETER_PLACEHOLDER']
            
            offset = 0
            total_rows = 0
            
            while True:
                data_query = f"""
                    SELECT * FROM {table_name} 
                    ORDER BY (SELECT NULL) 
                    OFFSET {offset} ROWS FETCH NEXT {batch_size} ROWS ONLY
                """
                
                batch_df = self.query(data_query.replace('?', source_placeholder), source_instance)
                if batch_df.empty:
                    break
                    
                # Insert batch
                placeholders = ','.join([target_placeholder] * len(batch_df.columns))
                insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
                
                with self.connections[target_instance].cursor() as cursor:
                    cursor.executemany(insert_query, batch_df.values.tolist())
                    self.connections[target_instance].commit()
                
                offset += batch_size
                total_rows += len(batch_df)
                self._logger.info(f"Copied {total_rows} rows to {target_instance}.{table_name}")
            
        except Exception as e:
            self._logger.error(f"Failed to copy table {table_name}: {str(e)}")
            raise DatabaseError(f"Failed to copy table: {str(e)}")

    def use(self, instance_name: str) -> 'MultiDatabaseConnector':
        """Switch active database instance."""
        if instance_name not in self.instances:
            raise DatabaseError(f"Instance {instance_name} not attached")
        
        self.active_instance = instance_name
        if instance_name in self.connections:
            self._connection = self.connections[instance_name]
            
        return self

    def get_instances_info(self) -> pd.DataFrame:
        """Get information about attached database instances."""
        return pd.DataFrame([
            {
                'instance_name': inst.name,
                'engine_type': inst.engine_type.name,
                'is_active': inst.is_active,
                'attached_at': inst.attached_at,
                'template_params': inst._finalized_params
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