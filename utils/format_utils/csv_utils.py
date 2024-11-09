# pydatabaseconnection/utils/format_utils/csv_utils.py
from typing import Dict, Any, Optional, List, Union
import pandas as pd
import csv
from pathlib import Path
from io import StringIO
import chardet

class CSVUtils:
    """Utilities for CSV format operations"""
    
    @staticmethod
    def detect_dialect(
        file_path: Union[str, Path],
        sample_size: int = 1024
    ) -> csv.Dialect:
        """Detect CSV dialect from file"""
        with open(file_path, 'rb') as f:
            sample = f.read(sample_size)
            
        # Detect encoding
        detected = chardet.detect(sample)
        encoding = detected['encoding']
        
        # Detect dialect
        return csv.Sniffer().sniff(
            sample.decode(encoding or 'utf-8')
        )

    @staticmethod
    def analyze_csv(
        file_path: Union[str, Path],
        sample_rows: Optional[int] = None
    ) -> Dict[str, Any]:
        """Analyze CSV file structure and content"""
        dialect = CSVUtils.detect_dialect(file_path)
        
        df = pd.read_csv(
            file_path,
            nrows=sample_rows,
            dialect=dialect
        )
        
        analysis = {
            "columns": len(df.columns),
            "sample_rows": len(df),
            "dialect": {
                "delimiter": dialect.delimiter,
                "quotechar": dialect.quotechar,
                "escapechar": dialect.escapechar,
                "doublequote": dialect.doublequote
            },
            "column_types": df.dtypes.to_dict(),
            "null_counts": df.isnull().sum().to_dict(),
            "unique_counts": {
                col: df[col].nunique()
                for col in df.columns
            }
        }
        
        return analysis

    @staticmethod
    def optimize_dtypes(
        df: pd.DataFrame,
        memory_threshold: float = 0.5
    ) -> pd.DataFrame:
        """Optimize DataFrame data types for memory usage"""
        initial_memory = df.memory_usage(deep=True).sum()
        
        # Optimize numeric columns
        for col in df.select_dtypes(include=['int']).columns:
            col_min, col_max = df[col].min(), df[col].max()
            
            # Find smallest possible integer type
            for dtype in ['int8', 'int16', 'int32', 'int64']:
                if pd.api.types.is_integer_dtype(dtype):
                    info = np.iinfo(dtype)
                    if col_min >= info.min and col_max <= info.max:
                        df[col] = df[col].astype(dtype)
                        break
        
        # Optimize string columns
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) < memory_threshold:
                df[col] = df[col].astype('category')
        
        return df

    @staticmethod
    def split_csv(
        input_path: Union[str, Path],
        output_dir: Union[str, Path],
        chunk_size: int,
        preserve_header: bool = True
    ) -> List[Path]:
        """Split large CSV file into smaller chunks"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_files = []
        
        for i, chunk in enumerate(pd.read_csv(input_path, chunksize=chunk_size)):
            output_path = output_dir / f"chunk_{i:04d}.csv"
            chunk.to_csv(
                output_path,
                index=False,
                header=preserve_header or i == 0
            )
            output_files.append(output_path)
            
        return output_files

    @staticmethod
    def validate_csv(
        file_path: Union[str, Path],
        schema: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Validate CSV file against schema"""
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check file readability
            df = pd.read_csv(file_path, nrows=1)
            
            if schema:
                # Validate columns
                missing_cols = set(schema.keys()) - set(df.columns)
                extra_cols = set(df.columns) - set(schema.keys())
                
                if missing_cols:
                    validation["errors"].append(
                        f"Missing columns: {missing_cols}"
                    )
                    
                if extra_cols:
                    validation["warnings"].append(
                        f"Extra columns: {extra_cols}"
                    )
                
                # Validate data types
                for col, expected_type in schema.items():
                    if col in df.columns:
                        actual_type = df[col].dtype
                        if not pd.api.types.is_dtype_equal(actual_type, expected_type):
                            validation["warnings"].append(
                                f"Column '{col}' type mismatch: "
                                f"expected {expected_type}, got {actual_type}"
                            )
                            
            validation["is_valid"] = not validation["errors"]
            
        except Exception as e:
            validation["is_valid"] = False
            validation["errors"].append(str(e))
            
        return validation

    @staticmethod
    def merge_csv_files(
        input_files: List[Union[str, Path]],
        output_path: Union[str, Path],
        **kwargs: Any
    ) -> Path:
        """Merge multiple CSV files into one"""
        output_path = Path(output_path)
        first_file = True
        
        for file in input_files:
            df = pd.read_csv(file)
            df.to_csv(
                output_path,
                mode='w' if first_file else 'a',
                header=first_file,
                index=False,
                **kwargs
            )
            first_file = False
            
        return output_path
```

These utilities provide comprehensive functionality for both SQL and CSV formats:

**SQL Utilities**:
1. SQL file parsing
2. Schema analysis
3. Batch insert generation
4. Dependency extraction
5. Index optimization

**CSV Utilities**:
1. Dialect detection
2. File analysis
3. Data type optimization
4. File splitting and merging
5. Schema validation

Example usage:

```python
# SQL Utilities Example
sql_file = Path("schema.sql")
sql_utils = SQLUtils()

# Analyze schema
statements = sql_utils.parse_sql_file(sql_file)
for stmt in statements:
    analysis = sql_utils.analyze_schema(stmt)
    deps = sql_utils.extract_dependencies(stmt)
    
    # Generate optimized indexes
    indexes = sql_utils.optimize_indexes(
        stmt,
        table_stats={"id": {"unique_ratio": 1.0}}
    )

# CSV Utilities Example
csv_utils = CSVUtils()

# Analyze CSV file
analysis = csv_utils.analyze_csv(
    "large_file.csv",
    sample_rows=1000
)

# Split large file
chunks = csv_utils.split_csv(
    "large_file.csv",
    "output_dir",
    chunk_size=100000
)

# Validate against schema
schema = {
    "id": "int64",
    "name": "object",
    "value": "float64"
}

validation = csv_utils.validate_csv(
    "data.csv",
    schema=schema
)