-- Numeric Functions and Their Uses in SQL

-- ABS()
-- Returns the absolute value of a number.
-- Example:
SELECT ABS(-5);  -- Returns 5

-- CEIL() or CEILING()
-- Returns the smallest integer greater than or equal to the specified number.
-- Example:
SELECT CEIL(4.9);  -- Returns 5

-- FLOOR()
-- Returns the largest integer less than or equal to the specified number.
-- Example:
SELECT FLOOR(4.9);  -- Returns 4

-- ROUND()
-- Rounds a numeric field to the number of decimal places specified.
-- Example:
SELECT ROUND(123.456, 2);  -- Returns 123.46

-- TRUNCATE()
-- Removes the decimal portion of a number (without rounding).
-- Example:
SELECT TRUNCATE(123.456, 2);  -- Returns 123.45

-- MOD()
-- Returns the remainder of a division operation.
-- Example:
SELECT MOD(10, 3);  -- Returns 1

-- POW() or POWER()
-- Returns the result of the first number raised to the power of the second number.
-- Example:
SELECT POW(2, 3);  -- Returns 8

-- SQRT()
-- Returns the square root of a number.
-- Example:
SELECT SQRT(16);  -- Returns 4

-- EXP()
-- Returns the exponential value of a number (e raised to the power of a specified number).
-- Example:
SELECT EXP(2);  -- Returns 7.389056 (e^2)

-- LOG() or LN()
-- Returns the natural logarithm (base e) of a number.
-- Example:
SELECT LOG(10);  -- Returns 2.302585 (logarithm of 10 to base e)

-- LOG10()
-- Returns the logarithm of a number with base 10.
-- Example:
SELECT LOG10(100);  -- Returns 2 (logarithm of 100 to base 10)

-- RAND()
-- Returns a random floating-point number between 0 and 1.
-- Example:
SELECT RAND();  -- Returns a random number between 0 and 1

-- SIGN()
-- Returns the sign of a number (1 for positive, -1 for negative, 0 for zero).
-- Example:
SELECT SIGN(-7);  -- Returns -1

-- PI()
-- Returns the value of pi (π).
-- Example:
SELECT PI();  -- Returns 3.141593

-- GREATEST()
-- Returns the largest value from a list of numbers.
-- Example:
SELECT GREATEST(3, 7, 2, 8) as largedt_value_of_list;  -- Returns 8

-- LEAST()
-- Returns the smallest value from a list of numbers.
-- Example:
SELECT LEAST(3, 7, 2, 8) as least_value_of_list;  -- Returns 2

-- CONV()
-- Converts a number from one base to another (e.g., binary to decimal).
-- Example:
SELECT CONV(1010, 2, 10);  -- Converts 1010 from binary to decimal, returns 10

-- BIN()
-- Converts a number to its binary representation.
-- Example:
SELECT BIN(10);  -- Returns '1010'

-- OCT()
-- Converts a number to its octal representation.
-- Example:
SELECT OCT(10);  -- Returns '12'

-- HEX()
-- Converts a number to its hexadecimal representation.
-- Example:
SELECT HEX(10);  -- Returns 'A'

#-- 1. Single-Row Subquery (Using Comparison Operators)
-- Retrieve cities where population is greater than the average population of all cities
SELECT name
FROM city
WHERE population > (SELECT AVG(population) FROM city);

-- 2. Multi-Row Subquery (Using IN)
-- Retrieve cities where the country is located in 'Asia' or 'Europe'
SELECT name
FROM city
WHERE countrycode IN (SELECT code FROM country WHERE continent IN ('Asia', 'Europe'));

-- 3. Multi-Column Subquery (Using IN with Multiple Columns)
-- Retrieve cities where the city’s population and district match the ones in the subquery
SELECT name, population, district
FROM city
WHERE (population, district) IN (SELECT population, district FROM city WHERE countrycode = 'USA');

-- 4. Correlated Subquery
-- Retrieve cities where the population is greater than the average population in their respective country
SELECT name, population, countrycode
FROM city c
WHERE population > (SELECT AVG(population) FROM city WHERE countrycode = c.countrycode);

-- 5. Scalar Subquery
-- Retrieve all cities and the largest population in the world
SELECT name, (SELECT MAX(population) FROM city) AS max_population
FROM city;

-- 6. EXISTS Subquery
-- Retrieve cities where there exists a country in the 'Asia' continent
SELECT name
FROM city c
WHERE EXISTS (SELECT 1 FROM country WHERE continent = 'Asia' AND code = c.countrycode);
#The subquery checks whether a country in Asia exists for each city, and if true,
#the outer query returns the cities where the condition is met.
#EXISTS: The EXISTS keyword is used to check if a subquery returns any rows. It returns a boolean value (TRUE or FALSE):

-- 7. ANY Subquery
-- Retrieve cities with population greater than the population of any city in the country with code 'USA'
SELECT name, population
FROM city
WHERE population > ANY (SELECT population FROM city WHERE countrycode = 'USA');

-- 8. ALL Subquery
-- Retrieve cities with population greater than the population of all cities in the country with code 'USA'
SELECT name, population
FROM city
WHERE population > ALL (SELECT population FROM city WHERE countrycode = 'USA');

-- 9. Non-Correlated Subquery
-- Retrieve cities where the country code is the same as the one in the 'Canada' country record
SELECT name
FROM city
WHERE countrycode = (SELECT code FROM country WHERE name = 'Canada');


