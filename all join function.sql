-- ***********************************************************************
-- 1. INNER JOIN
-- Description: The INNER JOIN returns only the rows with matching values in both tables.
-- Use Case: Use when you need only the rows where a match exists in both tables.
-- ***********************************************************************

SELECT City.Name AS CityName, Country.Name AS CountryName
FROM City
INNER JOIN Country ON City.CountryCode = Country.Code;

-- ***********************************************************************
-- 2. LEFT JOIN (LEFT OUTER JOIN)
-- Description: The LEFT JOIN returns all rows from the left table and matching rows from the right table.
-- If no match is found, NULL is returned for the columns from the right table.
-- Use Case: Use when you need all records from the left table, even if there is no match in the right table.
-- ***********************************************************************

SELECT Country.Name AS CountryName, City.Name AS CapitalCity
FROM Country
LEFT JOIN City ON Country.Capital = City.ID;

-- ***********************************************************************
-- 3. RIGHT JOIN (RIGHT OUTER JOIN)
-- Description: The RIGHT JOIN returns all rows from the right table and matching rows from the left table.
-- If no match is found, NULL is returned for the columns from the left table.
-- Use Case: Use when you need all records from the right table, even if there is no match in the left table.
-- ***********************************************************************

SELECT City.Name AS CityName, Country.Name AS CountryName
FROM City
RIGHT JOIN Country ON City.CountryCode = Country.Code;

-- ***********************************************************************
-- 4. FULL JOIN (FULL OUTER JOIN)
-- Description: The FULL JOIN returns all rows when there is a match in one of the tables.
-- If no match is found in one table, NULL is returned for that table’s columns.
-- Use Case: Use when you need all records from both tables, even if no match is found.
-- ***********************************************************************

SELECT Country.Name AS CountryName, City.Name AS CityName
FROM Country
FULL JOIN City ON Country.Code = City.CountryCode;

-- ***********************************************************************
-- 5. CROSS JOIN
-- Description: The CROSS JOIN returns the Cartesian product of two tables. Every combination of rows from both tables is returned.
-- Use Case: Use when you need every possible combination of records between two tables.
-- ***********************************************************************

SELECT Country.Name AS CountryName, City.Name AS CityName
FROM Country
CROSS JOIN City;

-- ***********************************************************************
-- 6. SELF JOIN
-- Description: A SELF JOIN joins a table with itself. It is useful for hierarchical data or comparing rows within the same table.
-- Use Case: Use when you need to compare rows within the same table, such as finding pairs of cities within the same country.
-- ***********************************************************************

SELECT A.Name AS City1, B.Name AS City2
FROM City A, City B
WHERE A.CountryCode = B.CountryCode AND A.ID != B.ID;

-- ***********************************************************************
-- END OF JOIN DEMONSTRATIONS
-- ***********************************************************************
