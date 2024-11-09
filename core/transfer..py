# pydatabaseconnection/core/transfer.py
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging
from ..types.format_types import TransferFormat
from ..types.exceptions import TransferError
from ..formats.base import FormatHandler
from ..config.formats.format_config import FormatConfiguration

logger = logging.getLogger(__name__)

class DatabaseTransfer:
    """Core transfer functionality for database operations"""
    
    def __init__(
        self,
        source_conn: 'DatabaseConnection',
        target_conn: 'DatabaseConnection',
        transfer_format: TransferFormat = TransferFormat.PARQUET,
        intermediate_dir: Optional[Path] = None,
        options: Optional[Dict[str, Any]] = None
    ):
        self.source = source_conn
        self.target = target_conn
        self.format = transfer_format
        self.intermediate_dir = Path(intermediate_dir or "./transfer_data")
        self.options = options or {}
        self.format_handler = FormatHandler.create(transfer_format)
        self._validate_setup()

    def _validate_setup(self) -> None:
        """Validate transfer setup and requirements"""
        if not self.source.is_connected or not self.target.is_connected:
            raise TransferError("Both source and target connections must be established")
            
        self.intermediate_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate format support
        source_formats = self.source.template_manager.get_supported_formats()
        target_formats = self.target.template_manager.get_supported_formats()
        
        if self.format not in source_formats:
            raise TransferError(f"Source does not support {self.format.value}")
        if self.format not in target_formats:
            raise TransferError(f"Target does not support {self.format.value}")

    def transfer_table(
        self,
        table_name: str,
        key_column: str,
        batch_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Transfer a single table between databases"""
        logger.info(f"Starting transfer of table: {table_name}")
        
        try:
            # Extract data
            intermediate_path = self.format_handler.extract(
                self.source,
                table_name,
                key_column,
                self.intermediate_dir,
                batch_size
            )
            
            # Load data
            result = self.format_handler.load(
                self.target,
                table_name,
                intermediate_path,
                self.options
            )
            
            # Validate transfer
            validation = self._validate_transfer(table_name)
            
            return {
                "table_name": table_name,
                "rows_transferred": result.get("rows_transferred", 0),
                "validation": validation,
                "format": self.format.value
            }
            
        except Exception as e:
            raise TransferError(f"Failed to transfer table {table_name}: {str(e)}")
            
        finally:
            if not self.options.get("keep_intermediate", False):
                self.format_handler.cleanup(intermediate_path)

    def transfer_database(
        self,
        exclude_tables: Optional[List[str]] = None,
        validate: bool = True
    ) -> Dict[str, Any]:
        """Transfer entire database"""
        exclude_tables = exclude_tables or []
        results = []
        total_rows = 0
        
        # Get metadata
        metadata = self.source.get_table_metadata(exclude_tables)
        
        for _, row in metadata.iterrows():
            try:
                result = self.transfer_table(
                    row['TABLE_NAME'],
                    row['table_name_key']
                )
                results.append(result)
                total_rows += result["rows_transferred"]
                
            except Exception as e:
                logger.error(f"Failed to transfer table {row['TABLE_NAME']}: {e}")
                if not self.options.get("continue_on_error", False):
                    raise

        return {
            "tables_transferred": len(results),
            "total_rows": total_rows,
            "results": results,
            "format": self.format.value
        }

    def _validate_transfer(self, table_name: str) -> Dict[str, Any]:
        """Validate transferred data"""
        source_count = self.source.get_row_count(table_name)
        target_count = self.target.get_row_count(table_name)
        
        if source_count != target_count:
            raise TransferError(
                f"Row count mismatch for {table_name}: "
                f"source={source_count}, target={target_count}"
            )
            
        return {
            "row_count_match": True,
            "source_count": source_count,
            "target_count": target_count
        }
