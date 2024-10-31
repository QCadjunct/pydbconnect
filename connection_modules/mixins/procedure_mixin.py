''' pydatabaseconnection/connection_modules/mixins/procedure_mixin.py '''

from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from ...exceptions import ExecutionError
from ...utility.decorators import log_operation, validate_connection, transaction

class StoredProcedureMixin:
    """Mixin for stored procedure operations."""

    @log_operation
    @validate_connection
    @transaction
    def execute_stored_procedure(self: 'DatabaseConnection',
                               procedure_name: str,
                               params: Optional[Dict[str, Any]] = None,
                               output_params: Optional[List[str]] = None) -> Tuple[Any, Dict[str, Any]]:
        """
        Execute a stored procedure with input and output parameters.
        Returns tuple of (result_sets, output_parameters).
        """
        try:
            cursor = self._connection.cursor()
            
            # Build parameter string
            param_string = ""
            if params or output_params:
                all_params = []
                if params:
                    all_params.extend(f":{param}" for param in params.keys())
                if output_params:
                    all_params.extend(f":{param} OUTPUT" for param in output_params)
                param_string = "(" + ", ".join(all_params) + ")"

            # Execute procedure
            cursor.execute(f"BEGIN {procedure_name}{param_string}; END;", params or {})

            # Get results
            results = []
            while True:
                try:
                    results.append(cursor.fetchall())
                except:
                    break

            # Get output parameters
            out_params = {}
            if output_params:
                for param in output_params:
                    out_params[param] = cursor.getvar(param).getvalue()

            return results, out_params
        except Exception as e:
            raise ExecutionError(f"Stored procedure execution failed: {str(e)}")
        finally:
            cursor.close()

    @log_operation
    @validate_connection
    def execute_stored_procedure_to_dataframe(self: 'DatabaseConnection',
                                            procedure_name: str,
                                            params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Execute stored procedure and return results as DataFrame."""
        results, _ = self.execute_stored_procedure(procedure_name, params)
        if not results or not results[0]:
            return pd.DataFrame()
        
        # Convert first result set to DataFrame
        cursor = self._connection.cursor()
        columns = [col[0] for col in cursor.description]
        return pd.DataFrame(results[0], columns=columns)