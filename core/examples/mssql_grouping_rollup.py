"""MSSQL Connection Demo."""

from core.connector import DatabaseConnector, DatabaseError, ConnectionError
from templates.constraints import (
    TargetDatabaseEngine,
    TargetDatabaseConnectionStringOption,
)


def main():
    """MSSQL connection demonstration."""
    try:
        # Initialize connector
        print("\nInitializing connector...")
        db = DatabaseConnector(
            target_database_engine=TargetDatabaseEngine.MSSQL,
            target_database_engine_connect_option=TargetDatabaseConnectionStringOption.DefaultFormatAndDefaultUserPwd,
        )

        # Test connection
        print("\nTesting connection...")
        with (
            db.set_credentials_based_on_connect_option()
            .finalization_of_connection_parameters(
                DRIVER="{ODBC Driver 17 for SQL Server}",
                SERVER="127.0.0.1",
                PORT_NUMBER=13001,
                DATABASE_NAME="Fall2024LastTest",
            )
            .connect_to_database()
        ) as conn:
            print("\nExecuting queries...")

            # Version check
            print("\n1. SQL Server Version:")
            conn.execute_query_to_prettytable(
                "SELECT @@VERSION as Version", print_result=True
            )

            # Product query
            print("\n2. rollup(hierarchically using scalar functions (inefficient):")
            conn.execute_query_to_prettytable(
                """
                    select concat(s.ShipperCompanyName, ' : (', s.ShipperId, ')') as Shipper,
                        coalesce(Utils.DefineFiscalYear(o.OrderDate),' ') as FiscalYear,
                        coalesce(Utils.DefineFiscalYearSemiAnnual(o.OrderDate),' ') as SemiAnnual,
                        coalesce(Utils.DefineFiscalYearQuarters(o.OrderDate),' ') as Quarters,
                        count(distinct o.OrderId) as NumberOfOrders,
                        avg(o.DaysToShipItem) as AverageDaysToShipItem,
                        sum(od.TotalLineCost) as LineCostTotal,
                        sum(od.TotalDiscountedLineCost) as DiscountedLineCostTotal
                    from [Sales].[OrderDetail] as od
                        inner join Sales.[Order] as o
                            on o.OrderId = od.OrderId
                        inner join Sales.Shipper as s
                            on s.ShipperId = o.ShipperId
                    group by rollup(concat(s.ShipperCompanyName, ' : (', s.ShipperId, ')'), Utils.DefineFiscalYear(o.OrderDate), Utils.DefineFiscalYearSemiAnnual(o.OrderDate), Utils.DefineFiscalYearQuarters(o.OrderDate))
                    order by concat(s.ShipperCompanyName, ' : (', s.ShipperId, ')'),
                            Utils.DefineFiscalYear(o.OrderDate),
                            Utils.DefineFiscalYearSemiAnnual(o.OrderDate),
                            Utils.DefineFiscalYearQuarters(o.OrderDate);
            """,
                print_result=True,
            )

            # Product query
            print("\n3. rollup(hierarchically using a date table used in OLAP):")
            conn.execute_query_to_prettytable(
                """
                    select concat(s.ShipperCompanyName, ' : (', s.ShipperId, ')') as Shipper,
                        coalesce(odt.FiscalYear,' ') as FiscalYear,
                        coalesce(odt.SemiAnnual,' ') as SemiAnnual,
                        coalesce(odt.Quarters,' ') as Quarters,
                        count(distinct o.OrderId) as NumberOfOrders,
                        avg(o.DaysToShipItem) as AverageDaysToShipItem,
                        sum(od.TotalLineCost) as LineCostTotal,
                        sum(od.TotalDiscountedLineCost) as DiscountedLineCostTotal
                    from [Sales].[OrderDetail] as od
                        inner join Sales.[Order] as o
                            on o.OrderId = od.OrderId
                        inner join Sales.Shipper as s
                            on s.ShipperId = o.ShipperId
                        inner join Sales.OrderDateTable as odt
                            on odt.OrderDate = o.OrderDate
                    group by rollup(concat(s.ShipperCompanyName, ' : (', s.ShipperId, ')'), odt.FiscalYear, odt.SemiAnnual, odt.Quarters)
                    order by concat(s.ShipperCompanyName, ' : (', s.ShipperId, ')'),
                            odt.FiscalYear,
                            odt.SemiAnnual,
                            odt.Quarters;
            """,
                print_result=True,
            )

    except ConnectionError as e:
        print(f"\nConnection error: {e}")
    except DatabaseError as e:
        print(f"\nDatabase error: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        if "db" in locals():
            db.close()
        print("\nDemo completed.")


if __name__ == "__main__":
    main()
