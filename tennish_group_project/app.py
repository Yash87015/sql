import streamlit as st
import pandas as pd
import sqlite3 as sql
import os
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# --- SQL Queries Embedded ---
QUERIES = {
    "query_competitions_categories": """
        SELECT c.name AS competition_name, cat.category_name
        FROM competitions c
        JOIN categories cat ON c.category_id = cat.category_id;
    """,
    "query_count_by_category": """
        SELECT cat.category_name, COUNT(c.id) AS competition_count
        FROM competitions c
        JOIN categories cat ON c.category_id = cat.category_id
        GROUP BY cat.category_name
        ORDER BY competition_count DESC;
    """,
    "query_doubles_competitions": """
        SELECT id, name, type, gender, category_id, level
        FROM competitions
        WHERE type = 'doubles';
    """,
    "query_itf_men_competitions": """
        SELECT c.id, c.name, c.type, c.gender, cat.category_name, c.level
        FROM competitions c
        JOIN categories cat ON c.category_id = cat.category_id
        WHERE cat.category_name = 'ITF Men';
    """,
    "query_parent_sub_competitions": """
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
    "query_competition_types_by_category": """
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
    "query_competitions_no_parent": """
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
    "query_venues_complex_name": """
        SELECT
            v.venue_name,
            c.complex_name
        FROM
            venues v
        JOIN
            complexes c ON v.complex_id = c.complex_id;
    """,
    "query_venue_count_by_complex": """
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
    "query_venues_in_chile": """
        SELECT venue_name, country, city, timezone
        FROM venues
        WHERE country = '{selected_country}';
    """, # Placeholder for dynamic country
    "query_all_venues_timezones": """
        SELECT DISTINCT
            venue_name,
            timezone
        FROM
            venues;
    """,
    "query_complexes_multiple_venues": """
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
    "query_venues_grouped_by_country": """
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
    "query_venues_for_nacional_complex": """
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
    "query_competitor_rank_points": """
        SELECT
            c.competitor_name,
            r.rank,
            r.points
        FROM
            competitors c
        JOIN
            competitor_rankings r ON c.competitor_id = r.competitor_id;
    """,
    "query_top_5_competitors": """
        SELECT
            c.competitor_name,
            r.rank,
            r.points
        FROM
            competitors c
        JOIN
            competitor_rankings r ON c.competitor_id = r.competitor_id
        WHERE
            r.rank <= 5
        ORDER BY r.rank ASC;
    """,
    "query_stable_rank_competitors": """
        SELECT
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
    "query_total_points_croatia": """
        SELECT
            SUM(r.points) AS total_points
        FROM
            competitors c
        JOIN
            competitor_rankings r ON c.competitor_id = r.competitor_id
        WHERE
            c.country = '{selected_country}';
    """, # Placeholder for dynamic country
    "query_competitor_count_by_country": """
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
    "query_highest_points_current_week": """
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
    """
}
st.set_page_config(layout="wide")

# Connect to the database
conn = sql.connect('tennish.db')

st.title('Food Waste Management Dashboard')

# --- Dataset Information ---
st.header('Dataset Information')

@st.cache_data
def load_data(query_str):
    if not os.path.exists(DB_PATH):
        st.error(f"Database file '{DB_PATH}' not found. Please place the SQLite database in the app directory.")
        return pd.DataFrame()
    conn = None
    try:
        # Create a fresh connection for this call to avoid SQLite "same thread" errors.
        conn = sql.connect(DB_PATH, check_same_thread=False)
        df = pd.read_sql(query_str, conn)
        return df
    except Exception as e:
        logging.exception("Failed to execute SQL query")
        st.error("Database query failed. Check that the database exists and contains the expected tables.")
        st.exception(e)
        return pd.DataFrame()
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass

# Main application logic



