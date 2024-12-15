# Database Type Mapping System Documentation 📚

## Table of Contents

- [Overview](#overview)
- [Type Mapping Class](#type-mapping-class)
- [Initialization Parameters](#initialization-parameters)
- [Usage Examples](#usage-examples)
- [ETL Integration](#etl-integration)
- [Best Practices](#best-practices)

## Overview

🔄 The Database Type Mapping System provides a robust way to map data types between different database systems during ETL processes.

## Type Mapping Class

The core of the system is the `TypeMapping` dataclass:

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

### To summarize the key points about __post_init__ and type parameters 🔑

- __`__post_init__`__ ensures we have a valid list for fallbacks even if None is passed
- __`The type parameters`__ form a complete description of the data type's characteristics
- This becomes particularly useful in ETL when:

  - Mapping entire tables
  - Preserving data precision
  - Handling type conversions
  - Managing fallback scenarios

### Key Components 🔑

- __source_type__: Original data type
- __target_type__: Destination data type
- __is_lossy__: Flags potential data loss
- __fallback_types__: Alternative type options
- __Precision Parameters__: Length, precision, scale

## Initialization Parameters

### 📏 Length Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| max_length | Maximum length for string/binary | VARCHAR(50) |
| precision | Total digits for numeric | DECIMAL(10,2) |
| scale | Decimal places | DECIMAL(10,2) |

### 🔄 Fallback System

The fallback system works like SQL's COALESCE:

1. Try primary mapping
2. Try fallback types in order
3. Use default category mapping

## Usage Examples

### Basic Mapping

```python
mapping = TypeMapping(
    source_type="VARCHAR",
    target_type="TEXT",
    is_lossy=False,
    max_length=255
)
```

### With Fallbacks

```python
mapping = TypeMapping(
    source_type="MEDIUMINT",
    target_type="INTEGER",
    is_lossy=False,
    fallback_types=["INT", "BIGINT"]
)
```

## ETL Integration

### Table Column Iteration

```python
# Pseudo-code for mapping table columns
for column in source_table.columns:
    type_mapping = get_type_mapping(
        source_db="MYSQL",
        target_db="POSTGRESQL",
        source_type=column.type
    )
    # Use mapping for column creation
```

## Best Practices

### 🎯 When to Use Parameters

- __max_length__: String/binary types
- __precision/scale__: Numeric types
- __fallback_types__: When multiple types are acceptable

### ⚠️ Important Notes

1. Always initialize with appropriate parameters
2. Check is_lossy flag for data integrity
3. Validate mappings before bulk operations

### 💡 Tips

- Use fallback_types for flexible mapping
- Monitor lossy conversions
- Validate precision requirements

[Back to Top](#database-type-mapping-system-documentation-)
