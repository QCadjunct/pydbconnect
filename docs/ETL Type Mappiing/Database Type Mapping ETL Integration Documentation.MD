# Database Type Mapping System for ETL 📚

## Table of Contents

- [Overview](#overview)
- [Type Mapping Class](#type-mapping-class)
- [ETL Integration Examples](#etl-integration-examples)
  - [Basic Table Migration](#basic-table-migration)
  - [Complex Type Handling](#complex-type-handling)
  - [Batch Processing](#batch-processing)
  - [Error Handling](#error-handling)
- [Migration Patterns](#migration-patterns)
- [Best Practices](#best-practices)

## Overview

🔄 The Database Type Mapping System facilitates ETL processes by providing type conversion between different database systems.

## Type Mapping Class

```python
@dataclass
class TypeMapping:
    source_type: str
    target_type: str
    is_lossy: bool
    fallback_types: List[str] = None
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None

    def __post_init__(self):
        if self.fallback_types is None:
            self.fallback_types = []
```

## ETL Integration Examples

### Basic Table Migration

📋 Using structured analysis and mapping implementation for basic table migrations.

#### 1. Source Table Analysis

```python
def analyze_source_table(source_conn, table_name):
    """Analyze source table structure."""
    metadata_query = """
        SELECT column_name, data_type, 
               character_maximum_length,
               numeric_precision, numeric_scale
        FROM information_schema.columns
        WHERE table_name = ?
    """
    return execute_query(source_conn, metadata_query, [table_name])

# Usage
source_metadata = analyze_source_table(source_conn, "customers")
```

#### 2. Type Mapping Implementation

```python
def create_column_mappings(source_metadata, source_db, target_db):
    """Create mappings for all columns."""
    mappings = {}
    for column in source_metadata:
        mapping, actual_type = get_type_mapping(
            source_db, 
            target_db, 
            column.data_type
        )
        mappings[column.column_name] = {
            'mapping': mapping,
            'target_type': actual_type,
            'original_type': column.data_type
        }
    return mappings
```

#### 3. Target Table Creation

```python
def generate_create_table_sql(table_name, column_mappings):
    """Generate CREATE TABLE statement for target."""
    columns = []
    for col_name, mapping in column_mappings.items():
        col_type = mapping['target_type']
        if mapping['mapping'].max_length:
            col_type = f"{col_type}({mapping['mapping'].max_length})"
        columns.append(f"{col_name} {col_type}")
    
    return f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(columns) + "\n)"
```

### Complex Type Handling

🔄 Handling complex data types and precision requirements.

#### 1. BLOB/BINARY Data

```python
def handle_binary_data(source_type, target_db):
    binary_mappings = {
        "MSSQL": {
            "varbinary(max)": TypeMapping(
                "varbinary", "BYTEA", False,
                fallback_types=["BLOB"]
            ),
            "image": TypeMapping(
                "image", "BYTEA", True,
                fallback_types=["BLOB", "BINARY VARYING"]
            )
        }
    }
    return binary_mappings.get(target_db, {}).get(source_type)
```

#### 2. Numeric Precision

```python
def handle_numeric_conversion(source_col, mapping):
    """Handle numeric type conversion with precision."""
    if mapping.precision and mapping.scale:
        return f"{mapping.target_type}({mapping.precision},{mapping.scale})"
    elif mapping.precision:
        return f"{mapping.target_type}({mapping.precision})"
    return mapping.target_type
```

### Batch Processing

📦 Managing large data transfers through chunked processing.

#### 1. Chunked Data Migration

```python
def migrate_data_in_chunks(source_conn, target_conn, table_name, mappings, chunk_size=1000):
    """Migrate data in chunks to manage memory."""
    offset = 0
    while True:
        query = f"""
            SELECT * FROM {table_name} 
            ORDER BY id
            LIMIT {chunk_size} OFFSET {offset}
        """
        chunk = execute_query(source_conn, query)
        if not chunk:
            break
            
        # Transform data types according to mappings
        transformed_chunk = transform_chunk(chunk, mappings)
        
        # Insert transformed chunk
        insert_chunk(target_conn, table_name, transformed_chunk)
        offset += chunk_size
```

#### 2. Data Transformation

```python
def transform_chunk(chunk, mappings):
    """Transform data according to type mappings."""
    transformed = []
    for row in chunk:
        new_row = {}
        for col_name, value in row.items():
            mapping = mappings[col_name]['mapping']
            new_row[col_name] = transform_value(value, mapping)
        transformed.append(new_row)
    return transformed
```

### Error Handling

⚠️ Comprehensive error handling and validation strategies.

#### 1. Type Conversion Validation

```python
def validate_conversion(value, mapping):
    """Validate type conversion before execution."""
    try:
        if mapping.is_lossy:
            log_warning(f"Lossy conversion for value: {value}")
            
        if mapping.max_length and len(str(value)) > mapping.max_length:
            raise ValueError(f"Value exceeds maximum length: {value}")
            
        return True
    except Exception as e:
        log_error(f"Validation failed: {str(e)}")
        return False
```

#### 2. Migration Error Recovery

```python
def safe_migrate_table(source_conn, target_conn, table_name, mappings):
    """Migrate table with error recovery."""
    try:
        with target_conn.transaction():
            migrate_data_in_chunks(
                source_conn, 
                target_conn, 
                table_name, 
                mappings
            )
    except Exception as e:
        log_error(f"Migration failed: {str(e)}")
        rollback_migration(target_conn, table_name)
        raise
```

## Migration Patterns

🔋 Common patterns for different migration scenarios.

### 1. Sequential Migration

```python
def migrate_schema_sequential(tables, source_db, target_db):
    """Migrate tables in sequential order."""
    for table in tables:
        metadata = analyze_source_table(source_conn, table)
        mappings = create_column_mappings(metadata, source_db, target_db)
        safe_migrate_table(source_conn, target_conn, table, mappings)
```

### 2. Dependency-Aware Migration

```python
def migrate_schema_with_dependencies(tables_with_deps, source_db, target_db):
    """Migrate tables respecting foreign key dependencies."""
    processed = set()
    
    def process_table(table):
        if table in processed:
            return
        
        # Process dependencies first
        for dep in tables_with_deps[table]['dependencies']:
            process_table(dep)
            
        # Migrate the table
        metadata = analyze_source_table(source_conn, table)
        mappings = create_column_mappings(metadata, source_db, target_db)
        safe_migrate_table(source_conn, target_conn, table, mappings)
        processed.add(table)
```

## Best Practices

💡 Recommended practices for optimal ETL performance and reliability.

### Performance Optimization

- Use appropriate chunk sizes for batch processing
- Index management during migration
- Parallel processing for independent tables

### Data Integrity

- Validate all type conversions
- Handle NULL values appropriately
- Maintain referential integrity

### Error Recovery

- Transaction management
- Logging and monitoring
- Rollback procedures
