-- 1. ROW_NUMBER() Example: Assign a unique number to each film ordered by release year
SELECT 
    title, 
    release_year, 
    ROW_NUMBER() OVER (ORDER BY release_year DESC) AS row_num
FROM 
    film
ORDER BY 
    release_year DESC;

-- 2. RANK() Example: Rank films by their rental rate
SELECT 
    title, 
    rental_rate,
    RANK() OVER (ORDER BY rental_rate DESC) AS rank
FROM 
    film
ORDER BY 
    rental_rate DESC;

-- 3. DENSE_RANK() Example: Dense rank films by rental rate
SELECT 
    title, 
    rental_rate,
    DENSE_RANK() OVER (ORDER BY rental_rate DESC) AS dense_rank
FROM 
    film
ORDER BY 
    rental_rate DESC;

-- 4. NTILE() Example: Divide films into 4 quartiles based on rental rate
SELECT 
    title, 
    rental_rate, 
    NTILE(4) OVER (ORDER BY rental_rate DESC) AS quartile
FROM 
    film
ORDER BY 
    rental_rate DESC;

-- 5. LAG() Example: Get the rental rate of the previous film
SELECT 
    title, 
    release_year,
    rental_rate,
    LAG(rental_rate) OVER (ORDER BY release_year) AS previous_rental_rate
FROM 
    film
ORDER BY 
    release_year;

-- 6. LEAD() Example: Get the rental rate of the next film
SELECT 
    title, 
    release_year,
    rental_rate,
    LEAD(rental_rate) OVER (ORDER BY release_year) AS next_rental_rate
FROM 
    film
ORDER BY 
    release_year;

-- 7. FIRST_VALUE() Example: Get the first rental rate for each film category
SELECT 
    title, 
    category_id,
    rental_rate,
    FIRST_VALUE(rental_rate) OVER (PARTITION BY category_id ORDER BY rental_rate DESC) AS first_rental_rate_in_category
FROM 
    film
ORDER BY 
    category_id, rental_rate DESC;

-- 8. LAST_VALUE() Example: Get the last rental rate for each film category
SELECT 
    title, 
    category_id,
    rental_rate,
    LAST_VALUE(rental_rate) OVER (PARTITION BY category_id ORDER BY rental_rate DESC 
                                  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_rental_rate_in_category
FROM 
    film
ORDER BY 
    category_id, rental_rate DESC;

-- 9. SUM() Example: Calculate the total rental income for each customer
SELECT 
    c.first_name, 
    c.last_name, 
    SUM(p.amount) OVER (PARTITION BY c.customer_id) AS total_spent
FROM 
    customer c
JOIN 
    payment p ON c.customer_id = p.customer_id
GROUP BY 
    c.customer_id;

-- 10. AVG() Example: Calculate the average rental rate for each category
SELECT 
    category_id, 
    AVG(rental_rate) OVER (PARTITION BY category_id) AS avg_rental_rate
FROM 
    film
ORDER BY 
    category_id;

-- 11. COUNT() Example: Count the number of rentals for each customer
SELECT 
    c.first_name, 
    c.last_name, 
    COUNT(*) OVER (PARTITION BY c.customer_id) AS rental_count
FROM 
    customer c
JOIN 
    rental r ON c.customer_id = r.customer_id
ORDER BY 
    c.customer_id;

-- 12. PERCENT_RANK() Example: Calculate the percentile rank of each rental rate
SELECT 
    title, 
    rental_rate, 
    PERCENT_RANK() OVER (ORDER BY rental_rate DESC) AS percentile_rank
FROM 
    film
ORDER BY 
    rental_rate DESC;
