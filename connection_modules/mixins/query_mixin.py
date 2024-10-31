'''pydatabaseconnection/connection_modules/mixins/query_mixin.py'''

from typing import Any, Dict, Optional, Union, List
import pandas as pd
from ...exceptions import ExecutionError
from ...utility.decorators import log_operation, validate_connection, transaction

class QueryMixin:
    """Mixin for database query operations."""

    @log_operation
    @validate_connection
    def execute_sql_to_panda_dataframe(self: 'DatabaseConnection',
                                     sql_command: str,
                                     params: Optional[Dict[str, Any]] = None,
                                     index_column: Optional[str] = None) -> pd.DataFrame:
        """Execute SELECT query and return DataFrame."""
        try:
            return pd.read_sql(sql_command, self._connection, 
                             params=params, index_col=index_column)
        except Exception as e:
            raise ExecutionError(f"Query execution failed: {str(e)}")

    @log_operation
    @validate_connection
    def execute_sql_to_dict(self: 'DatabaseConnection',
                           sql_command: str,
                           params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return list of dictionaries."""
        try:
            cursor = self._connection.cursor()
            cursor.execute(sql_command, params or {})
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            raise ExecutionError(f"Query execution failed: {str(e)}")
        finally:
            cursor.close()
