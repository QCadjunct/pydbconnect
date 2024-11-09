# pydatabaseconnection/formats/orc.py
import pyorc
import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path
from .base import FormatHandler

class ORCHandler(FormatHandler):
    """Handler for Apache ORC format operations"""
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.default_options = {
            "stripe_size": 67108864,  # 64MB
            "compression": "ZLIB",
            "compression_strategy": "SPEED",
            "batch_size": 1024
        }
        self.options = {**self.default_options, **(options or {})}

    def _get_orc_type(self, df: pd.DataFrame) -> str:
        """Generate ORC schema from DataFrame"""
        type_mapping = {
            'int64': 'BIGINT',
            'float64': 'DOUBLE',
            'object': 'STRING',
            'bool': 'BOOLEAN',
            'datetime64[ns]': 'TIMESTAMP'
        }
        
        fields = []
        for column, dtype in df.dtypes.items():
            orc_type = type_mapping.get(str(dtype), 'STRING')
            fields.append(f'{column}:{orc_type}')
        
        return f"struct<{','.join(f
