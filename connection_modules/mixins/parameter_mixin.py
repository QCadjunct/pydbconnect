# pydatabaseconnection/connection_modules/mixins/parameter_mixin.py
from typing import Any, Dict, Optional
from ...exceptions import ValidationError
from ...utility.decorators import log_operation

class ParameterMixin:
    """Mixin for handling database parameters."""

    @log_operation
    def set_parameter(self: 'DatabaseConnection', key: str, value: Any) -> 'DatabaseConnection':
        """Set a single parameter."""
        if not hasattr(self, '_parameters'):
            self._parameters = {}
        self._parameters[key] = value
        return self

    @log_operation
    def set_parameters(self: 'DatabaseConnection', params: Dict[str, Any]) -> 'DatabaseConnection':
        """Set multiple parameters."""
        if not hasattr(self, '_parameters'):
            self._parameters = {}
        self._parameters.update(params)
        return self

    def get_parameter(self: 'DatabaseConnection', key: str, default: Any = None) -> Any:
        """Get parameter value."""
        return getattr(self, '_parameters', {}).get(key, default)

# pydatabaseconnection/connection_modules/mixins/query_mixin.py
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
