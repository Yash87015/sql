import streamlit as st
import pandas as pd
import sqlite3 as sql
import os
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
warnings.filterwarnings('ignore')

# --- SQL Queries Dictionary ---
QUERIES = {
    'competitions_with_categories': """
SELECT c.name AS competition_name, cat.category_name
FROM competitions c
JOIN categories cat ON c.category_id = cat.category_id;
""",
    'count_competitions_by_category': """
SELECT cat.category_name, COUNT(c.id) AS competition_count
FROM competitions c
JOIN categories cat ON c.category_id = cat.category_id
GROUP BY cat.category_name
ORDER BY competition_count DESC;
""",
    'doubles_competitions': """
SELECT id, name, type, gender, category_id, level
FROM competitions
WHERE type = 'doubles';
""",
    'itf_men_competitions': """
SELECT c.id, c.name, c.type, c.gender, cat.category_name, c.level
FROM competitions c
JOIN categories cat ON c.category_id = cat.category_id
WHERE cat.category_name = 'ITF Men';
""",
    'parent_sub_competitions': """
SELECT
    comp.name AS Sub_category,
    comp.type AS Type,
    comp.gender AS Gender,
    cat.category_name AS Category,
    comp.parent_id AS Parent_ID
FROM
    competitions comp
JOIN
    categories cat ON comp.category_id = cat.category_id
WHERE
    comp.parent_id IS NOT NULL
    AND comp.parent_id != '';
""",
    'competition_type_by_category_distribution': """
SELECT
    cat.category_name AS Category,
    comp.type AS Competition_Type,
    COUNT(*) AS Total_Count
FROM
    competitions comp
JOIN
    categories cat ON comp.category_id = cat.category_id
GROUP BY
    cat.category_name,
    comp.type
ORDER BY
    cat.category_name ASC,
    Total_Count DESC;
""",
    'top_level_competitions': """
SELECT
    comp.id AS Competition_ID,
    comp.name AS Competition_Name,
    cat.category_name AS Category
FROM
    competitions comp
LEFT JOIN
    categories cat ON comp.category_id = cat.category_id
WHERE
    comp.parent_id IS NULL
    OR comp.parent_id = '';
""",
    'count_null_parent_id': """
SELECT
    COUNT(*) AS Null_Count
FROM competitions
where Parent_ID is null;
""",
    'venues_with_complex_name': """
SELECT
    v.venue_name,
    c.complex_name
FROM
    venues v
JOIN
    complexes c ON v.complex_id = c.complex_id;
""",
    'venue_count_by_complex': """
SELECT
    c.complex_name,
    COUNT(v.venue_id) AS Venue_Count
FROM
    complexes c
LEFT JOIN
    venues v ON c.complex_id = v.complex_id
GROUP BY
    c.complex_id;
""",
    'venue_count_by_complex_desc': """
SELECT
    c.complex_name,
    COUNT(v.venue_id) AS Venue_Count
FROM
    complexes c
LEFT JOIN
    venues v ON c.complex_id = v.complex_id
GROUP BY
    c.complex_id
ORDER BY
    Venue_Count DESC;
""",
    'venues_in_chile': """
select venue_name, country, city, timezone from venues where country = 'CHILE';
""",
    'venues_timezones': """
SELECT distinct
    venue_name,
    timezone
FROM
    venues;
""",
    'complex_more_than_one_venue': """
SELECT
complex_name,
    COUNT(venue_id) AS venue_count
FROM
    venues
GROUP BY
    complex_name
HAVING
    COUNT(venue_id) > 1
ORDER BY
    venue_count DESC;
""",
    'venues_grouped_by_country': """
SELECT
    country,
    COUNT(venue_name) AS venue_count
FROM
    venues
GROUP BY
    country
ORDER BY
    venue_count DESC;
""",
    'venues_for_nacional_complex': """
SELECT
    v.venue_name,
    v.city,
    v.timezone
FROM
    venues v
JOIN
    complexes c ON v.complex_id = c.complex_id
WHERE
    c.complex_name = 'Nacional';
""",
    'competitors_rank_points': """
SELECT
    c.competitor_name,
    r.rank,
    r.points
FROM
    competitors c
JOIN
    competitor_rankings r ON c.competitor_id = r.competitor_id;
""",
    'top_5_competitors': """
SELECT
    c.competitor_name,
    r.rank,
    r.points
FROM
    competitors c
JOIN
    competitor_rankings r ON c.competitor_id = r.competitor_id
    AND r.rank <= 5;
""",
    'stable_rank_competitors': """
select
    c.competitor_name,
    r.rank,
    r.points,
    r.movement
FROM
    competitors c
JOIN
    competitor_rankings r ON c.competitor_id = r.competitor_id
WHERE
    r.movement = 0;
""",
    'total_points_by_country': """
SELECT
     SUM(r.points) AS total_points
FROM
    competitors c
JOIN
    competitor_rankings r ON c.competitor_id = r.competitor_id
WHERE
    c.country = ?;
""",
    'competitors_per_country': """
SELECT
    country,
    COUNT(competitor_id) AS competitor_count
FROM
    competitors
GROUP BY
    country
ORDER BY
    competitor_count DESC;
""",
    'highest_points_current_week': """
SELECT
    c.competitor_name,
    r.points
FROM
    competitors c
JOIN
    competitor_rankings r ON c.competitor_id = r.competitor_id
    AND r.week = (SELECT MAX(week) FROM competitor_rankings)
ORDER BY
    r.points DESC;
""",
}

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Tennish DB Analysis", layout="wide")
st.title("🎾 Tennish Database Analysis 🎾")

# --- Cached Database Connection ---
@st.cache_resource
def get_db_connection():
    logging.info("Attempting to connect to tennish.db...")
    try:
        conn = sql.connect('tennish.db')
        logging.info("Successfully connected to tennish.db.")
        return conn
    except sql.Error as e:
        logging.error(f"Database connection error: {e}")
        st.error(f"Error connecting to database: {e}")
        return None

# --- Cached Data Loading Function ---
@st.cache_data(ttl=3600) # Cache data for 1 hour
def load_data(query, conn, params=None):
    if conn is None:
        return pd.DataFrame() # Return empty DataFrame if no connection
    logging.info(f"Loading data with query: {query}")
    try:
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        logging.info("Data loaded successfully.")
        return df
    except pd.io.sql.DatabaseError as e:
        logging.error(f"Error executing SQL query: {e}")
        st.error(f"Error executing SQL query: {e}")
        return pd.DataFrame()



