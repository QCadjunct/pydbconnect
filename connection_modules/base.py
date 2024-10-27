'''pydatabaseconnection/connection_modules/protocols.py '''

from typing import Protocol, Any, Dict, Optional, Union
import pandas as pd

class DatabaseProtocol(Protocol):
    """Protocol defining database interface requirements."""
    
    def connect(self) -> bool:
        """Establish database connection."""
        ...

    def disconnect(self) -> bool:
        """Close database connection."""
        ...

    def is_connected(self) -> bool:
        """Check connection status."""
        ...

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute raw query."""
        ...

class QueryExecutionProtocol(Protocol):
    """Protocol for query execution operations."""
    
    def execute_sql_to_panda_dataframe(self, sql_command: str,
                                     index_column: Optional[str] = None,
                                     return_dataframe: bool = True) -> Union['DatabaseConnection', pd.DataFrame]:
        """Execute SELECT query to DataFrame."""
        ...

    def execute_sql_to_dict(self, sql_command: str) -> Dict[str, Any]:
        """Execute SELECT query to dictionary."""
        ...

class ModificationProtocol(Protocol):
    """Protocol for data modification operations."""
    
    def execute_insert(self, table_name: str, data: Dict[str, Any]) -> int:
        """Execute INSERT operation."""
        ...

    def execute_update(self, table_name: str, data: Dict[str, Any],
                      where_clause: str) -> int:
        """Execute UPDATE operation."""
        ...

    def execute_delete(self, table_name: str, where_clause: str) -> int:
        """Execute DELETE operation."""
        ...

class StoredProcedureProtocol(Protocol):
    """Protocol for stored procedure operations."""
    
    def execute_stored_procedure(self, name: str,
                               params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute stored procedure."""
        ...
