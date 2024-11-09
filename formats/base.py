# pydatabaseconnection/formats/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path

class FormatHandler(ABC):
    """Base class for all format handlers"""
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options = options or {}

    @abstractmethod
    def extract(
        self,
        connection: 'DatabaseConnection',
        table_name: str,
        key_column: str,
        output_dir: Path,
        batch_size: Optional[int] = None
    ) -> Path:
        """Extract data from source database"""
        pass

    @abstractmethod
    def load(
        self,
        connection: 'DatabaseConnection',
        table_name: str,
        source_path: Path,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Load data into target database"""
        pass

    @abstractmethod
    def cleanup(self, path: Path) -> None:
        """Clean up intermediate files"""
        pass

    @classmethod
    def create(cls, format_type: 'TransferFormat') -> 'FormatHandler':
        """Factory method to create format handler"""
        handlers = {
            TransferFormat.PARQUET: ParquetHandler,
            TransferFormat.CSV: CSVHandler,
            TransferFormat.SQL: SQLHandler,
            TransferFormat.AVRO: AvroHandler,
            TransferFormat.ORC: ORCHandler,
            TransferFormat.ARROW: ArrowHandler
        }
        
        handler_class = handlers.get(format_type)
        if not handler_class:
            raise ValueError(f"Unsupported format: {format_type}")
            
        return handler_class()
