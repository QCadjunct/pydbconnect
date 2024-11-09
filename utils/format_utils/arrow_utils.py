# pydatabaseconnection/utils/format_utils/arrow_utils.py
from typing import Dict, Any, Optional, List
import pyarrow as pa
import pyarrow.compute as pc
from pathlib import Path

class ArrowUtils:
    """Utilities for Apache Arrow operations"""
    
    @staticmethod
    def optimize_table(
        table: pa.Table,
        options: Optional[Dict[str, Any]] = None
    ) -> pa.Table:
        """Optimize Arrow table memory layout"""
        options = options or {}
        result = table
        
        if options.get("dictionary_encode", True):
            # Dictionary encode string columns
            for field in table.schema:
                if pa.types.is_string(field.type):
                    result = result.dictionary_encode(field.name)
        
        if options.get("null_optimize", True):
            # Optimize null handling
            for field in table.schema:
                if result.field(field.name).nullable:
                    mask = pc.is_null(result[field.name])
                    if pc.sum(mask).as_py() > (len(result) / 2):
                        result = result.set_column(
                            result.schema.get_field_index(field.name),
                            field.name,
                            result[field.name].fill_null(None)
                        )
        
        return result

    @staticmethod
    def suggest_chunking(
        table: pa.Table,
        target_chunk_size: int = 64 * 1024 * 1024  # 64MB
    ) -> List[int]:
        """Suggest optimal chunk sizes"""
        sizes = []
        current_size = 0
        current_rows = 0
        
        for batch in table.to_batches():
            batch_size = batch.nbytes
            if current_size + batch_size > target_chunk_size:
                sizes.append(current_rows)
                current_size = batch_size
                current_rows = batch.num_rows
            else:
                current_size += batch_size
                current_rows += batch.num_rows
                
        if current_rows > 0:
            sizes.append(current_rows)
            
        return sizes

    @staticmethod
    def analyze_memory_usage(
        table: pa.Table
    ) -> Dict[str, Any]:
        """Analyze memory usage of Arrow table"""
        return {
            "total_bytes": table.nbytes,
            "column_bytes": {
                name: table[name].nbytes
                for name in table.column_names
            },
            "null_counts": {
                name: table[name].null_count
                for name in table.column_names
            },
            "dictionary_encoded": {
                name: pa.types.is_dictionary(table[name].type)
                for name in table.column_names
            }
        }
