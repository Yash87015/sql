-- ================================================
-- SQL Commands and Their Uses
-- ================================================

-- 1. SELECT
-- Purpose: Retrieves data from a database table.
-- Example:
SELECT Name, Population
FROM country;

-- 2. INSERT
-- Purpose: Inserts new records into a table.
-- Example:
INSERT INTO country (Name, Continent, Population)
VALUES ('New Country', 'Europe', 5000000);

-- 3. UPDATE
-- Purpose: Modifies existing records in a table.
-- Example:
UPDATE country
SET Population = 6000000
WHERE Name = 'New Country';

-- 4. DELETE
-- Purpose: Deletes records from a table.
-- Example:
DELETE FROM country
WHERE Name = 'New Country';

-- 5. WHERE
-- Purpose: Filters records based on specified conditions.
-- Example:
SELECT Name, Population
FROM country
WHERE Population > 10000000;

-- 6. ORDER BY
-- Purpose: Sorts the results of a query in ascending or descending order.
-- Example:
SELECT Name, Population
FROM country
ORDER BY Population DESC;

-- 7. LIMIT
-- Purpose: Limits the number of rows returned by a query.
-- Example:
SELECT Name, Population
FROM country
ORDER BY Population DESC
LIMIT 5;

-- 8. GROUP BY
-- Purpose: Groups records that have the same values in specified columns, often used with aggregate functions.
-- Example:
SELECT continent, SUM(Population)
FROM country
GROUP BY continent;

-- 9. HAVING
-- Purpose: Filters the results of aggregated data (works with GROUP BY).
-- Example:
SELECT continent, SUM(Population)
FROM country
GROUP BY continent
HAVING SUM(Population) > 100000000;

-- 10. JOIN
-- Purpose: Combines rows from two or more tables based on related columns.
-- INNER JOIN: Returns matching records from both tables.
-- Example:
SELECT c.Name AS Country, ci.Name AS Capital
FROM country c
INNER JOIN city ci ON c.Capital = ci.ID;

-- LEFT JOIN (LEFT OUTER JOIN): Returns all records from the left table, and matched records from the right table. If no match, NULL values are returned for right table columns.
-- Example:
SELECT c.Name AS Country, ci.Name AS Capital
FROM country c
LEFT JOIN city ci ON c.Capital = ci.ID;

-- 11. ALTER TABLE
-- Purpose: Modifies an existing table, such as adding, deleting, or modifying columns.
-- Example: Add a new column 'Region' to the 'country' table.
ALTER TABLE country
ADD Region VARCHAR(255);

-- 12. DROP TABLE
-- Purpose: Deletes a table and its data.
-- Example:
DROP TABLE country;

-- 13. CREATE TABLE
-- Purpose: Creates a new table in the database.
-- Example:
CREATE TABLE city (
    ID INT PRIMARY KEY,
    Name VARCHAR(255),
    Population INT
);

-- 14. DISTINCT
-- Purpose: Removes duplicate rows from the result set.
-- Example:
SELECT DISTINCT continent
FROM country;

-- 15. LIKE
-- Purpose: Search for a specified pattern in a column.
-- Example:
SELECT Name
FROM country
WHERE Name LIKE 'A%';

-- 16. IN
-- Purpose: Checks whether a value is within a set of values.
-- Example:
SELECT Name
FROM country
WHERE continent IN ('Europe', 'Asia');

-- 17. BETWEEN
-- Purpose: Filters records within a specific range.
-- Example:
SELECT Name, Population
FROM country
WHERE Population BETWEEN 10000000 AND 100000000;

-- 18. UNION
-- Purpose: Combines the results of two or more SELECT statements (removes duplicates).
-- Example:
SELECT Name
FROM country
UNION
SELECT Name
FROM city;

-- 19. EXISTS
-- Purpose: Checks whether a subquery returns any results.
-- Example:
SELECT Name
FROM country
WHERE EXISTS (SELECT 1 FROM city WHERE city.CountryCode = country.Code);

-- 20. CASE
-- Purpose: Provides conditional logic within a query.
-- Example:
SELECT Name,
       CASE
           WHEN Population > 100000000 THEN 'Large'
           WHEN Population > 50000000 THEN 'Medium'
           ELSE 'Small'
       END AS Population_Size
FROM country;

-- 21. NULL
-- Purpose: Represents missing or unknown data.
-- IS NULL: Checks for NULL values.
-- Example:
SELECT Name
FROM country
WHERE Population IS NULL;

-- IS NOT NULL: Checks for non-NULL values.
-- Example:
SELECT Name
FROM country
WHERE Population IS NOT NULL;

-- 22. INDEX
-- Purpose: Creates an index on a table to speed up retrieval of data.
-- Example:
CREATE INDEX idx_country_name
ON country (Name);

-- 23. TRANSACTION
-- Purpose: Allows multiple SQL operations to be executed as a single unit of work (commit or rollback).
-- Example:
BEGIN TRANSACTION;

UPDATE country
SET Population = 6000000
WHERE Name = 'New Country';

COMMIT; -- or ROLLBACK;

