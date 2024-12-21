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
                DATABASE_NAME="AdventureWorks2019",
            )
            .connect_to_database()
        ) as conn:
            print("\nExecuting queries...")

            # Version check
            print("\n1. SQL Server Version:")
            conn.execute_query_to_prettytable("SELECT @@VERSION as Version", print_result=True)

            # Product query
            print("\n2. group by rollup(d.Name, E.JobTitle):")
            conn.execute_query_to_prettytable(
                """
                    select d.Name,
                        case
                            when grouping_id(d.Name, E.JobTitle) = 0 then
                                E.JobTitle
                            when grouping_id(d.Name, E.JobTitle) = 1 then
                                'Sub-Total: ' + d.Name
                            when grouping_id(d.Name, E.JobTitle) = 3 then
                                N'Company Total:'
                            else
                                'Unknown'
                        end as [Job Title],
                        count(E.BusinessEntityID) as [Employee Count]
                    from HumanResources.Employee E
                        inner join HumanResources.EmployeeDepartmentHistory as dh
                            on E.BusinessEntityID = dh.BusinessEntityID
                        inner join HumanResources.Department as d
                            on d.DepartmentID = dh.DepartmentID
                    where dh.EndDate is null
                        and d.DepartmentID in ( 12, 14 )
                    group by rollup(d.Name, E.JobTitle);
                """,
                print_result=True,
            )

            # Product query
            print("\n3. Complex usage of GROUP BY GROUPING SETS and GROUPING_ID:")
            conn.execute_query_to_prettytable(
                """
                DECLARE @Grouping NVARCHAR(50);
                DECLARE @GroupingLevel SMALLINT;

                SET @Grouping = N'CountryRegionCode Total';

                SELECT @GroupingLevel = (
                    CASE @Grouping
                        WHEN N'Grand Total' THEN 15
                        WHEN N'SalesPerson Total' THEN 14
                        WHEN N'Store Total' THEN 13
                        WHEN N'Store SalesPerson Total' THEN 12
                        WHEN N'CountryRegionCode Total' THEN 11
                        WHEN N'Group Total' THEN 7
                        ELSE N'Unknown'
                    END
                );

                SELECT T.[Group],
                    T.CountryRegionCode,
                    S.Name AS N'Store',
                    (
                        SELECT P.FirstName + ' ' + P.LastName
                        FROM Person.Person AS P
                        WHERE P.BusinessEntityID = H.SalesPersonID
                    ) AS N'Sales Person',
                    SUM(TotalDue) AS N'TotalSold',
                    CAST(GROUPING(T.[Group]) AS CHAR(1)) + CAST(GROUPING(T.CountryRegionCode) AS CHAR(1)) + CAST(GROUPING(S.Name) AS CHAR(1)) + CAST(GROUPING(H.SalesPersonID) AS CHAR(1)) AS N'GROUPING base-2',
                    GROUPING_ID((T.[Group]), (T.CountryRegionCode), (S.Name), (H.SalesPersonID)) AS N'GROUPING_ID',
                    CASE 
                        WHEN GROUPING_ID((T.[Group]), (T.CountryRegionCode), (S.Name), (H.SalesPersonID)) = 15
                            THEN N'Grand Total'
                        WHEN GROUPING_ID((T.[Group]), (T.CountryRegionCode), (S.Name), (H.SalesPersonID)) = 14
                            THEN N'SalesPerson Total'
                        WHEN GROUPING_ID((T.[Group]), (T.CountryRegionCode), (S.Name), (H.SalesPersonID)) = 13
                            THEN N'Store Total'
                        WHEN GROUPING_ID((T.[Group]), (T.CountryRegionCode), (S.Name), (H.SalesPersonID)) = 12
                            THEN N'Store SalesPerson Total'
                        WHEN GROUPING_ID((T.[Group]), (T.CountryRegionCode), (S.Name), (H.SalesPersonID)) = 11
                            THEN N'CountryRegionCode Total'
                        WHEN GROUPING_ID((T.[Group]), (T.CountryRegionCode), (S.Name), (H.SalesPersonID)) = 7
                            THEN N'Group Total'
                        ELSE N'Error'
                    END AS N'Level'
                FROM Sales.Customer AS C
                INNER JOIN Sales.Store AS S
                    ON C.StoreID = S.BusinessEntityID
                INNER JOIN Sales.SalesTerritory AS T
                    ON C.TerritoryID = T.TerritoryID
                INNER JOIN Sales.SalesOrderHeader AS H
                    ON C.CustomerID = H.CustomerID
                GROUP BY GROUPING SETS(
                    (S.Name,H.SalesPersonID),
                    (H.SalesPersonID), 
                    (S.Name), 
                    (T.[Group]),
                    (T.CountryRegionCode),
                    ()
                )
                HAVING GROUPING_ID(
                    (T.[Group]),
                    (T.CountryRegionCode),
                    (S.Name),
                    (H.SalesPersonID)
                ) = @GroupingLevel
                ORDER BY
                    GROUPING_ID(S.Name, H.SalesPersonID),
                    GROUPING_ID(
                        (T.[Group]),
                        (T.CountryRegionCode),
                        (S.Name),
                        (H.SalesPersonID)
                    ) ASC;
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
