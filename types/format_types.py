# pydatabaseconnection/types/format_types.py
from enum import Enum
from typing import TypedDict, Optional, List

class TransferFormat(Enum):
    """Supported transfer formats"""
    PARQUET = "parquet"
    CSV = "csv"
    SQL = "sql"
    AVRO = "avro"
    ORC = "orc"
    ARROW = "arrow"
    FEATHER = "feather"
    JSON = "json"
    EXCEL = "excel"
    PICKLE = "pickle"

class FormatCapabilities(TypedDict):
    """Format capabilities definition"""
    extension: str
    compression: List[str]
    partition_support: bool
    schema_support: bool
    binary_support: bool
    streaming_support: bool
    module: Optional[str]
    max_batch_size: int

class TransferResult(TypedDict):
    """Transfer operation result"""
    table_name: str
    rows_transferred: int
    validation: Dict[str, Any]
    format: str
    duration: float

class TransferOptions(TypedDict):
    """Transfer operation options"""
    batch_size: Optional[int]
    compression: Optional[str]
    keep_intermediate: bool
    continue_on_error: bool
    validate: bool