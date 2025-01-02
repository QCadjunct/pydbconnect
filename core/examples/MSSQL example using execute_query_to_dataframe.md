# 🔌 MSSQL example using methodexecute_query_to_dataframe v1.0

## 📋 Version History

| Version | Date | Author | Notes |
|---------|------|---------|-------|
| 1.0.0 | 2025-01-02 | Peter Heller & Claude.ai 3.5 Sonnet | Initial documentation & using pairs programming|

## Table of Contents

- [Overview](#-overview)
- [Complete Example](#-complete-example)
- [Core Methods](#-core-methods)
  - [execute_query_to_dataframe](#-execute_query_to_dataframe)
  - [save_to_file](#-save_to_file)
  - [to_dataframe](#-to_dataframe)
- [Format Options](#-format-options)
- [Usage Examples](#-usage-examples)
- [Dependencies](#-dependencies)
- [Best Practices](#-best-practices)

## 🎯 Overview

[⬆️ Back to Top](#-Table-of-Contents)

The Database Connector provides a fluent interface for executing SQL queries and handling data exports in multiple formats.

### 🔧 Key Features

- Fluent interface design
- Multiple export formats
- Batch processing
- Advanced formatting options
- Memory-efficient operations

## 💻 Complete Example

```python
"""Complete working example of Database Connector usage with all features."""

from pathlib import Path
from core.connector import DatabaseConnector, FormatOptions
from templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
    FileFormat
)

def main():
    # Initialize connector with MSSQL configuration
    connector = DatabaseConnector(
        target_database_engine=TargetDatabaseEngine.MSSQL,
        target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
    )

    try:
        connector.finalization_of_connection_parameters(
            DRIVER="{ODBC Driver 17 for SQL Server}",
            SERVER="127.0.0.1",
            PORT_NUMBER=15001,
            DATABASE_NAME="Fall2024LastTest",
        )

        connector.connect_to_database()

        query = """
            SELECT 
                CONCAT(s.ShipperCompanyName, ' : (', s.ShipperId, ')') as Shipper,
                COALESCE(odt.FiscalYear,' ') as FiscalYear,
                COALESCE(odt.SemiAnnual,' ') as SemiAnnual,
                COALESCE(odt.Quarters,' ') as Quarters,
                COUNT(DISTINCT o.OrderId) as NumberOfOrders,
                AVG(o.DaysToShipItem) as AverageDaysToShipItem,
                SUM(od.TotalLineCost) as LineCostTotal,
                SUM(od.TotalDiscountedLineCost) as DiscountedLineCostTotal
            FROM Sales.OrderDetail as od
                INNER JOIN Sales.[Order] as o
                    ON o.OrderId = od.OrderId
                INNER JOIN Sales.Shipper as s 
                    ON s.ShipperId = o.ShipperId
                INNER JOIN Sales.OrderDateTable as odt
                    ON odt.OrderDate = o.OrderDate
            GROUP BY ROLLUP (
                CONCAT(s.ShipperCompanyName, ' : (', s.ShipperId, ')'),
                odt.FiscalYear,
                odt.SemiAnnual,
                odt.Quarters
            )
            ORDER BY 
                CONCAT(s.ShipperCompanyName, ' : (', s.ShipperId, ')'),
                odt.FiscalYear,
                odt.SemiAnnual,
                odt.Quarters;
        """

        format_options = FormatOptions(
            compression="gzip",
            encoding="utf-8",
            batch_size=1000,
            csv_options={
                "sep": ";",
                "date_format": "%Y-%m-%d"
            },
            excel_options={
                "sheet_name": "Shipping Analysis",
                "freeze_panes": (1, 0)
            },
            parquet_options={
                "engine": "pyarrow",
                "compression": "snappy"
            }
        )

        df = (connector
            .execute_query_to_dataframe(query, index_col="Shipper")
            .save_to_file(
                "output/shipping_analysis.csv",
                file_format=FileFormat.CSV,
                format_options=format_options,
                index=True
            )
            .save_to_file(
                "output/shipping_analysis.xlsx",
                file_format=FileFormat.XLSX,
                format_options=format_options
            )
            .save_to_file(
                "output/shipping_analysis.parquet",
                file_format=FileFormat.PARQUET,
                format_options=format_options
            )
            .to_dataframe())

    finally:
        connector.close()

if __name__ == "__main__":
    main()
```

## 🔧 Core Methods

### 📊 execute_query_to_dataframe

[⬆️ Back to Top](#-database-connector-documentation-v1.0)

```python
@ensure_connected
def execute_query_to_dataframe(self, query: str, index_col: Optional[str] = None) -> "DatabaseConnector":
    """Execute query and return connector for chaining."""
    if not self._connection or not self.is_database_active:
        raise ConnectionError("Database connection not active")

    try:
        with self._cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            data = [list(row) for row in cursor.fetchall()]
            
            df = pd.DataFrame(data, columns=columns) if data else pd.DataFrame()
            if index_col and index_col in df.columns:
                df.set_index(index_col, inplace=True)
                
            self._current_df = df
            return self
            
    except Exception as e:
        raise DatabaseError(f"Query execution failed: {e}")
```

**Features:**

- ✅ Connection validation
- ✅ Safe cursor management
- ✅ Flexible index handling
- ✅ Error propagation
- ✅ Method chaining support

### 💾 save_to_file

[⬆️ Back to Top](#-database-connector-documentation-v1.0)

```python
def save_to_file(
    self, 
    path: Union[str, Path], 
    file_format: Optional[FileFormat] = None, 
    format_options: Optional[FormatOptions] = None,
    **kwargs
) -> "DatabaseConnector":
    """Save current DataFrame using specified format with options."""
    if not hasattr(self, '_current_df'):
        return self
        
    path = Path(path)
    if file_format is None:
        extension = path.suffix.lstrip('.')
        file_format = FileFormat.from_extension(extension)
        if file_format is None:
            raise ValueError(f"Unsupported file extension: {extension}")
    
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        
        save_kwargs = kwargs.copy()
        if format_options:
            save_kwargs.update(format_options.get_format_options(file_format))
            
            if format_options.batch_size and hasattr(self._current_df, 'shape'):
                total_rows = self._current_df.shape[0]
                for i in range(0, total_rows, format_options.batch_size):
                    batch_df = self._current_df.iloc[i:i + format_options.batch_size]
                    batch_path = path.parent / f"{path.stem}_batch_{i//format_options.batch_size}{path.suffix}"
                    file_format.write_dataframe(batch_df, str(batch_path), **save_kwargs)
                    print(f"Saved batch: {batch_path}")
                return self
        
        file_format.write_dataframe(self._current_df, str(path), **save_kwargs)
        print(f"Saved: {path}")
        
    except Exception as e:
        print(f"Warning: Failed to save {path}: {str(e)}")
    
    return self
```

**Features:**

- ✅ Multiple format support
- ✅ Automatic directory creation
- ✅ Batch processing
- ✅ Flexible options handling
- ✅ Error handling

### 📈 to_dataframe

[⬆️ Back to Top](#-database-connector-documentation-v1.0)

```python
def to_dataframe(self) -> pd.DataFrame:
    """Get the current DataFrame and clear it from memory."""
    if not hasattr(self, '_current_df'):
        return pd.DataFrame()
        
    df = self._current_df
    del self._current_df
    return df
```

**Features:**

- ✅ Memory cleanup
- ✅ Safe state handling
- ✅ Default empty return

## 🛠️ Format Options

```python
@dataclass
class FormatOptions:
    """Configuration options for file format handling."""
    
    compression: Optional[str] = None
    encoding: Optional[str] = None
    date_format: Optional[str] = None
    float_format: Optional[str] = None
    batch_size: Optional[int] = None
    chunk_size: Optional[int] = None
    
    excel_options: Optional[Dict[str, Any]] = None
    json_options: Optional[Dict[str, Any]] = None
    csv_options: Optional[Dict[str, Any]] = None
    parquet_options: Optional[Dict[str, Any]] = None
```

## 📝 Usage Examples

### Basic Usage

```python
# Simple CSV export
df = (connector
    .execute_query_to_dataframe(query)
    .save_to_file("output.csv", index=False)
    .to_dataframe())
```

### Advanced Usage

```python
# Advanced format options
format_options = FormatOptions(
    compression="gzip",
    batch_size=1000,
    excel_options={"sheet_name": "Report"}
)

# Multi-format export
df = (connector
    .execute_query_to_dataframe(query, index_col="ID")
    .save_to_file(
        "output.xlsx",
        file_format=FileFormat.XLSX,
        format_options=format_options
    )
    .save_to_file(
        "output.parquet",
        file_format=FileFormat.PARQUET,
        format_options=format_options
    )
    .to_dataframe())
```

## 📦 Dependencies

Core Requirements:

- `pandas`: DataFrame operations
- `pathlib`: Path handling
- `typing`: Type hints

Optional Features:

- `openpyxl`: Excel support
- `pyarrow`: Parquet support
- `tables`: HDF5 support

## ⚡ Best Practices

### Memory Management

- Use batch processing for large datasets
- Clean up DataFrames after use
- Monitor memory usage with large operations

### Error Handling

- Check dependencies before operations
- Use try-except blocks appropriately
- Provide meaningful error messages

### Performance Optimization

- Use appropriate batch sizes
- Choose correct compression options
- Monitor disk space for large operations

### Code Style

- Follow fluent interface patterns
- Maintain consistent error handling
- Use type hints for better IDE support

## 🔄 Maintenance Notes

### Regular Tasks

- Update dependencies
- Check for new format support
- Monitor performance metrics
- Update documentation

### Version Control

- Tag major releases
- Document breaking changes
- Maintain backwards compatibility

---

📅 Last Updated: 2025-01-02  
🔖 Version: 1.0.0  
📝 Status: Production Ready

