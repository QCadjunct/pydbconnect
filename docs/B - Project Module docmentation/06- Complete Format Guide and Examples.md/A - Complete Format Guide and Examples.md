# Database Transfer Format Guide

## Table of Contents
1. [Supported Formats Overview](#supported-formats-overview)
2. [Detailed Format Descriptions](#detailed-format-descriptions)
3. [Usage Examples](#usage-examples)
4. [Error Handling](#error-handling)
5. [Format-Specific Utilities](#format-specific-utilities)
6. [Performance Considerations](#performance-considerations)

## Supported Formats Overview

| Format  | Binary | Compression | Schema Support | Streaming | Best For |
|---------|---------|-------------|----------------|-----------|-----------|
| Parquet | Yes | High | Yes | No | Analytics, Column-oriented data |
| CSV | No | Medium | No | Yes | Simple data, Universal compatibility |
| SQL | No | Low | Yes | Yes | Database migrations, Full schema transfer |
| Arrow | Yes | Medium | Yes | Yes | In-memory operations, Fast processing |
| Avro | Yes | High | Yes | Yes | Schema evolution, Complex types |
| ORC | Yes | High | Yes | Yes | Big data, Hadoop ecosystem |

## Detailed Format Descriptions

### 1. Apache Parquet
 
# Basic Parquet transfer
db = DatabaseConnection("MSSQL") \
    .with_credentials_from_env() \
    .transfer_to(
        target_engine="DUCKDB",
        format=TransferFormat.PARQUET,
        options={
            "compression": "snappy",
            "row_group_size": 100000,
            "use_dictionary": True
        }
    )

# Partitioned Parquet transfer
db.transfer_table(
    "sales_data",
    partition_by=["year", "month"],
    options={
        "compression": "zstd",
        "statistics": True,
        "validate_schema": True
    }
)

# Error handling for Parquet
try:
    db.transfer_table("large_table")
except ParquetError as e:
    if "memory" in str(e).lower():
        # Retry with smaller row groups
        db.transfer_table(
            "large_table",
            options={"row_group_size": 10000}
        )
 

### 2. CSV Format
 
# Basic CSV transfer
db = DatabaseConnection("POSTGRESQL") \
    .with_credentials_from_env() \
    .transfer_to(
        target_engine="MYSQL",
        format=TransferFormat.CSV,
        options={
            "delimiter": ",",
            "encoding": "utf-8",
            "quoting": "QUOTE_MINIMAL"
        }
    )

# Streaming large CSV
db.transfer_table(
    "huge_table",
    options={
        "chunksize": 50000,
        "compression": "gzip",
        "date_format": "%Y-%m-%d"
    }
)

# CSV with custom handling
try:
    db.transfer_table("problematic_data")
except CSVError as e:
    if "encoding" in str(e):
        # Retry with different encoding
        db.transfer_table(
            "problematic_data",
            options={
                "encoding": "latin1",
                "errors": "ignore"
            }
        )
 

### 3. SQL Format
 
# Full schema transfer
db = DatabaseConnection("MSSQL") \
    .with_credentials_from_env() \
    .transfer_to(
        target_engine="POSTGRESQL",
        format=TransferFormat.SQL,
        options={
            "include_schema": True,
            "include_indexes": True,
            "transaction_size": 1000
        }
    )

# Incremental SQL transfer
db.transfer_table(
    "audit_logs",
    options={
        "batch_size": 5000,
        "include_triggers": True,
        "validate_constraints": True
    }
)

# Error handling with retry
def transfer_with_retry(table_name, max_retries=3):
    for attempt in range(max_retries):
        try:
            return db.transfer_table(table_name)
        except SQLError as e:
            if "deadlock" in str(e) and attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
 

### 4. Arrow Format
 
# Memory-optimized transfer
db = DatabaseConnection("MYSQL") \
    .with_credentials_from_env() \
    .transfer_to(
        target_engine="DUCKDB",
        format=TransferFormat.ARROW,
        options={
            "use_threads": True,
            "memory_map": True,
            "compression": "lz4"
        }
    )

# Streaming Arrow transfer
db.transfer_table(
    "timeseries_data",
    options={
        "chunk_size": 100000,
        "parallel_reads": 4,
        "validate_arrays": True
    }
)

# Custom Arrow schema
from pyarrow import schema
custom_schema = schema([
    ('id', pa.int64()),
    ('name', pa.string()),
    ('timestamp', pa.timestamp('us'))
])

db.transfer_table(
    "events",
    options={
        "schema": custom_schema,
        "preserve_index": True
    }
)
 

### 5. Avro Format
 
# Schema evolution support
db = DatabaseConnection("POSTGRESQL") \
    .with_credentials_from_env() \
    .transfer_to(
        target_engine="MYSQL",
        format=TransferFormat.AVRO,
        options={
            "compression": "snappy",
            "sync_interval": 16000
        }
    )

# Complex type handling
complex_schema = {
    "type": "record",
    "name": "UserActivity",
    "fields": [
        {"name": "id", "type": "long"},
        {"name": "user", "type": "string"},
        {"name": "activities", "type": {
            "type": "array",
            "items": {
                "type": "record",
                "name": "Activity",
                "fields": [
                    {"name": "type", "type": "string"},
                    {"name": "timestamp", "type": "long"}
                ]
            }
        }}
    ]
}

db.transfer_table(
    "user_activities",
    options={
        "schema": complex_schema,
        "validate_records": True
    }
)

# Error handling with schema resolution
try:
    db.transfer_table("evolving_data")
except AvroSchemaError as e:
    if "schema mismatch" in str(e):
        # Attempt schema resolution
        resolver = AvroSchemaResolver(db)
        resolved_schema = resolver.resolve_schemas(
            "evolving_data",
            strategy="compatible"
        )
        db.transfer_table(
            "evolving_data",
            options={"schema": resolved_schema}
        )
 

### 6. ORC Format
 
# High-performance analytics transfer
db = DatabaseConnection("MYSQL") \
    .with_credentials_from_env() \
    .transfer_to(
        target_engine="DUCKDB",
        format=TransferFormat.ORC,
        options={
            "stripe_size": 67108864,  # 64MB
            "compression": "ZLIB",
            "batch_size": 1024
        }
    )

# Predicate pushdown
db.transfer_table(
    "analytics_data",
    options={
        "predicate_pushdown": True,
        "column_indices": True,
        "bloom_filter_columns": ["user_id", "date"]
    }
)

# Error handling with monitoring
class ORCTransferMonitor:
    def __init__(self):
        self.stripes_processed = 0
        self.rows_processed = 0
        
    def update(self, stripe_stats):
        self.stripes_processed += 1
        self.rows_processed += stripe_stats.row_count

monitor = ORCTransferMonitor()
try:
    db.transfer_table(
        "large_analytics_table",
        options={
            "monitor": monitor,
            "recovery_log": True
        }
    )
except ORCError as e:
    if "memory" in str(e):
        # Switch to streaming mode
        db.transfer_table(
            "large_analytics_table",
            options={
                "stream_mode": True,
                "buffer_size": "256MB"
            }
        )
 

## Format-Specific Utilities

### 1. Schema Management
 
class SchemaManager:
    def detect_schema_changes(
        self,
        source_conn: 'DatabaseConnection',
        target_conn: 'DatabaseConnection',
        table_name: str
    ) -> Dict[str, Any]:
        """Detect schema differences between source and target"""
        pass

    def generate_migration_plan(
        self,
        changes: Dict[str, Any]
    ) -> List[str]:
        """Generate SQL statements for schema migration"""
        pass

# Usage
schema_manager = SchemaManager()
changes = schema_manager.detect_schema_changes(
    source_conn,
    target_conn,
    "users"
)
 

### 2. Format Conversion
 
class FormatConverter:
    def convert(
        self,
        source_path: Path,
        target_format: TransferFormat,
        options: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Convert between formats"""
        pass

# Usage
converter = FormatConverter()
parquet_path = converter.convert(
    csv_path,
    TransferFormat.PARQUET,
    {"compression": "snappy"}
)
 

### 3. Performance Monitoring
 
class TransferMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.metrics = defaultdict(int)

    def update(
        self,
        rows_processed: int,
        bytes_processed: int
    ) -> None:
        """Update transfer metrics"""
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """Get transfer statistics"""
        pass

# Usage
monitor = TransferMonitor()
db.transfer_table(
    "large_table",
    options={"monitor": monitor}
)
 

## Performance Considerations

### Memory Management
 
class MemoryManager:
    def estimate_memory_requirements(
        self,
        table_info: Dict[str, Any],
        format: TransferFormat
    ) -> int:
        """Estimate memory requirements for transfer"""
        pass

    def suggest_batch_size(
        self,
        available_memory: int,
        row_size: int
    ) -> int:
        """Suggest optimal batch size"""
        pass

# Usage
memory_manager = MemoryManager()
batch_size = memory_manager.suggest_batch_size(
    available_memory=8 * 1024 * 1024 * 1024,  # 8GB
    row_size=1024  # 1KB per row
)
 

Would you like me to:
1. Add more specific examples for any format?
2. Include more utility functions?
3. Add benchmarking examples?
4. Expand error handling scenarios?