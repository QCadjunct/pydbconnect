'''  pydatabaseconnection/connection_modules/mixins/modification_mixin.py  '''

from typing import Any, Dict, List, Optional, Tuple, Union
from ...exceptions import ExecutionError
from ...utils.decorators import log_operation, validate_connection, transaction

class ModificationMixin:
    """Mixin for database modification operations."""

    @log_operation
    @validate_connection
    @transaction
    def execute_insert(self: 'DatabaseConnection',
                      table_name: str,
                      data: Union[Dict[str, Any], List[Dict[str, Any]]],
                      return_id: bool = False) -> Union[int, List[int]]:
        """Execute INSERT operation(s)."""
        try:
            cursor = self._connection.cursor()
            
            if isinstance(data, dict):
                # Single insert
                columns = list(data.keys())
                placeholders = [f":{col}" for col in columns]
                query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                cursor.execute(query, data)
                return cursor.lastrowid if return_id else 1
            else:
                # Bulk insert
                if not data:
                    return []
                columns = list(data[0].keys())
                placeholders = [f":{col}" for col in columns]
                query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                cursor.executemany(query, data)
                return [cursor.lastrowid] if return_id else len(data)
        except Exception as e:
            raise ExecutionError(f"Insert operation failed: {str(e)}")
        finally:
            cursor.close()

    @log_operation
    @validate_connection
    @transaction
    def execute_update(self: 'DatabaseConnection',
                      table_name: str,
                      data: Dict[str, Any],
                      where_clause: str,
                      where_params: Optional[Dict[str, Any]] = None) -> int:
        """Execute UPDATE operation."""
        try:
            cursor = self._connection.cursor()
            set_clause = ", ".join(f"{k} = :{k}" for k in data.keys())
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            params = {**data, **(where_params or {})}
            cursor.execute(query, params)
            return cursor.rowcount
        except Exception as e:
            raise ExecutionError(f"Update operation failed: {str(e)}")
        finally:
            cursor.close()

    @log_operation
    @validate_connection
    @transaction
    def execute_delete(self: 'DatabaseConnection',
                      table_name: str,
                      where_clause: str,
                      params: Optional[Dict[str, Any]] = None) -> int:
        """Execute DELETE operation."""
        try:
            cursor = self._connection.cursor()
            query = f"DELETE FROM {table_name} WHERE {where_clause}"
            cursor.execute(query, params or {})
            return cursor.rowcount
        except Exception as e:
            raise ExecutionError(f"Delete operation failed: {str(e)}")
        finally:
            cursor.close()
