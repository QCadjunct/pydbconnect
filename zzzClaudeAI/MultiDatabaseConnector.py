from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import logging
from contextlib import contextmanager
from functools import wraps
import importlib
import pandas as pd
from pandas import DataFrame
from src.db_templates.base_database_connector import BaseDatabaseConnector, DatabaseError
from src.db_templates.database_target_engine_template_modules import (
    load_default_parameter_keys_dict,
    load_dsn_parameter_keys_dict,
    MSSQL, MYSQL, POSTGRESQL, PSYCOPG2, SQLITE3, DUCKDB as template
)
from src.db_templates.database_target_engine_modules_enum_contraints import (
    TargetDatabaseEngine, TargetDatabaseConnectionStringOption,ChangeDefaultUsernameAndPassword
)
from src.utils import preload_default_parameters

class MultiDatabaseConnector(BaseDatabaseConnector):
    """Multi-database connector following BaseDatabaseConnector patterns."""
    
    def __init__(self):
        super().__init__()
        self.instances: Dict[str, Dict[str, Any]] = {}
        self.connections: Dict[str, Any] = {}
        self.active_instance: Optional[str] = None
        self._transaction_instance: Optional[str] = None
        self._logger = logging.getLogger(__name__)

    def _load_target_database_engine_template_config(self) -> Dict[str, Any]:
        """Load engine-specific configuration."""
        try:
            return getattr(template, self.target_database_engine_name)
        except AttributeError as e:
            raise DatabaseError(f"Unsupported database engine: {self.target_database_engine_name}") from e

    def attach(self, database_alias_name: str,
               target_database_engine_type: TargetDatabaseEngine,
               target_database_engine_connect_option: TargetDatabaseConnectionStringOption) -> 'MultiDatabaseConnector':
        """
        First step in connection chain.
        Mirrors DatabaseConnector's initialization pattern.
        """
        try:
            self.target_database_engine_name = target_database_engine_type.name
            self.target_database_engine_connect_option = target_database_engine_connect_option
            self.target_database_engine_template_config = self._load_target_database_engine_template_config()
            
            # Store instance configuration
            self.instances[database_alias_name] = {
                'database_alias_name': database_alias_name,
                'target_database_engine_type': target_database_engine_type,
                'target_database_engine_connect_option': target_database_engine_connect_option,
                'target_database_engine_template_config': self.target_database_engine_template_config,
                'finalized_connection_parameters': self.finalization_of_connection_parameters,
                'is_active': True,
                'attached_at': datetime.now(),
                'deattached_at': None # At disconnect (detachment) datetime.now(),
            }
            
            if not self.active_instance:
                self.active_instance = database_alias_name
            
            return self
            
        except Exception as e:
            raise DatabaseError(f"Failed to attach database {database_alias_name}: {str(e)}")

    def get_default_params(self) -> Dict[str, Any]:
        """Get default parameters from template."""
        if not self.active_instance:
            raise DatabaseError("No active instance")
            
        instance = self.instances[self.active_instance]
        target_database_engine_name = instance['target_database_engine_type'].name
        
        if self.connect_option.uses_dsn:
            return load_dsn_parameter_keys_dict(self.target_database_engine_name, 
                {target_database_engine_name: self.target_database_engine_template_config[self.target_database_engine_name]})
        else:
            return load_default_parameter_keys_dict(self.target_database_engine_name,
                {target_database_engine_name: self.target_database_engine_template_config[self.target_database_engine_name]})

    @preload_default_parameters(get_default_params)
    def finalization_of_connection_parameters(self, **params) -> 'MultiDatabaseConnector':
        """
        Second step in connection chain.
        Uses same parameter handling as DatabaseConnector.
        """
        super().finalization_of_connection_parameters(**params)
        return self

    def change_default_username_and_password(self, show_password: bool = False) -> 'MultiDatabaseConnector':
        """
        Optional credential step in connection chain.
        Identical to DatabaseConnector's implementation.
        """
        super().change_default_username_and_password(show_password)
        return self

    def connect_to_database(self) -> 'MultiDatabaseConnector':
        """
        Final step in connection chain.
        Uses template's connection creation.
        """
        if not self.active_instance:
            raise DatabaseError("No active instance")
            
        try:
            instance = self.instances[self.active_instance]
            self.target_database_engine_name = instance['target_database_engine_type'].name
            
            # Use template's connection creator
            connection_creator = self.target_database_engine_template_config[self.target_database_engine_name]['CREATE_DATABASE_CONNECTION'][
                'LAMBDA_FINALIZED_PARAMETER_CONNECTION_STRING'
            ]
            connection = connection_creator(self._connection_string)()
            
            self.connections[self.active_instance] = connection
            self._connection = connection
            
            return self
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")

    def use(self, database_alias_name: str) -> 'MultiDatabaseConnector':
        """Switch active database instance."""
        if database_alias_name not in self.instances:
            raise DatabaseError(f"Instance {database_alias_name} not attached")
            
        self.active_instance = database_alias_name
        if database_alias_name in self.connections:
            self._connection = self.connections[database_alias_name]
        
        # Reset connection state
        self.target_database_engine_name = self.instances[database_alias_name]['target_database_engine_type'].name
        self.connect_option = self.instances[database_alias_name]['connect_option']
        self.engine_config = self.instances[database_alias_name]['target_database_engine_template_config']
        
        return self

    @contextmanager
    def transaction(self, database_alias_name: Optional[str] = None):
        """Transaction context manager for single-instance operations."""
        target = database_alias_name or self.active_instance
        if not target:
            raise DatabaseError("No active database instance")
            
        if target not in self.connections:
            raise DatabaseError(f"Instance {target} not attached")
            
        connection = self.connections[target]
        
        try:
            if self._transaction_instance and self._transaction_instance != target:
                raise DatabaseError(
                    f"Cannot start transaction on {target} while transaction "
                    f"active on {self._transaction_instance}"
                )
                
            self._transaction_instance = target
            connection.autocommit = False
            yield
            connection.commit()
            
        except Exception as e:
            connection.rollback()
            raise DatabaseError(f"Transaction failed: {str(e)}")
            
        finally:
            connection.autocommit = True
            self._transaction_instance = None

    def close(self) -> None:
        """Close all database connections."""
        try:
            for conn in self.connections.values():
                conn.close()
                
            self.connections.clear()
            self.instances.clear()
            self.active_instance = None
            self._connection = None
            
        except Exception as e:
            raise DatabaseError(f"Failed to close connections: {str(e)}")

    def __enter__(self) -> 'MultiDatabaseConnector':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
    
    def detach(self, database_alias_name: str) -> 'MultiDatabaseConnector':
        """Detach database instance and record timestamp."""
    
        if database_alias_name not in self.instances:
            raise DatabaseError(f"Instance {database_alias_name} not attached")
            
        try:
            # Close connection if exists
            if database_alias_name in self.connections:
                self.connections[database_alias_name].close()
                del self.connections[database_alias_name]
                
            # Update instance state
            self.instances[database_alias_name]['is_active'] = False
            self.instances[database_alias_name]['deattached_at'] = datetime.now()
            
            # Reset active instance if needed
            if self.active_instance == database_alias_name:
                self.active_instance = next(
                    (name for name, inst in self.instances.items() 
                    if inst['is_active'] and name != database_alias_name), 
                    None
                )
            
            self._logger.info(f"Successfully detached database: {database_alias_name}")
            return self
            
        except Exception as e:
            raise DatabaseError(f"Failed to detach database {database_alias_name}: {str(e)}")

    def get_instance_lifecycle(self, database_alias_name: str) -> Dict[str, Any]:
        """Get instance lifecycle information."""
        if database_alias_name not in self.instances:
            raise DatabaseError(f"Instance {database_alias_name} not found")
            
        instance = self.instances[database_alias_name]
        return {
            'database_alias_name': instance['database_alias_name'],
            'engine_type': instance['target_database_engine_type'].name,
            'is_active': instance['is_active'],
            'attached_at': instance['attached_at'],
            'deattached_at': instance['deattached_at'],
            'connection_status': database_alias_name in self.connections,
            'is_current': self.active_instance == database_alias_name
        }

    def get_all_instances_status(self) -> pd.DataFrame: # PAH
        """Get status of all instances as DataFrame."""
        status_data = []
        for database_alias_name, instance in self.instances.items():
            status_data.append({
                'instance_name': database_alias_name,
                'target_database_engine_type': instance['target_database_engine_type'].name,
                'is_active': instance['is_active'],
                'attached_at': instance['attached_at'],
                'deattached_at': instance['deattached_at'],
                'connection_status': database_alias_name in self.connections,
                'is_current': self.active_instance == database_alias_name
            })
        return pd.DataFrame(status_data)

    def close(self) -> None:
        """Close all database connections with proper lifecycle recording."""
        try:
            current_time = datetime.now()
            for database_alias_name in list(self.connections.keys()):
                try:
                    self.connections[database_alias_name].close()
                    self.instances[database_alias_name]['is_active'] = False
                    self.instances[database_alias_name]['deattached_at'] = current_time
                    self._logger.debug(f"Closed connection to instance: {database_alias_name}")
                except Exception as e:
                    self._logger.warning(f"Error closing connection to {database_alias_name}: {str(e)}")
                    
            self.connections.clear()
            self.active_instance = None
            self._connection = None
            self._logger.info("Closed all database connections")
            
        except Exception as e:
            self._logger.error(f"Error during connection cleanup: {str(e)}")
            raise DatabaseError(f"Failed to close connections: {str(e)}")

def execute_query(self, query: str, instance_name: Optional[str] = None) -> pd.DataFrame:
        """Execute query on specified instance with template configuration."""
        target = instance_name or self.active_instance
        if not target:
            raise DatabaseError("No active database instance")
        
        if target not in self.connections:
            raise DatabaseError(f"Instance {target} not attached")
            
        try:
            # Get placeholder from template
            placeholder = self.instances[target]['target_database_engine_template_config'][self.instances[target]['engine_type'].name][
                'CRUDBASIC']['PARAMETER_PLACEHOLDER']
            
            return pd.read_sql(query.replace('?', placeholder), self.connections[target])
        except Exception as e:
            self._logger.error(f"Query failed on instance {target}: {str(e)}")
            raise DatabaseError(f"Query failed: {str(e)}")

def execute_many(self, query: str, parameters: List[Any], 
                instance_name: Optional[str] = None) -> None:
    """Execute parameterized query with multiple parameter sets."""
    target = instance_name or self.active_instance
    if not target:
        raise DatabaseError("No active database instance")
        
    if target not in self.connections:
        raise DatabaseError(f"Instance {target} not attached")
        
    try:
        placeholder = self.instances[target]['target_database_engine_template_config'][self.instances[target]['engine_type'].name][
            'CRUDBASIC']['PARAMETER_PLACEHOLDER']
        
        with self.connections[target].cursor() as cursor:
            cursor.executemany(query.replace('?', placeholder), parameters)
            self.connections[target].commit()
            
        self._logger.debug(f"Batch execution successful on instance: {target}")
    except Exception as e:
        self._logger.error(f"Batch execution failed on instance {target}: {str(e)}")
        raise DatabaseError(f"Batch execution failed: {str(e)}")

def copy_table(self, source_instance: str, target_instance: str, 
                table_name: str, batch_size: int = 1000) -> None:
    """Copy table between instances with template-specific handling."""
    if source_instance not in self.instances or target_instance not in self.instances:
        raise DatabaseError("Source or target instance not attached")
        
    try:
        # Get schema using template's system queries
        source_config = self.instances[source_instance]['target_database_engine_template_config']
        schema_query = source_config.get('INFORMATION_SCHEMA_QUERY', 
            """SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table_name}'""")
        
        schema_df = self.execute_query(
            schema_query.format(table_name=table_name), 
            source_instance
        )
        
        # Create table in target
        columns = [f"{row['COLUMN_NAME']} {row['DATA_TYPE']}" 
                    for _, row in schema_df.iterrows()]
        create_query = f"CREATE TABLE {table_name} ({', '.join(columns)})"
        
        with self.transaction(target_instance):
            self.execute_query(create_query, target_instance)
        
        # Copy data in batches using template placeholders
        total_rows = 0
        offset = 0
        
        while True:
            select_query = f"""
                SELECT * FROM {table_name} 
                ORDER BY (SELECT NULL) 
                OFFSET {offset} ROWS FETCH NEXT {batch_size} ROWS ONLY
            """
            
            batch_df = self.execute_query(select_query, source_instance)
            if batch_df.empty:
                break
            
            # Insert using target's placeholder style
            target_config = self.instances[target_instance]['target_database_engine_template_config']
            placeholder = target_config[self.instances[target_instance]['engine_type'].name][
                'CRUDBASIC']['PARAMETER_PLACEHOLDER']
            
            placeholders = ','.join([placeholder] * len(batch_df.columns))
            insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
            
            with self.transaction(target_instance):
                self.execute_many(insert_query, batch_df.values.tolist(), target_instance)
            
            total_rows += len(batch_df)
            offset += batch_size
            self._logger.info(f"Copied {total_rows} rows to {target_instance}.{table_name}")
        
        self._logger.info(
            f"Successfully copied table {table_name} from {source_instance} to {target_instance}"
        )
        
    except Exception as e:
        self._logger.error(f"Failed to copy table {table_name}: {str(e)}")
        raise DatabaseError(f"Failed to copy table: {str(e)}")

def execute_procedure(self, name: str, params: Optional[List[Any]] = None,
                        instance_name: Optional[str] = None) -> Optional[List[Any]]:
    """Execute stored procedure using template configuration."""
    target = instance_name or self.active_instance
    if not target:
        raise DatabaseError("No active database instance")
        
    if target not in self.connections:
        raise DatabaseError(f"Instance {target} not attached")
        
    try:
        with self.connections[target].cursor() as cursor:
            if params:
                cursor.callproc(name, params)
            else:
                cursor.callproc(name)
            try:
                return cursor.fetchall()
            except:
                return None
                
    except Exception as e:
        self._logger.error(f"Procedure execution failed on instance {target}: {str(e)}")
        raise DatabaseError(f"Procedure execution failed: {str(e)}")

def backup_database(self, path: str, instance_name: Optional[str] = None) -> None:
    """Backup database using template's backup command."""
    target = instance_name or self.active_instance
    if not target:
        raise DatabaseError("No active database instance")
        
    instance = self.instances[target]
    self.target_database_engine_name = instance['engine_type'].name
    
    backup_command = instance['target_database_engine_template_config'][self.target_database_engine_name].get('BACKUP_COMMAND', '')
    if not backup_command:
        raise DatabaseError(f"Backup not supported for {self.target_database_engine_name}")
        
    try:
        with self.connections[target].cursor() as cursor:
            cursor.execute(backup_command.format(path=path))
            self._logger.info(f"Successfully backed up database {target} to {path}")
            
    except Exception as e:
        self._logger.error(f"Backup failed for instance {target}: {str(e)}")
        raise DatabaseError(f"Backup failed: {str(e)}")

def restore_database(self, path: str, instance_name: Optional[str] = None) -> None:
    """Restore database using template's restore command."""
    target = instance_name or self.active_instance
    if not target:
        raise DatabaseError("No active database instance")
        
    instance = self.instances[target]
    self.target_database_engine_name = instance['engine_type'].name
    
    restore_command = instance['target_database_engine_template_config'][self.target_database_engine_name].get('RESTORE_COMMAND', '')
    if not restore_command:
        raise DatabaseError(f"Restore not supported for {self.target_database_engine_name}")
        
    try:
        with self.connections[target].cursor() as cursor:
            cursor.execute(restore_command.format(path=path))
            self._logger.info(f"Successfully restored database {target} from {path}")
            
    except Exception as e:
        self._logger.error(f"Restore failed for instance {target}: {str(e)}")
        raise DatabaseError(f"Restore failed: {str(e)}")

def validate_instance_state(self, instance_name: str) -> None:
        """Validate instance state and connectivity."""
        if instance_name not in self.instances:
            raise DatabaseError(f"Instance {instance_name} not attached")
            
        instance = self.instances[instance_name]
        if not instance['is_active']:
            raise DatabaseError(
                f"Instance {instance_name} is not active. "
                f"Deactivated at: {instance['deattached_at']}"
            )
            
        if instance_name not in self.connections:
            raise ConnectionError(f"No active connection for instance {instance_name}")

def get_template_info(self, instance_name: Optional[str] = None) -> Dict[str, Any]:
    """Get template configuration for instance."""
    target = instance_name or self.active_instance
    self.validate_instance_state(target)
    
    instance = self.instances[target]
    self.target_database_engine_name = instance['engine_type'].name
    
    return {
        'engine_type': self.target_database_engine_name,
        'connection_type': instance['connect_option'].name,
        'requires_credentials': instance['target_database_engine_template_config'][self.target_database_engine_name]['CRUDBASIC']['IS_USERNAME_AND_PASSWORD_REQUIRED'],
        'supports_dsn': instance['connect_option'].uses_dsn,
        'placeholder': instance['target_database_engine_template_config'][self.target_database_engine_name]['CRUDBASIC']['PARAMETER_PLACEHOLDER']
    }

@contextmanager
def batch_operations(self, instance_name: Optional[str] = None):
    """Context manager for batch operations with template-specific handling."""
    target = instance_name or self.active_instance
    self.validate_instance_state(target)
    
    connection = self.connections[target]
    instance = self.instances[target]
    
    try:
        if hasattr(connection, 'autocommit'):
            previous_autocommit = connection.autocommit
            connection.autocommit = False
        
        yield
        
        connection.commit()
        self._logger.debug(f"Batch operations committed on instance: {target}")
        
    except Exception as e:
        connection.rollback()
        self._logger.error(f"Batch operations failed on instance {target}: {str(e)}")
        raise DatabaseError(f"Batch operations failed: {str(e)}")
        
    finally:
        if hasattr(connection, 'autocommit'):
            connection.autocommit = previous_autocommit

# Usage Examples:
def main():
    """Example usage of MultiDatabaseConnector."""
    try:
        # Initialize connector
        mdb = MultiDatabaseConnector()
        
        # Attach multiple databases
        mdb.attach(
            "mssql_prod",
            TargetDatabaseEngine.MSSQL,
            TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd
        ).change_default_username_and_password(
        ).finalization_of_connection_parameters(
            host="prod.server",
            database="production"
        ).connect_to_database()
        
        # Attach another instance
        mdb.attach(
            "mysql_reporting",
            TargetDatabaseEngine.MYSQL,
            TargetDatabaseConnectionStringOption.Default_DSN_AndChangeUserPwd
        ).finalization_of_connection_parameters(
            dsn="ReportingDSN"
        ).connect_to_database()
        
        # Perform operations
        with mdb.batch_operations("mssql_prod"):
            # Copy data between instances
            mdb.copy_table(
                "mysql_reporting", 
                "mssql_prod",
                "monthly_sales",
                batch_size=5000
            )
            
            # Execute queries
            results = mdb.execute_query(
                "SELECT * FROM monthly_sales WHERE amount > ?",
                ["mssql_prod"]
            )
            print("Query Results:", results)
        
        # Check instance status
        status = mdb.get_all_instances_status()
        print("Instance Status:", status)
        
        # Get template information
        template_info = mdb.get_template_info("mssql_prod")
        print("Template Configuration:", template_info)
        
        # Detach instance
        mdb.detach("mysql_reporting")
        
    except DatabaseError as e:
        print(f"Database operation failed: {e}")
        raise
    finally:
        mdb.close()

if __name__ == "__main__":
    main()