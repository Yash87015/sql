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

# Map descriptive names to query keys
QUERY_OPTIONS = {
    "1. Competitions and their Categories": "query_competitions_categories",
    "2. Number of Competitions in Each Category": "query_count_by_category",
    "3. Doubles Competitions": "query_doubles_competitions",
    "4. ITF Men Competitions": "query_itf_men_competitions",
    "5. Parent and Sub-Competitions": "query_parent_sub_competitions",
    "6. Distribution of Competition Types by Category": "query_competition_types_by_category",
    "7. Top-Level Competitions (No Parent)": "query_competitions_no_parent",
    "8. Venues with Complex Names": "query_venues_complex_name",
    "9. Number of Venues in Each Complex": "query_venue_count_by_complex",
    "10. Venues in a Specific Country": "query_venues_in_chile",
    "11. All Venues and Their Timezones": "query_all_venues_timezones",
    "12. Complexes with Multiple Venues": "query_complexes_multiple_venues",
    "13. Venues Grouped by Country": "query_venues_grouped_by_country",
    "14. Venues for Nacional Complex": "query_venues_for_nacional_complex",
    "15. Competitors with Rank and Points": "query_competitor_rank_points",
    "16. Top 5 Competitors": "query_top_5_competitors",
    "17. Stable Rank Competitors": "query_stable_rank_competitors",
    "18. Total Points for Competitors from a Specific Country": "query_total_points_croatia",
    "19. Count Competitors per Country": "query_competitor_count_by_country",
    "20. Competitors with Highest Points in Current Week": "query_highest_points_current_week"
}

selected_option = st.selectbox(
    "Select a query to display results:",
    list(QUERY_OPTIONS.keys())
)

query_key = QUERY_OPTIONS[selected_option]

st.subheader(selected_option)

# Handle specific queries with filters or visualizations
if query_key == "query_count_by_category":
    df = load_data(QUERIES[query_key])
    st.dataframe(df)
    if not df.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='competition_count', y='category_name', data=df.head(10), ax=ax, palette='viridis')
        ax.set_title('Top 10 Categories by Competition Count')
        ax.set_xlabel('Competition Count')
        ax.set_ylabel('Category Name')
        st.pyplot(fig)
        plt.close(fig) # Close the figure to prevent display issues

elif query_key == "query_competition_types_by_category":
    df_comp_types_by_cat = load_data(QUERIES[query_key])

    categories_list = ['All Categories'] + sorted(df_comp_types_by_cat['Category'].unique().tolist())
    selected_category = st.selectbox('Filter by Category:', categories_list, key='comp_type_category_filter')

    if selected_category == 'All Categories':
        filtered_df = df_comp_types_by_cat
    else:
        filtered_df = df_comp_types_by_cat[df_comp_types_by_cat['Category'] == selected_category]
    st.dataframe(filtered_df)

    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.barplot(x='Competition_Type', y='Total_Count', data=filtered_df, ax=ax, palette='magma')
        ax.set_title(f'Distribution of Competition Types for {selected_category}')
        ax.set_xlabel('Competition Type')
        ax.set_ylabel('Total Count')
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.write("No data to display for the selected category.")

elif query_key == "query_venue_count_by_complex":
    df_venues_by_complex = load_data(QUERIES[query_key])
    st.dataframe(df_venues_by_complex)

    min_venue_count = st.number_input(
        'Minimum Venue Count for display:',
        min_value=0,
        value=1,
        step=1,
        key='min_venue_count_filter'
    )
    filtered_df = df_venues_by_complex[df_venues_by_complex['Venue_Count'] >= min_venue_count]
    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.barplot(
            x='Venue_Count',
            y='complex_name',
            data=filtered_df.head(20),
            ax=ax,
            palette='cubehelix'
        )
        ax.set_title(f'Top Complexes by Venue Count (>= {min_venue_count} venues)')
        ax.set_xlabel('Venue Count')
        ax.set_ylabel('Complex Name')
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.write("No complexes found with the specified minimum venue count.")

elif query_key == "query_venues_in_chile":
    # First, get all unique countries for the selectbox
    countries_query = "SELECT DISTINCT country FROM venues ORDER BY country;"
    df_countries = load_data(countries_query)
    all_countries = sorted(df_countries['country'].unique().tolist())

    selected_country = st.selectbox('Select a Country:', all_countries, index=all_countries.index('CHILE') if 'CHILE' in all_countries else 0, key='venue_country_filter')

    if selected_country:
        dynamic_query = QUERIES[query_key].format(selected_country=selected_country)
        df = load_data(dynamic_query)
        st.dataframe(df)
    else:
        st.write("Please select a country to view venue details.")

elif query_key == "query_venues_grouped_by_country":
    df = load_data(QUERIES[query_key])
    st.dataframe(df)
    if not df.empty:
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.barplot(
            x='venue_count',
            y='country',
            data=df.head(15),
            ax=ax,
            palette='plasma'
        )
        ax.set_title('Top 15 Countries by Number of Venues')
        ax.set_xlabel('Venue Count')
        ax.set_ylabel('Country')
        st.pyplot(fig)
        plt.close(fig)

elif query_key == "query_total_points_croatia":
    # First, get all unique countries for the selectbox
    countries_query = "SELECT DISTINCT country FROM competitors ORDER BY country;"
    df_countries = load_data(countries_query)
    all_competitor_countries = sorted(df_countries['country'].unique().tolist())

    # Default to 'Croatia' if available, otherwise select the first country
    croatia_index = all_competitor_countries.index('Croatia') if 'Croatia' in all_competitor_countries else 0
    selected_competitor_country = st.selectbox(
        'Select a country for competitor points:',
        all_competitor_countries,
        index=croatia_index,
        key='competitor_country_filter'
    )

    if selected_competitor_country:
        dynamic_query = QUERIES[query_key].format(selected_country=selected_competitor_country)
        df = load_data(dynamic_query)
        st.dataframe(df)
    else:
        st.write("Please select a country to view total competitor points.")

elif query_key == "query_competitor_count_by_country":
    df = load_data(QUERIES[query_key])
    st.dataframe(df)
    if not df.empty:
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.barplot(
            x='competitor_count',
            y='country',
            data=df.head(15),
            ax=ax,
            palette='rocket'
        )
        ax.set_title('Top 15 Countries by Number of Competitors')
        ax.set_xlabel('Competitor Count')
        ax.set_ylabel('Country')
        st.pyplot(fig)
        plt.close(fig)

else:
    df = load_data(QUERIES[query_key])
    st.dataframe(df)
