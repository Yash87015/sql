-- ================================================
-- SQL String Functions with Examples in Sakila Database
-- ================================================

-- 1. LENGTH()
-- Purpose: Returns the length of a string (the number of characters in the string).  
-- Example:
SELECT first_name, LENGTH(first_name) AS first_name_length
FROM customer
ORDER BY first_name_length desc
LIMIT 10;

-- 2. CONCAT()
-- Purpose: Concatenates (joins) two or more strings into one.  
-- Example:
SELECT CONCAT(first_name, ' ', last_name) AS full_name
FROM customer
LIMIT 5;

-- 3. LOWER()
-- Purpose: Converts all characters in a string to lowercase.  
-- Example:
SELECT first_name, LOWER(first_name) AS lower_first_name
FROM customer
LIMIT 5;

-- 4. UPPER()
-- Purpose: Converts all characters in a string to uppercase.  
-- Example:
SELECT first_name, UPPER(first_name) AS upper_first_name
FROM customer
LIMIT 5;

-- 5. SUBSTRING()
-- Purpose: Extracts a substring from a string, starting from a specified position and for a specified length.  
-- Example:
SELECT first_name, SUBSTRING(first_name, 1, 3) AS first_three_letters
FROM customer
LIMIT 5;

-- 6. REPLACE()
-- Purpose: Replaces all occurrences of a substring within a string with another substring.  
-- Example:
SELECT title, REPLACE(title, ' ', '_') AS title_with_underscores
FROM film
LIMIT 5;

-- 7. TRIM()
-- Purpose: Removes leading and trailing spaces from a string.  
-- Example:
SELECT first_name, TRIM(first_name) AS trimmed_first_name
FROM customer
LIMIT 5;

-- 8. LEFT()
-- Purpose: Extracts a specified number of characters from the left side of a string.  
-- Example:
SELECT first_name, LEFT(first_name, 2) AS first_two_letters
FROM customer
LIMIT 5;

-- 9. RIGHT()
-- Purpose: Extracts a specified number of characters from the right side of a string.  
-- Example:
SELECT first_name, RIGHT(first_name, 2) AS last_two_letters
FROM customer
LIMIT 5;

-- 10. INSTR()
-- Purpose: Returns the position of the first occurrence of a substring within a string.  
-- Example:
SELECT first_name, INSTR(first_name, 'a') AS position_of_a
FROM customer
LIMIT 5;

-- 11. REVERSE()
-- Purpose: Reverses the characters in a string.  
-- Example:
SELECT first_name, REVERSE(first_name) AS reversed_first_name
FROM customer
LIMIT 5;

-- 12. LIKE
-- Purpose: Matches a string against a pattern. (Can use wildcards like '%' for any sequence of characters or '_' for a single character)  
-- Example:
SELECT first_name, last_name
FROM customer
WHERE first_name LIKE 'A%';

-- 13. LOCATE()
-- Purpose: Similar to INSTR(), returns the position of the first occurrence of a substring within a string.  
-- Example:
SELECT first_name, LOCATE('a', first_name) AS position_of_a
FROM customer
LIMIT 5;

-- 14. CONCAT_WS()
-- Purpose: Concatenates strings with a separator.  
-- Example:
SELECT CONCAT_WS('-', first_name, last_name) AS full_name_with_dash
FROM customer
LIMIT 5;

-- 15. CHAR_LENGTH()
-- Purpose: Returns the length of the string, counting characters instead of bytes (useful for multi-byte characters).  
-- Example:
SELECT first_name, CHAR_LENGTH(first_name) AS char_length
FROM customer
LIMIT 5;

-- 16. LPAD()
-- Purpose: Pads the left side of a string with a specified character up to a certain length.  
-- Example:
SELECT first_name, LPAD(first_name, 10, '*') AS padded_first_name
FROM customer
LIMIT 5;

-- 17. RPAD()
-- Purpose: Pads the right side of a string with a specified character up to a certain length.  
-- Example:
SELECT first_name, RPAD(first_name, 10, '*') AS padded_first_name
FROM customer
LIMIT 5;

-- 18. SOUNDEX()
-- Purpose: Returns a four-character code that is based on the pronunciation of a string (useful for finding similar-sounding names).  
-- Example:
SELECT first_name, SOUNDEX(first_name) AS soundex_code
FROM customer
LIMIT 5;

-- 19. SPACE()
-- Purpose: Returns a string with a specified number of spaces.  
-- Example:
SELECT first_name, SPACE(5) AS five_spaces
FROM customer
LIMIT 5;

