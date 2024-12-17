-- Example SQL file for Date/Time functions using Sakila database

-- 1. Get the current date
SELECT CURDATE() AS current_date;

-- 2. Get the current date and time
SELECT NOW() AS current_datetime;

-- 3. Get only the date part from the current date and time
SELECT DATE(NOW()) AS current_date;

-- 4. Extract Year, Month, and Day from the current date
SELECT 
  YEAR(NOW()) AS current_year,
  MONTH(NOW()) AS current_month,
  DAY(NOW()) AS current_day;

-- 5. Add 7 days to the current date and subtract 7 days from the current date
SELECT 
  DATE_ADD(CURDATE(), INTERVAL 7 DAY) AS date_plus_7_days,
  DATE_SUB(CURDATE(), INTERVAL 7 DAY) AS date_minus_7_days;

-- 6. Calculate the number of days since a specific date (e.g., '2005-05-25')
SELECT 
  DATEDIFF(NOW(), '2005-05-25') AS days_since_release;

-- 7. Format the current date in 'YYYY-MM-DD' and 'Weekday, Month Day, Year' format
SELECT 
  DATE_FORMAT(NOW(), '%Y-%m-%d') AS formatted_date,
  DATE_FORMAT(NOW(), '%W, %M %d, %Y') AS custom_format;

-- 8. Calculate the difference in years between two dates (e.g., '2005-05-25' and NOW)
SELECT 
  TIMESTAMPDIFF(YEAR, '2005-05-25', NOW()) AS years_difference;

-- 9. Get the last day of the current month
SELECT 
  LAST_DAY(NOW()) AS last_day_of_current_month;

-- 10. Count the number of rentals in the last 30 days from the rental table
SELECT COUNT(*) AS rentals_in_last_30_days
FROM rental
WHERE rental_date >= DATE_SUB(NOW(), INTERVAL 30 DAY);

-- 11. Get films released in the year 2005 from the film table
SELECT title, release_year
FROM film
WHERE release_year = 2006;

-- 12. Calculate the number of days between the rental date and return date in the rental table
SELECT rental_id, DATEDIFF(return_date, rental_date) AS days_rented
FROM rental
WHERE return_date IS NOT NULL;

-- 13. Get the most recent payment date from the payment table
SELECT MAX(payment_date) AS most_recent_payment
FROM payment;

-- 14. Find customers who rented films on a specific date (e.g., '2024-12-15')
SELECT customer_id, COUNT(*) AS rentals_on_specific_date
FROM rental
WHERE rental_date =  '2005-05-25 04:47:44'

GROUP BY customer_id;

-- 15. Find the month with the most rentals in the past year
SELECT 
  MONTH(rental_date) AS rental_month,
  COUNT(*) AS rental_count
FROM rental
WHERE rental_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND CURDATE()
GROUP BY rental_month
ORDER BY rental_count DESC
LIMIT 1;
