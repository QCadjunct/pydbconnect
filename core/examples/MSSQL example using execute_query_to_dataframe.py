"""MSSQL Example using execute_query_to_dataframe with fluent design and advanced format options."""

from pathlib import Path
from core.connector import DatabaseConnector
from templates.constraints import (
    ChangeDefaultUsernameAndPassword,
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
    FileFormat,
)


def main():
    # Initialize connector with MSSQL configuration
    connector = DatabaseConnector(
        target_database_engine=TargetDatabaseEngine.MSSQL,
        target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
    )

    try:
        # Configure connection parameters
        connector.finalization_of_connection_parameters(
            DRIVER="{ODBC Driver 17 for SQL Server}",
            SERVER="127.0.0.1",
            PORT_NUMBER=13001,
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

        # Set up output directory
        output_dir = Path("output/shipping_analysis")
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nOutput directory: {output_dir}")

        # Example 1: Basic CSV Export
        print("\n=== Example 1: Basic CSV Export ===")
        df1 = (
            connector.execute_query_to_dataframe(query)
            .save_to_file(output_dir / "shipper_analysis_no_index.csv", index=False)
            .to_dataframe()
        )

        print("\nData without index:")
        print(df1.head())

        # Example 2: Multi-format Export with basic options
        print("\n=== Example 2: Multi-format Export (Basic) ===")
        df2 = (
            connector.execute_query_to_dataframe(query, index_col="Shipper")
            .save_to_file(output_dir / "shipper_analysis.csv", file_format=FileFormat.CSV, index=True)
            .save_to_file(output_dir / "shipper_analysis.xlsx", file_format=FileFormat.XLSX, index=True)
            .save_to_file(output_dir / "shipper_analysis.parquet", file_format=FileFormat.PARQUET)
            .save_to_file(output_dir / "shipper_analysis.json", file_format=FileFormat.JSON, orient="records")
            .to_dataframe()
        )

        print("\nData with Shipper as index (basic options):")
        print(df2.head())

        # Example 3: Advanced Format Options
        print("\n=== Example 3: Advanced Format Options ===")

        # Define advanced format options
        format_options = {
            "compression": "gzip",
            "encoding": "utf-8",
            "batch_size": 1000,
            "csv_options": {"sep": ";", "date_format": "%Y-%m-%d"},
            "excel_options": {"sheet_name": "Shipping Analysis", "freeze_panes": (1, 0)},
            "parquet_options": {"engine": "pyarrow", "compression": "snappy"},
        }

        # Apply advanced options with batching
        df3 = (
            connector.execute_query_to_dataframe(query, index_col="Shipper")
            .save_to_file(
                output_dir / "shipper_analysis_advanced.csv",
                file_format=FileFormat.CSV,
                format_options=format_options,
                index=True,
            )
            .save_to_file(
                output_dir / "shipper_analysis_advanced.xlsx",
                file_format=FileFormat.XLSX,
                format_options=format_options,
            )
            .save_to_file(
                output_dir / "shipper_analysis_advanced.parquet",
                file_format=FileFormat.PARQUET,
                format_options=format_options,
            )
            .to_dataframe()
        )

        print("\nData with advanced format options:")
        print(df3.head())

        # Display available files
        print("\nGenerated files:")
        for file in sorted(output_dir.glob("*.*")):
            print(f"- {file.name}")

    except Exception as e:
        print(f"Database operation failed: {str(e)}")
        raise

    finally:
        connector.close()


if __name__ == "__main__":
    main()
