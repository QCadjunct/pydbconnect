# pydatabaseconnection/utils/format_utils/orc_utils.py
from typing import Dict, Any, Optional, List
import pyorc
import pandas as pd
from pathlib import Path

class ORCUtils:
    """Utilities for Apache ORC operations"""
    
    @staticmethod
    def analyze_stripes(
        path: Path
    ) -> Dict[str, Any]:
        """Analyze ORC file stripes"""
        with open(path, 'rb') as f:
            reader = pyorc.Reader(f)
            stripe_stats = []
            
            for stripe in reader.stripes:
                stats = {
                    "rows": stripe.num_rows,
                    "bytes": stripe.bytes_length,
                    "data_length": stripe.data_length,
                    "index_length": stripe.index_length,
                    "offset": stripe.offset
                }
                stripe_stats.append(stats)
            
            return {
                "num_stripes": len(stripe_stats),
                "stripes": stripe_stats,
                "total_rows": reader.num_rows,
                "compression": reader.compression,
                "schema": str(reader.schema)
            }

    @staticmethod
    def optimize_schema(
        df: pd.DataFrame,
        include_indexes: bool = True
    ) -> str:
        """Generate optimized ORC schema from DataFrame"""
        type_mapping = {
            'int64': 'bigint',
            'float64': 'double',
            'object': 'string',
            'bool': 'boolean',
            'datetime64[ns]': 'timestamp',
            'category': 'string'
        }
        
        def _get_orc_type(dtype: str) -> str:
            return type_mapping.get(str(dtype), 'string')
        
        columns = []
        for col, dtype in df.dtypes.items():
            # Add index columns if requested
            if include_indexes and col in df.index.names:
                columns.append(f"{col}:{_get_orc_type(dtype)} index")
            else:
                columns.append(f"{col}:{_get_orc_type(dtype)}")
        
        return f"struct<{','.join(columns)}>"

    @staticmethod
    def suggest_stripe_size(
        data_size: int,
        target_stripe_count: int = 10
    ) -> int:
        """Suggest optimal stripe size"""
        base_size = data_size // target_stripe_count
        # Round to nearest power of 2
        return 2 ** (base_size - 1).bit_length()

    @staticmethod
    def create_bloom_filters(
        df: pd.DataFrame,
        columns: List[str],
        false_positive_probability: float = 0.01
    ) -> Dict[str, Any]:
        """Create Bloom filters for specified columns"""
        bloom_filters = {}
        for col in columns:
            if col in df.columns:
                unique_values = df[col].nunique()
                # Calculate optimal Bloom filter parameters
                m = int(-unique_values * np.log(false_positive_probability) / (np.log(2)**2))
                k = int(m/unique_values * np.log(2))
                bloom_filters[col] = {
                    "size": m,
                    "num_hash_functions": k,
                    "estimated_fpp": false_positive_probability
                }
        return bloom_filters
