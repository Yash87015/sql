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
    'total_competitors': """
SELECT COUNT(DISTINCT competitor_id) AS Total_Competitors FROM competitors;
""",
    'total_countries_competitors': """
SELECT COUNT(DISTINCT country) AS Total_Countries FROM competitors WHERE country IS NOT NULL AND country != '';
""",
    'highest_points_competitor': """
SELECT MAX(points) AS Highest_Points FROM competitor_rankings;
""",
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
    'competitions_by_type': """
SELECT id, name, type, gender, category_id, level
FROM competitions
WHERE type = ?;
""",
    'competition_types_overall_distribution': """
SELECT type, COUNT(*) AS type_count
FROM competitions
WHERE type IS NOT NULL AND type != ''
GROUP BY type
ORDER BY type_count DESC;
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
SELECT
    timezone, COUNT(venue_id) AS venue_count
FROM
    venues
WHERE timezone IS NOT NULL AND timezone != ''
GROUP BY
    timezone
ORDER BY
    venue_count DESC;
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
    'filtered_competitors': """
SELECT
    c.competitor_name,
    c.country,
    r.rank,
    r.points,
    r.movement
FROM
    competitors c
JOIN
    competitor_rankings r ON c.competitor_id = r.competitor_id
WHERE
    (:name_filter IS NULL OR c.competitor_name LIKE :name_filter) AND
    (:min_rank_filter IS NULL OR r.rank >= :min_rank_filter) AND
    (:max_rank_filter IS NULL OR r.rank <= :max_rank_filter) AND
    (:country_filter IS NULL OR c.country = :country_filter) AND
    (:min_points_filter IS NULL OR r.points >= :min_points_filter)
ORDER BY r.rank;
""",
    'competitor_details': """
SELECT
    c.competitor_name,
    c.country,
    r.rank,
    r.points,
    r.movement,
    r.competitions_played
FROM
    competitors c
JOIN
    competitor_rankings r ON c.competitor_id = r.competitor_id
WHERE
    c.competitor_id = ?;
""",
    'all_competitors_name_id': """
SELECT competitor_id, competitor_name FROM competitors ORDER BY competitor_name;
""",
    'country_wise_analysis': """
SELECT
    c.country,
    COUNT(c.competitor_id) AS Total_Competitors,
    AVG(r.points) AS Average_Points
FROM
    competitors c
JOIN
    competitor_rankings r ON c.competitor_id = r.competitor_id
WHERE
    c.country IS NOT NULL AND c.country != ''
GROUP BY
    c.country
ORDER BY
    Average_Points DESC;
""",
    'top_ranked_competitors': """
SELECT
    c.competitor_name,
    c.country,
    r.rank,
    r.points
FROM
    competitors c
JOIN
    competitor_rankings r ON c.competitor_id = r.competitor_id
ORDER BY
    r.rank ASC
LIMIT ?;
""",
    'top_points_competitors': """
SELECT
    c.competitor_name,
    c.country,
    r.rank,
    r.points
FROM
    competitors c
JOIN
    competitor_rankings r ON c.competitor_id = r.competitor_id
ORDER BY
    r.points DESC
LIMIT ?;
""",
    'competition_levels_distribution': """
SELECT
    level, COUNT(*) AS count
FROM
    competitions
WHERE
    level IS NOT NULL AND level != ''
GROUP BY
    level
ORDER BY
    count DESC;
"""
}

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Tennish DB Analysis", layout="wide")
st.title("🎾 Tennish Database Analysis 🎾")

# --- Cached Database Connection ---
def get_db_connection():
    logging.info("Attempting to get a database connection...")
    try:
        conn = sql.connect('tennish.db', check_same_thread=False)
        logging.info("Database connection obtained.")
        return conn
    except sql.Error as e:
        logging.error(f"Database connection error: {e}")
        st.error(f"Error connecting to database: {e}")
        return None

# --- Cached Data Loading Function ---
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
        return pd.DataFrame() # Return empty DataFrame on error
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")

# --- Main Application Logic ---
def main():
    # --- Homepage Dashboard Section ---
    st.header("Dashboard Overview")
    col1, col2, col3 = st.columns(3)

    # Total Competitors
    total_competitors_df = load_data(QUERIES['total_competitors'])
    total_competitors = total_competitors_df['Total_Competitors'].iloc[0] if not total_competitors_df.empty else 0
    col1.metric("Total Competitors", total_competitors)

    # Number of Countries represented by Competitors
    total_countries_df = load_data(QUERIES['total_countries_competitors'])
    total_countries = total_countries_df['Total_Countries'].iloc[0] if not total_countries_df.empty else 0
    col2.metric("Countries Represented", total_countries)

    # Highest Points Scored by a Competitor
    highest_points_df = load_data(QUERIES['highest_points_competitor'])
    highest_points = highest_points_df['Highest_Points'].iloc[0] if not highest_points_df.empty else 0
    col3.metric("Highest Competitor Points", highest_points)

    st.markdown("--- # Query Selection")

    # --- User-friendly Query Names Mapping ---
    QUERY_NAMES = {
        'competitions_with_categories': '1. List all competitions along with their category name',
        'count_competitions_by_category': '2. Count the number of competitions in each category',
        'competitions_by_type': "3. Find all competitions of a specific type (e.g., 'doubles')",
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
        'highest_points_current_week': '22. Find competitors with the highest points in the current week',
        'filtered_competitors': '23. Competitor Search and Filtering',
        'competitor_details': '24. View Competitor Details',
        'country_wise_analysis': '25. Country-Wise Competitor Analysis (Count & Avg Points)',
        'top_ranked_competitors': '26. Top Ranked Competitors',
        'top_points_competitors': '27. Top Competitors by Points',
        'competition_levels_distribution': '28. Distribution of Competition Levels'
    }

    query_options = list(QUERY_NAMES.values())

    # --- Load dynamic filter options ---
    all_category_names = load_data("SELECT DISTINCT category_name FROM categories ORDER BY category_name;")['category_name'].tolist()
    all_venue_countries = load_data("SELECT DISTINCT country FROM venues WHERE country IS NOT NULL AND country != '' ORDER BY country;")['country'].tolist()
    all_competitor_countries = load_data("SELECT DISTINCT country FROM competitors WHERE country IS NOT NULL AND country != '' ORDER BY country;")['country'].tolist()
    all_complex_names = load_data("SELECT DISTINCT complex_name FROM complexes WHERE complex_name IS NOT NULL AND complex_name != '' ORDER BY complex_name;")['complex_name'].tolist()
    all_competition_types = load_data("SELECT DISTINCT type FROM competitions WHERE type IS NOT NULL AND type != '' ORDER BY type;")['type'].tolist()

    # Load all competitor names and IDs for the details viewer
    all_competitors_df = load_data(QUERIES['all_competitors_name_id'])
    all_competitor_names = all_competitors_df['competitor_name'].tolist() if not all_competitors_df.empty else []
    competitor_name_to_id = dict(zip(all_competitors_df['competitor_name'], all_competitors_df['competitor_id']))

    # Load max values for filters
    max_rank_df = load_data("SELECT MAX(rank) AS max_rank FROM competitor_rankings;")
    max_rank = int(max_rank_df['max_rank'].iloc[0]) if not max_rank_df.empty else 1000

    max_points_df = load_data("SELECT MAX(points) AS max_points FROM competitor_rankings;")
    max_points = int(max_points_df['max_points'].iloc[0]) if not max_points_df.empty else 10000

    selected_query_display_name = st.selectbox(
        'Select a query to run:',
        options=query_options
    )

    selected_query_key = next((key for key, value in QUERY_NAMES.items() if value == selected_query_display_name), None)

    if selected_query_key:
        st.subheader(f"Results for: {selected_query_display_name}")

        # --- Conditional Display Logic ---
        if selected_query_key == 'competitions_with_categories':
            df = load_data(QUERIES[selected_query_key])
            st.dataframe(df)

        elif selected_query_key == 'count_competitions_by_category':
            df = load_data(QUERIES[selected_query_key])
            st.dataframe(df)
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='competition_count', y='category_name', data=df.head(10), ax=ax, palette='viridis')
            ax.set_title('Top 10 Categories by Competition Count')
            ax.set_xlabel('Number of Competitions')
            ax.set_ylabel('Category Name')
            st.pyplot(fig)
            plt.close(fig)

        elif selected_query_key == 'competitions_by_type':
            # Overall distribution of competition types (Pie Chart)
            type_dist_df = load_data(QUERIES['competition_types_overall_distribution'])
            if not type_dist_df.empty:
                fig, ax = plt.subplots(figsize=(4, 5))
                ax.pie(type_dist_df['type_count'], labels=type_dist_df['type'], autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'black'})
                ax.set_title('Overall Distribution of Competition Types')
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("No competition type distribution data available.")

            # Filtered results
            selected_type = st.selectbox(
                'Select a Competition Type to Filter:',
                options=all_competition_types,
                index=all_competition_types.index('doubles') if 'doubles' in all_competition_types else 0
            )
            df = load_data(QUERIES[selected_query_key], params=[selected_type])
            st.dataframe(df)

        elif selected_query_key == 'competitions_by_category':
            selected_category = st.selectbox(
                'Select a Category:',
                options=all_category_names,
                index=all_category_names.index('ITF Men') if 'ITF Men' in all_category_names else 0
            )
            df = load_data(QUERIES[selected_query_key], params=[selected_category])
            st.dataframe(df)

        elif selected_query_key == 'parent_sub_competitions':
            df = load_data(QUERIES[selected_query_key])
            st.dataframe(df)

        elif selected_query_key == 'competition_type_by_category_distribution':
            df = load_data(QUERIES[selected_query_key])
            st.dataframe(df)

            selected_category_for_plot = st.selectbox(
                'Select a Category to visualize Type Distribution:',
                options=['All'] + all_category_names,
                index=0
            )
            if selected_category_for_plot != 'All':
                plot_df = df[df['Category'] == selected_category_for_plot]
            else:
                plot_df = df

            if not plot_df.empty:
                fig, ax = plt.subplots(figsize=(12, 7))
                sns.barplot(x='Total_Count', y='Competition_Type', hue='Category', data=plot_df.head(20), dodge=False, ax=ax, palette='coolwarm')
                ax.set_title(f'Distribution of Competition Types for {selected_category_for_plot}')
                ax.set_xlabel('Total Count')
                ax.set_ylabel('Competition Type')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("No data to display for the selected category.")

        elif selected_query_key == 'top_level_competitions':
            df = load_data(QUERIES[selected_query_key])
            st.dataframe(df)

        elif selected_query_key == 'count_null_parent_id':
            df = load_data(QUERIES[selected_query_key])
            st.dataframe(df)

        elif selected_query_key == 'venues_with_complex_name':
            df = load_data(QUERIES[selected_query_key])
            st.dataframe(df)

        elif selected_query_key == 'venue_count_by_complex' or selected_query_key == 'venue_count_by_complex_desc':
            min_venue_count = st.number_input('Minimum number of venues in a complex:', min_value=0, value=1)
            df = load_data(QUERIES[selected_query_key])
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
            selected_country = st.selectbox(
                'Select a Country:',
                options=all_venue_countries,
                index=all_venue_countries.index('CHILE') if 'CHILE' in all_venue_countries else 0
            )
            df = load_data(QUERIES[selected_query_key], params=[selected_country])
            st.dataframe(df)

        elif selected_query_key == 'venues_timezones':
            df = load_data(QUERIES[selected_query_key])
            st.dataframe(df)
            if not df.empty:
                fig, ax = plt.subplots(figsize=(12, 7))
                sns.barplot(x='venue_count', y='timezone', data=df.head(15), ax=ax, palette='coolwarm')
                ax.set_title('Top 15 Timezones by Venue Count')
                ax.set_xlabel('Number of Venues')
                ax.set_ylabel('Timezone')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("No timezone data available for visualization.")

        elif selected_query_key == 'complex_more_than_one_venue':
            df = load_data(QUERIES[selected_query_key])
            st.dataframe(df)

        elif selected_query_key == 'venues_grouped_by_country':
            df = load_data(QUERIES[selected_query_key])
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
            selected_complex = st.selectbox(
                'Select a Complex Name:',
                options=all_complex_names,
                index=all_complex_names.index('Nacional') if 'Nacional' in all_complex_names else 0
            )
            df = load_data(QUERIES[selected_query_key], params=[selected_complex])
            st.dataframe(df)

        elif selected_query_key == 'competitors_rank_points':
            df = load_data(QUERIES[selected_query_key])
            st.dataframe(df)

        elif selected_query_key == 'top_5_competitors':
            df = load_data(QUERIES[selected_query_key])
            st.dataframe(df)

        elif selected_query_key == 'stable_rank_competitors':
            df = load_data(QUERIES[selected_query_key])
            st.dataframe(df)

        elif selected_query_key == 'total_points_by_country':
            selected_country = st.selectbox(
                'Select a Country for Competitor Points:',
                options=all_competitor_countries,
                index=all_competitor_countries.index('Croatia') if 'Croatia' in all_competitor_countries else 0
            )
            df = load_data(QUERIES[selected_query_key], params=[selected_country])
            st.dataframe(df)

        elif selected_query_key == 'competitors_per_country':
            df = load_data(QUERIES[selected_query_key])
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
            df = load_data(QUERIES[selected_query_key])
            st.dataframe(df)

        elif selected_query_key == 'filtered_competitors':
            st.subheader("Competitor Search Filters")
            col_search_1, col_search_2 = st.columns(2)

            competitor_name_filter = col_search_1.text_input('Search by Competitor Name (e.g., "Federer")')
            rank_range = col_search_2.slider('Filter by Rank Range', min_value=1, max_value=max_rank, value=(1, max_rank))

            col_search_3, col_search_4 = st.columns(2)
            country_filter = col_search_3.selectbox(
                'Filter by Country',
                options=['All'] + all_competitor_countries
            )
            min_points_filter = col_search_4.number_input('Minimum Points Threshold', min_value=0, value=0, max_value=max_points)

            # Prepare parameters for the SQL query
            params = {
                'name_filter': f'%{competitor_name_filter}%' if competitor_name_filter else None,
                'min_rank_filter': rank_range[0],
                'max_rank_filter': rank_range[1],
                'country_filter': country_filter if country_filter != 'All' else None,
                'min_points_filter': min_points_filter if min_points_filter > 0 else None
            }
            # For rank, if the slider is at its default full range (1, max_rank), we treat it as no filter
            if rank_range[0] == 1 and rank_range[1] == max_rank:
                params['min_rank_filter'] = None
                params['max_rank_filter'] = None

            df_filtered = load_data(QUERIES[selected_query_key], params=params)
            st.dataframe(df_filtered)

        elif selected_query_key == 'competitor_details':
            st.subheader("View Detailed Competitor Information")
            if all_competitor_names:
                selected_competitor_name = st.selectbox(
                    'Select a Competitor:',
                    options=all_competitor_names
                )
                selected_competitor_id = competitor_name_to_id.get(selected_competitor_name)
                if selected_competitor_id:
                    competitor_detail_df = load_data(QUERIES[selected_query_key], params=[selected_competitor_id])
                    if not competitor_detail_df.empty:
                        st.dataframe(competitor_detail_df)
                    else:
                        st.info("No details found for the selected competitor.")
                else:
                    st.info("Competitor ID not found.")
            else:
                st.info("No competitors available to display details.")

        elif selected_query_key == 'country_wise_analysis':
            st.subheader("Country-Wise Competitor Analysis (Count & Avg Points)")
            df = load_data(QUERIES[selected_query_key])
            st.dataframe(df)

            if not df.empty:
                fig, ax = plt.subplots(figsize=(14, 8))
                sns.barplot(x='Average_Points', y='country', data=df.head(15), ax=ax, palette='viridis')
                ax.set_title('Top 15 Countries by Average Competitor Points')
                ax.set_xlabel('Average Points')
                ax.set_ylabel('Country')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("No data to display for country-wise analysis.")

        elif selected_query_key == 'top_ranked_competitors':
            st.subheader("Top Ranked Competitors")
            num_competitors_rank = st.number_input('Number of top-ranked competitors to display:', min_value=1, value=10, max_value=max_rank)
            df = load_data(QUERIES[selected_query_key], params=[num_competitors_rank])
            st.dataframe(df)

        elif selected_query_key == 'top_points_competitors':
            st.subheader("Top Competitors by Points")
            num_competitors_points = st.number_input('Number of competitors with highest points to display:', min_value=1, value=10, max_value=max_rank)
            df = load_data(QUERIES[selected_query_key], params=[num_competitors_points])
            st.dataframe(df)

        elif selected_query_key == 'competition_levels_distribution':
            df = load_data(QUERIES[selected_query_key])
            st.dataframe(df)
            if not df.empty:
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(x='count', y='level', data=df, ax=ax, palette='cubehelix')
                ax.set_title('Distribution of Competition Levels')
                ax.set_xlabel('Number of Competitions')
                ax.set_ylabel('Competition Level')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("No data to display for competition levels distribution.")


if __name__ == "__main__":
    main()
