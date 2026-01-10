import streamlit as st
import pandas as pd
import sqlite3 as sql
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
import logging

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
    'competitions_by_category': """
SELECT c.id, c.name, c.type, c.gender, cat.category_name, c.level
FROM competitions c
JOIN categories cat ON c.category_id = cat.category_id
WHERE cat.category_name = ?;
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
    'venues_by_country': """
SELECT venue_name, country, city, timezone FROM venues WHERE country = ?;
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
    'venues_by_complex_name': """
SELECT
    v.venue_name,
    v.city,
    v.timezone
FROM
    venues v
JOIN
    complexes c ON v.complex_id = c.complex_id
WHERE
    c.complex_name = ?;
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

# --- Cached Database Connection --- (Modified)
# Removed @st.cache_resource as it caches the connection object which is not thread-safe.
# Now, get_db_connection will provide a new connection on each call (or rely on load_data's internal caching).
def get_db_connection():
    logging.info("Attempting to get a database connection...")
    try:
        # Ensure thread-safety for SQLite connections in a multi-threaded environment like Streamlit
        conn = sql.connect('tennish.db', check_same_thread=False)
        logging.info("Database connection obtained.")
        return conn
    except sql.Error as e:
        logging.error(f"Database connection error: {e}")
        st.error(f"Error connecting to database: {e}")
        return None

# --- Cached Data Loading Function --- (Modified)
@st.cache_data(ttl=3600) # Cache data for 1 hour
def load_data(query, params=None):
    conn = None # Initialize conn to None
    try:
        conn = get_db_connection()
        if conn is None:
            return pd.DataFrame() # Return empty DataFrame if no connection
        logging.info(f"Loading data with query: {query}")
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
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")

# --- Main Application Logic ---
def main():
    # --- User-friendly Query Names Mapping ---
    QUERY_NAMES = {
        'competitions_with_categories': '1. List all competitions along with their category name',
        'count_competitions_by_category': '2. Count the number of competitions in each category',
        'doubles_competitions': "3. Find all competitions of type 'doubles'",
        'competitions_by_category': "4. Get competitions that belong to a specific category",
        'parent_sub_competitions': '5. Identify parent competitions and their sub-competitions',
        'competition_type_by_category_distribution': '6. Analyze the distribution of competition types by category',
        'top_level_competitions': '7. List all competitions with no parent (top-level competitions)',
        'count_null_parent_id': '8. Count null parent_ids (Internal Check)',
        'venues_with_complex_name': '9. List all venues along with their associated complex name',
        'venue_count_by_complex': '10. Count the number of venues in each complex (Ascending)',
        'venue_count_by_complex_desc': '11. Count the number of venues in each complex (Descending)',
        'venues_by_country': "12. Get details of venues in a specific country",
        'venues_timezones': '13. Identify all venues and their timezones',
        'complex_more_than_one_venue': '14. Find complexes that have more than one venue',
        'venues_grouped_by_country': '15. List venues grouped by country',
        'venues_by_complex_name': "16. Find all venues for a specific complex",
        'competitors_rank_points': '17. Get all competitors with their rank and points',
        'top_5_competitors': '18. Find competitors ranked in the top 5',
        'stable_rank_competitors': '19. List competitors with no rank movement (stable rank)',
        'total_points_by_country': '20. Get the total points of competitors from a specific country',
        'competitors_per_country': '21. Count the number of competitors per country',
        'highest_points_current_week': '22. Find competitors with the highest points in the current week'
    }

    query_options = list(QUERY_NAMES.values())

    # conn = get_db_connection() # No longer need to cache conn here

    # if conn: # No longer check conn here, load_data will handle it
    selected_query_display_name = st.selectbox(
        'Select a query to run:',
        options=query_options
    )

    selected_query_key = next((key for key, value in QUERY_NAMES.items() if value == selected_query_display_name), None)

    if selected_query_key:
        st.subheader(f"Results for: {selected_query_display_name}")

        # --- Conditional Display Logic ---
        if selected_query_key == 'competitions_with_categories':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)

        elif selected_query_key == 'count_competitions_by_category':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='competition_count', y='category_name', data=df.head(10), ax=ax, palette='viridis')
            ax.set_title('Top 10 Categories by Competition Count')
            ax.set_xlabel('Number of Competitions')
            ax.set_ylabel('Category Name')
            st.pyplot(fig)
            plt.close(fig)

        elif selected_query_key == 'doubles_competitions':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)

        elif selected_query_key == 'competitions_by_category':
            selected_category = st.selectbox(
                'Select a Category:',
                options=all_category_names, #all_category_names is populated using load_data. Ensure all dynamic lists are loaded with the new load_data signature.
                index=all_category_names.index('ITF Men') if 'ITF Men' in all_category_names else 0
            )
            df = load_data(QUERIES[selected_query_key], params=[selected_category]) # Removed conn argument
            st.dataframe(df)

        elif selected_query_key == 'parent_sub_competitions':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)

        elif selected_query_key == 'competition_type_by_category_distribution':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)
            
            # Filter for visualization
            all_category_names_for_plot = load_data("SELECT DISTINCT category_name FROM categories ORDER BY category_name;")['category_name'].tolist() # Fetch again for local scope
            selected_category_for_plot = st.selectbox(
                'Select a Category to visualize Type Distribution:',
                options=['All'] + all_category_names_for_plot,
                index=0
            )
            if selected_category_for_plot != 'All':
                plot_df = df[df['Category'] == selected_category_for_plot]
            else:
                plot_df = df

            if not plot_df.empty:
                fig, ax = plt.subplots(figsize=(12, 7))
                sns.barplot(x='Total_Count', y='Competition_Type', hue='Category', data=plot_df.head(20), dodge=False, ax=ax, palette='coolwarm')
                ax.set_title(f'Competition Type Distribution for {selected_category_for_plot}')
                ax.set_xlabel('Total Count')
                ax.set_ylabel('Competition Type')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("No data to display for the selected category.")

        elif selected_query_key == 'top_level_competitions':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)

        elif selected_query_key == 'count_null_parent_id':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)

        elif selected_query_key == 'venues_with_complex_name':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)

        elif selected_query_key == 'venue_count_by_complex' or selected_query_key == 'venue_count_by_complex_desc':
            min_venue_count = st.number_input('Minimum number of venues in a complex:', min_value=0, value=1)
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            df_filtered = df[df['Venue_Count'] >= min_venue_count]
            st.dataframe(df_filtered)
            if not df_filtered.empty:
                fig, ax = plt.subplots(figsize=(12, 7))
                sns.barplot(x='Venue_Count', y='complex_name', data=df_filtered.head(10), ax=ax, palette='plasma')
                ax.set_title(f'Top 10 Complexes with at least {min_venue_count} Venues')
                ax.set_xlabel('Number of Venues')
                ax.set_ylabel('Complex Name')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("No complexes found matching the minimum venue count.")

        elif selected_query_key == 'venues_by_country':
            all_venue_countries_for_filter = load_data("SELECT DISTINCT country FROM venues WHERE country IS NOT NULL AND country != '' ORDER BY country;")['country'].tolist() # Fetch again for local scope
            selected_country = st.selectbox(
                'Select a Country:',
                options=all_venue_countries_for_filter,
                index=all_venue_countries_for_filter.index('CHILE') if 'CHILE' in all_venue_countries_for_filter else 0
            )
            df = load_data(QUERIES[selected_query_key], params=[selected_country]) # Removed conn argument
            st.dataframe(df)

        elif selected_query_key == 'venues_timezones':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)

        elif selected_query_key == 'complex_more_than_one_venue':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)

        elif selected_query_key == 'venues_grouped_by_country':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)
            fig, ax = plt.subplots(figsize=(12, 7))
            sns.barplot(x='venue_count', y='country', data=df.head(15), ax=ax, palette='magma')
            ax.set_title('Top 15 Countries by Venue Count')
            ax.set_xlabel('Number of Venues')
            ax.set_ylabel('Country')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        elif selected_query_key == 'venues_by_complex_name':
            all_complex_names_for_filter = load_data("SELECT DISTINCT complex_name FROM complexes WHERE complex_name IS NOT NULL AND complex_name != '' ORDER BY complex_name;")['complex_name'].tolist() # Fetch again for local scope
            selected_complex = st.selectbox(
                'Select a Complex Name:',
                options=all_complex_names_for_filter,
                index=all_complex_names_for_filter.index('Nacional') if 'Nacional' in all_complex_names_for_filter else 0
            )
            df = load_data(QUERIES[selected_query_key], params=[selected_complex]) # Removed conn argument
            st.dataframe(df)

        elif selected_query_key == 'competitors_rank_points':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)

        elif selected_query_key == 'top_5_competitors':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)

        elif selected_query_key == 'stable_rank_competitors':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)

        elif selected_query_key == 'total_points_by_country':
            all_competitor_countries_for_filter = load_data("SELECT DISTINCT country FROM competitors WHERE country IS NOT NULL AND country != '' ORDER BY country;")['country'].tolist() # Fetch again for local scope
            selected_country = st.selectbox(
                'Select a Country for Competitor Points:',
                options=all_competitor_countries_for_filter,
                index=all_competitor_countries_for_filter.index('Croatia') if 'Croatia' in all_competitor_countries_for_filter else 0
            )
            df = load_data(QUERIES[selected_query_key], params=[selected_country]) # Removed conn argument
            st.dataframe(df)

        elif selected_query_key == 'competitors_per_country':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)
            fig, ax = plt.subplots(figsize=(12, 7))
            sns.barplot(x='competitor_count', y='country', data=df.head(15), ax=ax, palette='cividis')
            ax.set_title('Top 15 Countries by Competitor Count')
            ax.set_xlabel('Number of Competitors')
            ax.set_ylabel('Country')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        elif selected_query_key == 'highest_points_current_week':
            df = load_data(QUERIES[selected_query_key]) # Removed conn argument
            st.dataframe(df)

    # else block was here, removed as load_data now handles conn errors internally

if __name__ == "__main__":
    main()
