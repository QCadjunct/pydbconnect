"""MSSQL Example using execute_query_to_dataframe with fluent design."""

from pathlib import Path
from core.connector import DatabaseConnector
from templates.constraints import TargetDatabaseEngine, TargetDatabaseConnectionStringOption, FileFormat


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

        # Set up output directory
        output_dir = Path("output/shipping_analysis")
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nOutput directory: {output_dir}")

        # Example 1: Chain to CSV then get DataFrame
        print("\n=== Example 1: Basic CSV Export ===")
        df1 = (
            connector.execute_query_to_dataframe(query)
            .save_to_file(output_dir / "shipper_analysis_no_index.csv", index=False)
            .to_dataframe()
        )

        print("\nData without index:")
        print(df1.head())

        # Example 2: Chain with index and multiple formats
        print("\n=== Example 2: Multi-format Export ===")
        df2 = (
            connector.execute_query_to_dataframe(query, index_col="Shipper")
            .save_to_file(output_dir / "shipper_analysis.csv", file_format=FileFormat.CSV, index=True)
            .save_to_file(output_dir / "shipper_analysis.xlsx", file_format=FileFormat.XLSX, index=True)
            .save_to_file(output_dir / "shipper_analysis.parquet", file_format=FileFormat.PARQUET)
            .save_to_file(output_dir / "shipper_analysis.json", file_format=FileFormat.JSON, orient="records")
            .to_dataframe()
        )

        print("\nData with Shipper as index:")
        print(df2.head())

    except Exception as e:
        print(f"Database operation failed: {str(e)}")
        raise

    finally:
        connector.close()


if __name__ == "__main__":
    main()
