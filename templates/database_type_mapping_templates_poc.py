# database_type_mapping_templates.py
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass


@dataclass
class TypeMapping:
    source_type: str
    target_type: str
    is_problematic_lossy: bool  # True if data loss risk requires attention
    fallback_type: Optional[str] = (
        None  # Similar to COALESCE, provides safe alternative
    )
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    notes: Optional[str] = None  # Documents any conversion considerations


class DatabaseType(Enum):
    MSSQL = "MSSQL"
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    SQLITE3 = "SQLITE3"
    DUCKDB = "DUCKDB"
    PSYCOPG2 = "PSYCOPG2"


# Type mapping templates following the same structure as engine templates
TYPE_MAPPINGS: Dict[str, Dict[str, Any]] = {
    "MSSQL": {
        "DEFAULT_MAPPINGS": {
            "NUMERIC": {
                "bit": TypeMapping("bit", "BOOLEAN", False, "SMALLINT"),
                "tinyint": TypeMapping("tinyint", "SMALLINT", False, "INTEGER"),
                "smallint": TypeMapping("smallint", "SMALLINT", False, "INTEGER"),
                "int": TypeMapping("int", "INTEGER", False, "BIGINT"),
                "bigint": TypeMapping("bigint", "BIGINT", False, "NUMERIC"),
                "decimal": TypeMapping("decimal", "DECIMAL", False, "NUMERIC"),
                "numeric": TypeMapping("numeric", "NUMERIC", False, None),
                "float": TypeMapping("float", "DOUBLE PRECISION", False, "NUMERIC"),
                "real": TypeMapping("real", "REAL", False, "DOUBLE PRECISION"),
            },
            "CHARACTER": {
                "char": TypeMapping("char", "CHAR", False, "VARCHAR"),
                "varchar": TypeMapping("varchar", "VARCHAR", False, "TEXT"),
                "text": TypeMapping("text", "TEXT", False, None),
                "nchar": TypeMapping("nchar", "CHAR", False, "VARCHAR"),
                "nvarchar": TypeMapping(
                    "nvarchar",
                    "VARCHAR",
                    False,
                    "TEXT",
                    notes="Consider max length for large text",
                ),
                "ntext": TypeMapping("ntext", "TEXT", False, None),
            },
            "BINARY": {
                "binary": TypeMapping("binary", "BYTEA", False, None),
                "varbinary": TypeMapping("varbinary", "BYTEA", False, None),
                "image": TypeMapping(
                    "image",
                    "BYTEA",
                    True,
                    None,
                    notes="Legacy type, consider chunking large objects",
                ),
                "varbinary(max)": TypeMapping(
                    "varbinary(max)",
                    "BYTEA",
                    False,
                    None,
                    notes="May require streaming for very large objects",
                ),
            },
        }
    },
    "MYSQL": {
        "DEFAULT_MAPPINGS": {
            "NUMERIC": {
                "bit": TypeMapping("bit", "BOOLEAN", False, "SMALLINT"),
                "tinyint": TypeMapping("tinyint", "SMALLINT", False, "INTEGER"),
                "smallint": TypeMapping("smallint", "SMALLINT", False, "INTEGER"),
                "mediumint": TypeMapping(
                    "mediumint",
                    "INTEGER",
                    False,
                    "BIGINT",
                    notes="Safe conversion, INTEGER fully contains MEDIUMINT range",
                ),
                "int": TypeMapping("int", "INTEGER", False, "BIGINT"),
                "bigint": TypeMapping("bigint", "BIGINT", False, "NUMERIC"),
                "decimal": TypeMapping("decimal", "DECIMAL", False, "NUMERIC"),
            },
            "BINARY": {
                "binary": TypeMapping("binary", "BYTEA", False, None),
                "varbinary": TypeMapping("varbinary", "BYTEA", False, None),
                "tinyblob": TypeMapping("tinyblob", "BYTEA", False, None),
                "blob": TypeMapping("blob", "BYTEA", False, None),
                "mediumblob": TypeMapping(
                    "mediumblob",
                    "BYTEA",
                    False,
                    None,
                    notes="Consider chunking for large objects",
                ),
                "longblob": TypeMapping(
                    "longblob",
                    "BYTEA",
                    True,
                    None,
                    notes="May require streaming for very large objects",
                ),
            },
        }
    },
    "DUCKDB": {
        "DEFAULT_MAPPINGS": {
            "NUMERIC": {
                "tinyint": TypeMapping("tinyint", "SMALLINT", False, "INTEGER"),
                "smallint": TypeMapping("smallint", "SMALLINT", False, "INTEGER"),
                "integer": TypeMapping("integer", "INTEGER", False, "BIGINT"),
                "bigint": TypeMapping("bigint", "BIGINT", False, "NUMERIC"),
                "decimal": TypeMapping("decimal", "DECIMAL", False, "NUMERIC"),
            },
            "BINARY": {
                "blob": TypeMapping(
                    "blob",
                    "BYTEA",
                    False,
                    None,
                    notes="Direct mapping to PostgreSQL BYTEA",
                ),
                "varbinary": TypeMapping("varbinary", "BYTEA", False, None),
            },
        }
    },
}


def get_type_mapping(
    source_db: str, target_db: str, source_type: str
) -> Tuple[TypeMapping, bool]:
    """
    Get type mapping between source and target databases with fallback handling.
    Returns tuple of (mapping, used_fallback) where used_fallback indicates if primary mapping was found.
    """
    source_mappings = TYPE_MAPPINGS.get(source_db, {}).get("DEFAULT_MAPPINGS", {})

    # Search through all categories
    for category in source_mappings.values():
        if mapping := category.get(source_type.lower()):
            return mapping, False

    # Look for fallback mapping if exact match not found
    for category in source_mappings.values():
        for mapping in category.values():
            if mapping.source_type.lower().startswith(source_type.lower()):
                return mapping, True

    # Return most compatible general type mapping as last resort
    default_mapping = TypeMapping(
        source_type=source_type,
        target_type="TEXT",  # Most permissive type as last resort
        is_problematic_lossy=True,
        notes="Fallback mapping - validate data compatibility",
    )
    return default_mapping, True


def test_type_mappings():
    # Test exact mapping
    mapping, used_fallback = get_type_mapping("MYSQL", "POSTGRESQL", "mediumint")
    print(f"MySQL mediumint maps to: {mapping.target_type}")
    print(f"Used fallback: {used_fallback}")
    print(f"Notes: {mapping.notes}")

    # Test binary mapping
    mapping, used_fallback = get_type_mapping("MSSQL", "POSTGRESQL", "varbinary(max)")
    print(f"\nMSSQL varbinary(max) maps to: {mapping.target_type}")
    print(f"Is problematic lossy: {mapping.is_problematic_lossy}")
    print(f"Notes: {mapping.notes}")


if __name__ == "__main__":
    test_type_mappings()
