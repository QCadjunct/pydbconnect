# 📊 Query Execution Patterns

## Table of Contents

- [Simple Queries](#simple-queries)
- [Complex Queries](#complex-queries)
- [Data Transformation](#data-transform)
- [Performance Patterns](#performance)

<a name="simple-queries"></a>

## 🎯 Simple Queries [↑](#table-of-contents)

### Basic Select Query

```python
with db.connect_to_database() as conn:
    # Version check - Single value query
    conn.execute_query_to_prettytable(
        "SELECT @@VERSION as Version",
        print_result=True
    )

    # Simple table query
    conn.execute_query_to_prettytable(
        """
        SELECT TOP 10 ProductID, Name, ListPrice
        FROM Production.Product
        ORDER BY ProductID
        """,
        print_result=True
    )
```

### Parameter Convention

```python
# Correct - Using uppercase for parameters
db.finalization_of_connection_parameters(
    DRIVER="{ODBC Driver 17 for SQL Server}",
    SERVER="127.0.0.1",
    PORT_NUMBER=13001,
    DATABASE_NAME="AdventureWorks2019"
)

# Incorrect - Mixed case (will cause issues)
db.finalization_of_connection_parameters(
    driver="{ODBC Driver 17 for SQL Server}",  # ❌
    Server="127.0.0.1",                        # ❌
    PORT_NUMBER=13001                          # ✅
)
```

<a name="complex-queries"></a>

## 🔄 Complex Queries [↑](#table-of-contents)

### Using DataFrame Output

```python
# Complex join with DataFrame result
def get_product_analysis():
    query = """
    SELECT 
        p.ProductID,
        p.Name AS ProductName,
        c.Name AS Category,
        p.ListPrice,
        i.Quantity,
        i.Shelf,
        i.Bin
    FROM 
        Production.Product p
        JOIN Production.ProductCategory c 
            ON p.ProductSubcategoryID = c.ProductCategoryID
        JOIN Production.ProductInventory i 
            ON p.ProductID = i.ProductID
    WHERE 
        p.ListPrice > 0
    """
    return conn.execute_query_to_dataframe(
        query,
        index_col="ProductID"
    )
```

### Multi-Step Operations

```python
def inventory_analysis():
    with db.connect_to_database() as conn:
        # Step 1: Get current inventory
        current = conn.execute_query_to_prettytable(
            """
            SELECT TOP 5 *
            FROM Production.ProductInventory
            """,
            print_result=True
        )

        # Step 2: Show inventory statistics
        stats = conn.execute_query_to_prettytable(
            """
            SELECT 
                COUNT(*) as TotalProducts,
                AVG(Quantity) as AvgQuantity,
                MAX(Quantity) as MaxQuantity,
                MIN(Quantity) as MinQuantity
            FROM Production.ProductInventory
            """,
            print_result=True
        )

        return current, stats
```

<a name="data-transform"></a>

## 📈 Data Transformation [↑](#table-of-contents)

### PrettyTable Formatting

```python
def format_inventory_report():
    table = conn.execute_query_to_prettytable(
        """
        SELECT 
            p.ProductID,
            p.Name,
            i.Quantity,
            i.Shelf,
            i.Bin
        FROM 
            Production.Product p
            JOIN Production.ProductInventory i 
                ON p.ProductID = i.ProductID
        """
    )
    
    # Customize table appearance
    if table:
        table.align = 'l'  # Left align text
        table.align['Quantity'] = 'r'  # Right align numbers
        table.max_width['Name'] = 30  # Limit column width
        print(table)
```

<a name="performance"></a>

## ⚡ Performance Patterns [↑](#table-of-contents)

### Optimized Query Execution

```python
def efficient_data_retrieval():
    # Use specific columns instead of SELECT *
    query = """
    SELECT ProductID, Quantity, Shelf
    FROM Production.ProductInventory
    WHERE Quantity > 0
    """
    
    # Choose appropriate output format
    if need_analysis:
        return conn.execute_query_to_dataframe(query)  # For data manipulation
    else:
        return conn.execute_query_to_prettytable(query)  # For display
```

### Batch Processing Pattern

```python
def process_in_batches(batch_size=1000):
    query = f"""
    SELECT ProductID, Name, ListPrice
    FROM Production.Product
    ORDER BY ProductID
    OFFSET 0 ROWS
    FETCH NEXT {batch_size} ROWS ONLY
    """
    
    while True:
        batch = conn.execute_query_to_dataframe(query)
        if batch.empty:
            break
        
        # Process batch
        yield batch
```
