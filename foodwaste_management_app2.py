
import streamlit as st
import pandas as pd
import sqlite3 as sql
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Connect to the database
conn = sql.connect('database.db')

st.title('Food Waste Management Dashboard')

# --- Dataset Information ---
st.header('Dataset Information')

# Get and display the total number of records for each table
provider_count = pd.read_sql("SELECT COUNT(*) FROM provider_data", conn).iloc[0, 0]
receivers_count = pd.read_sql("SELECT COUNT(*) FROM receivers_data", conn).iloc[0, 0]
food_listings_count = pd.read_sql("SELECT COUNT(*) FROM food_listings_data", conn).iloc[0, 0]
claims_count = pd.read_sql("SELECT COUNT(*) FROM claims_data", conn).iloc[0, 0]

st.write(f"**Provider Data:** {provider_count} records available.")
st.write(f"**Receivers Data:** {receivers_count} records available.")
st.write(f"**Food Listings Data:** {food_listings_count} records available.")
st.write(f"**Claims Data:** {claims_count} records available.")


st.subheader('Provider Data Schema')
st.write(pd.read_sql("SELECT sql FROM sqlite_master WHERE name='provider_data'", conn).iloc[0, 0])
st.subheader('First 5 Rows of Provider Data')
st.dataframe(pd.read_sql("SELECT * FROM provider_data LIMIT 5", conn))


st.subheader('Receivers Data Schema')
st.write(pd.read_sql("SELECT sql FROM sqlite_master WHERE name='receivers_data'", conn).iloc[0, 0])
st.subheader('First 5 Rows of Receivers Data')
st.dataframe(pd.read_sql("SELECT * FROM receivers_data LIMIT 5", conn))


st.subheader('Food Listings Data Schema')
st.write(pd.read_sql("SELECT sql FROM sqlite_master WHERE name='food_listings_data'", conn).iloc[0, 0])
st.subheader('First 5 Rows of Food Listings Data')
st.dataframe(pd.read_sql("SELECT * FROM food_listings_data LIMIT 5", conn))


st.subheader('Claims Data Schema')
st.write(pd.read_sql("SELECT sql FROM sqlite_master WHERE name='claims_data'", conn).iloc[0, 0])
st.subheader('First 5 Rows of Claims Data')
st.dataframe(pd.read_sql("SELECT * FROM claims_data LIMIT 5", conn))



# --- Analysis and Visualizations ---
st.header('Analysis and Visualizations')

# Add filters to the sidebar
st.sidebar.header("Filter Options")

status_options = ['All'] + list(pd.read_sql("SELECT DISTINCT Status FROM claims_data", conn)['Status'])
selected_status = st.sidebar.selectbox('Select Claim Status:', status_options)

provider_type_options = ['All'] + list(pd.read_sql("SELECT DISTINCT Type FROM provider_data", conn)['Type'])
selected_provider_type = st.sidebar.selectbox('Select Provider Type:', provider_type_options)

receiver_type_options = ['All'] + list(pd.read_sql("SELECT DISTINCT Type FROM receivers_data", conn)['Type'])
selected_receiver_type = st.sidebar.selectbox('Select Receiver Type:', receiver_type_options)

food_type_options = ['All'] + list(pd.read_sql("SELECT DISTINCT Food_type FROM food_listings_data", conn)['Food_type'])
selected_food_type = st.sidebar.selectbox('Select Food Type:', food_type_options)

meal_type_options = ['All'] + list(pd.read_sql("SELECT DISTINCT Meal_Type FROM food_listings_data", conn)['Meal_Type'])
selected_meal_type = st.sidebar.selectbox('Select Meal Type:', meal_type_options)

location_options = ['All'] + list(pd.read_sql("SELECT DISTINCT Location FROM food_listings_data", conn)['Location'])
selected_location = st.sidebar.selectbox('Select Location:', location_options)


# --- Dynamic Metric Cards ---
st.subheader("Key Metrics")

# Query for number of providers with filters
query_provider_count_filtered = "SELECT COUNT(DISTINCT Provider_ID) FROM provider_data WHERE 1=1"
if selected_provider_type != 'All':
    query_provider_count_filtered += f" AND Type = '{selected_provider_type}'"
# Location filter is not directly applicable to provider count unless we join with food_listings_data
# For simplicity, I will not apply location filter here.

filtered_provider_count = pd.read_sql(query_provider_count_filtered, conn).iloc[0, 0]

# Query for number of receivers with filters
query_receiver_count_filtered = "SELECT COUNT(DISTINCT Receiver_ID) FROM receivers_data WHERE 1=1"
if selected_receiver_type != 'All':
    query_receiver_count_filtered += f" AND Type = '{selected_receiver_type}'"
# Location filter is not directly applicable to receiver count unless we join with claims_data and food_listings_data
# For simplicity, I will not apply location filter here.
filtered_receiver_count = pd.read_sql(query_receiver_count_filtered, conn).iloc[0, 0]


# Query for number of claims with filters
query_claims_count_filtered = """
SELECT COUNT(T1.Claim_ID)
FROM claims_data AS T1
JOIN food_listings_data AS T2 ON T1.Food_ID = T2.Food_ID
JOIN receivers_data AS T3 ON T1.Receiver_ID = T3.Receiver_ID
WHERE 1=1
"""
if selected_status != 'All':
    query_claims_count_filtered += f" AND T1.Status = '{selected_status}'"
if selected_receiver_type != 'All':
    query_claims_count_filtered += f" AND T3.Type = '{selected_receiver_type}'"
if selected_food_type != 'All':
    query_claims_count_filtered += f" AND T2.Food_type = '{selected_food_type}'"
if selected_meal_type != 'All':
    query_claims_count_filtered += f" AND T2.Meal_Type = '{selected_meal_type}'"
if selected_location != 'All':
    query_claims_count_filtered += f" AND T2.Location = '{selected_location}'"

filtered_claims_count = pd.read_sql(query_claims_count_filtered, conn).iloc[0, 0]
if filtered_claims_count is None:
    filtered_claims_count = 0

# Query for total quantity with filters
query_total_quantity_filtered = """
SELECT SUM(T1.Quantity)
FROM food_listings_data AS T1
JOIN provider_data AS T2 ON T1.Provider_ID = T2.Provider_ID
WHERE 1=1
"""
if selected_provider_type != 'All':
    query_total_quantity_filtered += f" AND T2.Type = '{selected_provider_type}'"
if selected_food_type != 'All':
    query_total_quantity_filtered += f" AND T1.Food_type = '{selected_food_type}'"
if selected_meal_type != 'All':
    query_total_quantity_filtered += f" AND T1.Meal_Type = '{selected_meal_type}'"
if selected_location != 'All':
    query_total_quantity_filtered += f" AND T1.Location = '{selected_location}'"


filtered_total_quantity = pd.read_sql(query_total_quantity_filtered, conn).iloc[0, 0]
if filtered_total_quantity is None:
    filtered_total_quantity = 0

# Display metrics in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Number of Providers", value=filtered_provider_count)

with col2:
    st.metric(label="Number of Receivers", value=filtered_receiver_count)

with col3:
    st.metric(label="Number of Claims", value=filtered_claims_count)

with col4:
    st.metric(label="Total Quantity (Units)", value=filtered_total_quantity)


# Create a selection box for the user to choose the analysis
analysis_option = st.selectbox(
    'Select an analysis to view:',
    (
        'Number of Food Providers and Receivers in Each City',
        'Percentage of Food Providers by Type',
        'Contact Information by City',
        'Receivers with the Most Claims',
        'Receivers with the Most Completed Claims',
        'Total Quantity of Food Available from All Providers',
        'Location with the Highest Number of Food Listings',
        'Cities with the Highest Number of Food Listings (Top 20)',
        'Most Commonly Available Food Types',
        'Number of Food Claims for Each Food Item',
        'Providers with the Highest Number of Successful Food Claims (Top 20)',
        'Percentage of Food Claims by Status',
        'Average Quantity of Food Claimed per Receiver',
        'Percentage of Food Claims by Meal Type',
        'Total Quantity of Food Donated by Each Provider',
        'Number of Food Listings and Claims Over Time',
        'Number of Food Claims by Status Over Time',
        'Number of Food Listings by Provider Type Over Time',
        'Total Quantity Donated by Provider (Top 20)',
        'Total Quantity Claimed by Receiver (Top 20)'
    )
)

# Display the selected analysis and visualization
if analysis_option == 'Number of Food Providers and Receivers in Each City':
    st.subheader('Q1: Number of Food Providers and Receivers in Each City')
    query_1 = """
    SELECT
        T1.City,
        COUNT(DISTINCT T1.Provider_ID) AS Number_of_Providers,
        COUNT(DISTINCT T2.Receiver_ID) AS Number_of_Receivers
    FROM provider_data AS T1
    LEFT JOIN receivers_data AS T2 ON T1.City = T2.City
    WHERE 1=1
    """
    if selected_provider_type != 'All':
        query_1 += f" AND T1.Type = '{selected_provider_type}'"
    if selected_receiver_type != 'All':
        query_1 += f" AND T2.Type = '{selected_receiver_type}'"
    # Location filter is not directly applicable at the city level unless we join

    query_1 += """
    GROUP BY T1.City;
    """
    result_1 = pd.read_sql(query_1, conn)
    st.dataframe(result_1)

    st.subheader('Top 20 Cities by Number of Food Providers and Receivers')
    result_1['Total_Count'] = result_1['Number_of_Providers'] + result_1['Number_of_Receivers']
    top_20_cities = result_1.sort_values(by='Total_Count', ascending=False).head(20)
    fig1, ax1 = plt.subplots(figsize=(12, 7))
    sns.barplot(x='City', y='Number_of_Providers', data=top_20_cities, ax=ax1)
    sns.barplot(x='City', y='Number_of_Receivers', data=top_20_cities, ax=ax1)
    plt.title('Top 20 Cities by Number of Food Providers and Receivers')
    plt.xlabel('City')
    plt.ylabel('Number of Providers/Receivers')
    plt.xticks(rotation=90)
    ax1.legend(['Providers', 'Receivers'])
    plt.tight_layout()
    st.pyplot(fig1)


elif analysis_option == 'Percentage of Food Providers by Type':
    st.subheader('Q2: Percentage of Food Providers by Type')
    query_2 = """
    SELECT
        Type,
        COUNT(*) AS Number_of_Providers
    FROM provider_data
    WHERE 1=1
    """
    if selected_provider_type != 'All':
        query_2 += f" AND Type = '{selected_provider_type}'"
    # Location filter is not directly applicable

    query_2 += """
    GROUP BY Type
    ORDER BY Number_of_Providers DESC;
    """
    result_2 = pd.read_sql(query_2, conn)
    st.dataframe(result_2)

    fig2, ax2 = plt.subplots(figsize=(6, 6))
    ax2.pie(result_2['Number_of_Providers'], labels=result_2['Type'], autopct='%1.1f%%', startangle=90)
    ax2.set_title('Percentage of Food Providers by Type')
    st.pyplot(fig2)

elif analysis_option == 'Contact Information by City':
    st.subheader('Contact Information by City')
    provider_city_query = "SELECT DISTINCT City FROM provider_data ORDER BY City;"
    provider_cities = pd.read_sql(provider_city_query, conn)['City'].tolist()
    selected_provider_city = st.selectbox('Select a city for Provider Contact Information:', provider_cities)

    st.subheader(f"Provider Contact Information in {selected_provider_city}:")
    query_provider_contact = f"""
    SELECT
        Name,
        Contact,
        Type
    FROM provider_data
    WHERE City = '{selected_provider_city}'
    """
    if selected_provider_type != 'All':
        query_provider_contact += f" AND Type = '{selected_provider_type}'"
    query_provider_contact += ";"
    result_provider_contact = pd.read_sql(query_provider_contact, conn)
    st.dataframe(result_provider_contact)

    receiver_city_query = "SELECT DISTINCT City FROM receivers_data ORDER BY City;"
    receiver_cities = pd.read_sql(receiver_city_query, conn)['City'].tolist()
    selected_receiver_city = st.selectbox('Select a city for Receiver Contact Information:', receiver_cities)

    st.subheader(f"Receiver Contact Information in {selected_receiver_city}:")
    query_receiver_contact = f"""
    SELECT
        Name,
        Contact,
        Type
    FROM receivers_data
    WHERE City = '{selected_receiver_city}'
    """
    if selected_receiver_type != 'All':
        query_receiver_contact += f" AND Type = '{selected_receiver_type}'"
    query_receiver_contact += ";"
    result_receiver_contact = pd.read_sql(query_receiver_contact, conn)
    st.dataframe(result_receiver_contact)


elif analysis_option == 'Receivers with the Most Claims':
    st.subheader('Q4: Receivers with the Most Claims')
    query_4 = """
    SELECT T1.Name, COUNT(*) AS Number_of_Claims
    FROM receivers_data AS T1
    JOIN claims_data AS T2 ON T1.Receiver_ID = T2.Receiver_ID
    JOIN food_listings_data AS T3 ON T2.Food_ID = T3.Food_ID
    WHERE 1=1
    """
    if selected_receiver_type != 'All':
        query_4 += f" AND T1.Type = '{selected_receiver_type}'"
    if selected_status != 'All':
        query_4 += f" AND T2.Status = '{selected_status}'"
    if selected_food_type != 'All':
        query_4 += f" AND T3.Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_4 += f" AND T3.Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_4 += f" AND T3.Location = '{selected_location}'"


    query_4 += """
    GROUP BY T1.Name
    ORDER BY Number_of_Claims DESC;
    """
    result_4 = pd.read_sql(query_4, conn)
    st.dataframe(result_4)

    st.subheader('Top 20 Receivers by Number of Claims')
    fig4, ax4 = plt.subplots(figsize=(12, 7))
    sns.barplot(x='Name', y='Number_of_Claims', data=result_4.head(20), ax=ax4)
    plt.title('Top 20 Receivers by Number of Claims')
    plt.xlabel('Receiver Name')
    plt.ylabel('Number of Claims')
    plt.xticks(rotation=90)
    plt.tight_layout()
    st.pyplot(fig4)

elif analysis_option == 'Receivers with the Most Completed Claims':
    st.subheader('Receivers with the Most Completed Claims')
    extra_query2 = """
    SELECT T1.Name, COUNT(*) AS Number_of_Claims
    FROM receivers_data AS T1
    JOIN claims_data AS T2 ON T1.Receiver_ID = T2.Receiver_ID
    JOIN food_listings_data AS T3 ON T2.Food_ID = T3.Food_ID
    WHERE T2.Status = 'Completed'
    """
    if selected_receiver_type != 'All':
        extra_query2 += f" AND T1.Type = '{selected_receiver_type}'"
    if selected_food_type != 'All':
        extra_query2 += f" AND T3.Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        extra_query2 += f" AND T3.Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        extra_query2 += f" AND T3.Location = '{selected_location}'"


    extra_query2 += """
    GROUP BY T1.Name
    ORDER BY Number_of_Claims DESC;
    """
    extra_result2 = pd.read_sql(extra_query2, conn)
    st.dataframe(extra_result2)

    st.subheader('Top 20 Receivers by Number of Completed Claims')
    fig_extra2, ax_extra2 = plt.subplots(figsize=(12, 7))
    sns.barplot(x='Name', y='Number_of_Claims', data=extra_result2.head(20), ax=ax_extra2)
    plt.title('Top 20 Receivers by Number of Completed Claims')
    plt.xlabel('Receiver Name')
    plt.ylabel('Number of Completed Claims')
    plt.xticks(rotation=90)
    plt.tight_layout()
    st.pyplot(fig_extra2)

elif analysis_option == 'Total Quantity of Food Available from All Providers':
    st.subheader('Q5: Total Quantity of Food Available from All Providers')
    query_5 = """
    SELECT SUM(Quantity) AS Total_Quantity
    FROM food_listings_data
    WHERE 1=1
    """
    if selected_provider_type != 'All':
        query_5 += f" AND Provider_Type = '{selected_provider_type}'"
    if selected_food_type != 'All':
        query_5 += f" AND Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_5 += f" AND Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_5 += f" AND Location = '{selected_location}'"

    query_5 += ";"
    result_5 = pd.read_sql(query_5, conn)
    st.dataframe(result_5)

elif analysis_option == 'Location with the Highest Number of Food Listings':
    st.subheader('Q6: Location with the Highest Number of Food Listings')
    query_6 = """
    SELECT Location, COUNT(*) AS Number_of_Listings
    FROM food_listings_data
    WHERE 1=1
    """
    if selected_provider_type != 'All':
        query_6 += f" AND Provider_Type = '{selected_provider_type}'"
    if selected_food_type != 'All':
        query_6 += f" AND Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_6 += f" AND Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_6 += f" AND Location = '{selected_location}'"
    query_6 += """
    GROUP BY Location
    ORDER BY Number_of_Listings DESC
    LIMIT 1;
    """
    result_6 = pd.read_sql(query_6, conn)
    st.dataframe(result_6)

elif analysis_option == 'Cities with the Highest Number of Food Listings (Top 20)':
    st.subheader('Cities with the Highest Number of Food Listings (Top 20)')
    query_Extra = """
    SELECT T1.City, COUNT(T2.Food_ID) AS Number_of_Listings
    FROM provider_data AS T1
    JOIN food_listings_data AS T2 ON T1.Provider_ID = T2.Provider_ID
    WHERE 1=1
    """
    if selected_provider_type != 'All':
        query_Extra += f" AND T1.Type = '{selected_provider_type}'"
    if selected_food_type != 'All':
        query_Extra += f" AND T2.Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_Extra += f" AND T2.Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_Extra += f" AND T2.Location = '{selected_location}'"

    query_Extra += """
    GROUP BY T1.City
    ORDER BY Number_of_Listings DESC
    LIMIT 20;
    """
    result_Extra = pd.read_sql(query_Extra, conn)
    st.dataframe(result_Extra)

elif analysis_option == 'Most Commonly Available Food Types':
    st.subheader('Q7: Most Commonly Available Food Types')
    query_7 = """
    SELECT Food_type, COUNT(*) AS Number_of_Listings
    FROM food_listings_data
    WHERE 1=1
    """
    if selected_provider_type != 'All':
        query_7 += f" AND Provider_Type = '{selected_provider_type}'"
    if selected_food_type != 'All':
        query_7 += f" AND Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_7 += f" AND Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_7 += f" AND Location = '{selected_location}'"

    query_7 += """
    GROUP BY Food_type
    ORDER BY Number_of_Listings DESC;
    """
    result_7 = pd.read_sql(query_7, conn)
    st.dataframe(result_7)

elif analysis_option == 'Number of Food Claims for Each Food Item':
    st.subheader('Q8: Number of Food Claims for Each Food Item')
    query_8 = """
    SELECT
        T1.Food_ID,
        T2.Food_Name,
        COUNT(T1.Claim_ID) AS Number_of_Claims
    FROM claims_data AS T1
    JOIN food_listings_data AS T2 ON T1.Food_ID = T2.Food_ID
    WHERE 1=1
    """
    if selected_status != 'All':
        query_8 += f" AND T1.Status = '{selected_status}'"
    if selected_food_type != 'All':
        query_8 += f" AND T2.Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_8 += f" AND T2.Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_8 += f" AND T2.Location = '{selected_location}'"

    query_8 += """
    GROUP BY T1.Food_ID, T2.Food_Name
    ORDER BY Number_of_Claims DESC;
    """
    result_8 = pd.read_sql(query_8, conn)
    st.dataframe(result_8)

    st.subheader('Top 20 Food Items by Number of Claims')
    fig8, ax8 = plt.subplots(figsize=(12, 7))
    sns.barplot(x='Food_Name', y='Number_of_Claims', data=result_8.head(20), ax=ax8)
    plt.title('Top 20 Food Items by Number of Claims')
    plt.xlabel('Food Item')
    plt.ylabel('Number of Claims')
    plt.xticks(rotation=90)
    plt.tight_layout()
    st.pyplot(fig8)


elif analysis_option == 'Providers with the Highest Number of Successful Food Claims (Top 20)':
    st.subheader('Q9: Providers with the Highest Number of Successful Food Claims (Top 20)')
    query_9 = """
    SELECT T2.Name, COUNT(T1.Claim_ID) AS Number_of_Claims
    FROM claims_data AS T1
    JOIN food_listings_data AS T3 ON T1.Food_ID = T3.Food_ID
    JOIN provider_data AS T2 ON T3.Provider_ID = T2.Provider_ID
    WHERE T1.Status = 'Completed'
    """
    if selected_provider_type != 'All':
        query_9 += f" AND T2.Type = '{selected_provider_type}'"
    if selected_food_type != 'All':
        query_9 += f" AND T3.Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_9 += f" AND T3.Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_9 += f" AND T3.Location = '{selected_location}'"

    query_9 += """
    GROUP BY T2.Name
    ORDER BY Number_of_Claims DESC
    LIMIT 20;
    """
    result_9 = pd.read_sql(query_9, conn)
    st.dataframe(result_9)

    fig9, ax9 = plt.subplots(figsize=(12, 7))
    sns.barplot(x='Name', y='Number_of_Claims', data=result_9, ax=ax9)
    plt.title('Top 20 Providers with Most Successful Claims')
    plt.xlabel('Provider Name')
    plt.ylabel('Number of Successful Claims')
    plt.xticks(rotation=90)
    plt.tight_layout()
    st.pyplot(fig9)


elif analysis_option == 'Percentage of Food Claims by Status':
    st.subheader('Q10: Percentage of Food Claims by Status')
    query_10 = """
    SELECT
        Status,
        COUNT(*) AS Number_of_Claims,
        (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims_data)) AS Percentage
    FROM claims_data
    WHERE 1=1
    """
    if selected_status != 'All':
        query_10 += f" AND Status = '{selected_status}'"
    # Location filter is not directly applicable

    query_10 += """
    GROUP BY Status;
    """
    result_10 = pd.read_sql(query_10, conn)
    st.dataframe(result_10)

    fig10, ax10 = plt.subplots(figsize=(6, 6))
    ax10.pie(result_10['Number_of_Claims'], labels=result_10['Status'], autopct='%1.1f%%', startangle=90)
    ax10.set_title('Percentage of Food Claims by Status')
    st.pyplot(fig10)

elif analysis_option == 'Average Quantity of Food Claimed per Receiver':
    st.subheader('Q11: Average Quantity of Food Claimed per Receiver')
    query_11 = """
    SELECT
        T2.Name AS Receiver_Name,
        AVG(T3.Quantity) AS Average_Quantity
    FROM claims_data AS T1
    JOIN receivers_data AS T2 ON T1.Receiver_ID = T2.Receiver_ID
    JOIN food_listings_data AS T3 ON T1.Food_ID = T3.Food_ID
    WHERE 1=1
    """
    if selected_status != 'All':
        query_11 += f" AND T1.Status = '{selected_status}'"
    if selected_receiver_type != 'All':
        query_11 += f" AND T2.Type = '{selected_receiver_type}'"
    if selected_food_type != 'All':
        query_11 += f" AND T3.Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_11 += f" AND T3.Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_11 += f" AND T3.Location = '{selected_location}'"

    query_11 += """
    GROUP BY T2.Name
    ORDER BY Average_Quantity DESC;
    """
    result_11 = pd.read_sql(query_11, conn)
    st.dataframe(result_11)

    st.subheader('Top 20 Receivers by Average Quantity Claimed')
    fig11, ax11 = plt.subplots(figsize=(12, 7))
    sns.barplot(x='Receiver_Name', y='Average_Quantity', data=result_11.head(20), ax=ax11)
    plt.title('Top 20 Receivers by Average Quantity Claimed')
    plt.xlabel('Receiver Name')
    plt.ylabel('Average Quantity')
    plt.xticks(rotation=90)
    plt.tight_layout()
    st.pyplot(fig11)


elif analysis_option == 'Percentage of Food Claims by Meal Type':
    st.subheader('Q12: Percentage of Food Claims by Meal Type')
    query_12 = """
    SELECT T1.Meal_Type, COUNT(T2.Claim_ID) AS Number_of_Claims
    FROM food_listings_data AS T1
    JOIN claims_data AS T2 ON T1.Food_ID = T2.Food_ID
    JOIN receivers_data AS T3 ON T2.Receiver_ID = T3.Receiver_ID
    WHERE 1=1
    """
    if selected_status != 'All':
        query_12 += f" AND T2.Status = '{selected_status}'"
    if selected_receiver_type != 'All':
        query_12 += f" AND T3.Type = '{selected_receiver_type}'"
    if selected_food_type != 'All':
        query_12 += f" AND T1.Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_12 += f" AND T1.Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_12 += f" AND T1.Location = '{selected_location}'"

    query_12 += """
    GROUP BY T1.Meal_Type
    ORDER BY Number_of_Claims DESC;
    """
    result_12 = pd.read_sql(query_12, conn)
    st.dataframe(result_12)

    fig12, ax12 = plt.subplots(figsize=(6, 6))
    ax12.pie(result_12['Number_of_Claims'], labels=result_12['Meal_Type'], autopct='%1.1f%%', startangle=90)
    ax12.set_title('Percentage of Food Claims by Meal Type')
    st.pyplot(fig12)

elif analysis_option == 'Total Quantity of Food Donated by Each Provider':
    st.subheader('Q13: Total Quantity of Food Donated by Each Provider')
    query_13 = """
    SELECT T1.Name, SUM(T2.Quantity) AS Total_Quantity
    FROM provider_data AS T1
    JOIN food_listings_data AS T2 ON T1.Provider_ID = T2.Provider_ID
    WHERE 1=1
    """
    if selected_provider_type != 'All':
        query_13 += f" AND T1.Type = '{selected_provider_type}'"
    if selected_food_type != 'All':
        query_13 += f" AND T2.Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_13 += f" AND T2.Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_13 += f" AND T2.Location = '{selected_location}'"

    query_13 += """
    GROUP BY T1.Name ORDER BY Total_Quantity DESC;
    """
    result_13 = pd.read_sql(query_13, conn)
    st.dataframe(result_13)

    st.subheader('Top 20 Providers by Total Quantity Donated')
    fig13, ax13 = plt.subplots(figsize=(12, 7))
    sns.barplot(x='Name', y='Total_Quantity', data=result_13.head(20), ax=ax13)
    plt.title('Top 20 Providers by Total Quantity Donated')
    plt.xlabel('Provider Name')
    plt.ylabel('Total Quantity')
    plt.xticks(rotation=90)
    plt.tight_layout()
    st.pyplot(fig13)

elif analysis_option == 'Number of Food Listings and Claims Over Time':
    st.subheader('Q15: Number of Food Listings and Claims Over Time')
    query_15 = """
    SELECT
        strftime('%Y-%m-%d', T1.Timestamp) AS Date,
        COUNT(T1.Claim_ID) AS Number_of_Claims,
        0 AS Number_of_Listings
    FROM claims_data AS T1
    JOIN food_listings_data AS T2 ON T1.Food_ID = T2.Food_ID
    JOIN receivers_data AS T3 ON T1.Receiver_ID = T3.Receiver_ID
    WHERE 1=1
    """
    if selected_status != 'All':
        query_15 += f" AND T1.Status = '{selected_status}'"
    if selected_receiver_type != 'All':
        query_15 += f" AND T3.Type = '{selected_receiver_type}'"
    if selected_food_type != 'All':
        query_15 += f" AND T2.Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_15 += f" AND T2.Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_15 += f" AND T2.Location = '{selected_location}'"

    query_15 += """
    GROUP BY Date

    UNION ALL

    SELECT
        strftime('%Y-%m-%d', T1.Expiry_Date) AS Date,
        0 AS Number_of_Claims,
        COUNT(T1.Food_ID) AS Number_of_Listings
    FROM food_listings_data AS T1
    JOIN provider_data AS T2 ON T1.Provider_ID = T2.Provider_ID
    WHERE 1=1
    """
    if selected_provider_type != 'All':
        query_15 += f" AND T2.Type = '{selected_provider_type}'"
    if selected_food_type != 'All':
        query_15 += f" AND T1.Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_15 += f" AND T1.Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_15 += f" AND T1.Location = '{selected_location}'"

    query_15 += """
    GROUP BY Date
    ORDER BY Date;
    """
    result_15 = pd.read_sql(query_15, conn)
    st.dataframe(result_15)

    fig15, ax15 = plt.subplots(figsize=(15, 6))
    sns.lineplot(x='Date', y='Number_of_Claims', data=result_15, label='Number of Claims', ax=ax15)
    sns.lineplot(x='Date', y='Number_of_Listings', data=result_15, label='Number of Listings', ax=ax15)
    plt.title('Number of Food Listings and Claims Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Listings/Claims')
    plt.xticks(rotation=90)
    ax15.legend()
    st.pyplot(fig15)

elif analysis_option == 'Number of Food Claims by Status Over Time':
    st.subheader('Number of Food Claims by Status Over Time')
    query_claims_status_time = """
    SELECT
        strftime('%Y-%m-%d', T1.Timestamp) AS Date,
        T1.Status,
        COUNT(T1.Claim_ID) AS Number_of_Claims
    FROM claims_data AS T1
    JOIN food_listings_data AS T2 ON T1.Food_ID = T2.Food_ID
    JOIN receivers_data AS T3 ON T1.Receiver_ID = T3.Receiver_ID
    WHERE 1=1
    """
    if selected_status != 'All':
        query_claims_status_time += f" AND T1.Status = '{selected_status}'"
    if selected_receiver_type != 'All':
        query_claims_status_time += f" AND T3.Type = '{selected_receiver_type}'"
    if selected_food_type != 'All':
        query_claims_status_time += f" AND T2.Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_claims_status_time += f" AND T2.Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_claims_status_time += f" AND T2.Location = '{selected_location}'"

    query_claims_status_time += """
    GROUP BY Date, T1.Status
    ORDER BY Date, T1.Status;
    """
    claims_status_time_result = pd.read_sql(query_claims_status_time, conn)
    st.dataframe(claims_status_time_result)

    fig_claims_status, ax_claims_status = plt.subplots(figsize=(15, 6))
    sns.lineplot(x='Date', y='Number_of_Claims', hue='Status', data=claims_status_time_result, ax=ax_claims_status)
    plt.title('Number of Food Claims by Status Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Claims')
    plt.xticks(rotation=90)
    ax_claims_status.legend(title='Status')
    st.pyplot(fig_claims_status)

elif analysis_option == 'Number of Food Listings by Provider Type Over Time':
    st.subheader('Number of Food Listings by Provider Type Over Time')
    query_listings_provider_time = """
    SELECT
        strftime('%Y-%m-%d', T1.Expiry_Date) AS Date,
        T1.Provider_Type,
        COUNT(T1.Food_ID) AS Number_of_Listings
    FROM food_listings_data AS T1
    JOIN provider_data AS T2 ON T1.Provider_ID = T2.Provider_ID
    WHERE 1=1
    """
    if selected_provider_type != 'All':
        query_listings_provider_time += f" AND T1.Provider_Type = '{selected_provider_type}'"
    if selected_food_type != 'All':
        query_listings_provider_time += f" AND T1.Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_listings_provider_time += f" AND T1.Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_listings_provider_time += f" AND T1.Location = '{selected_location}'"

    query_listings_provider_time += """
    GROUP BY Date, T1.Provider_Type
    ORDER BY Date, T1.Provider_Type;
    """
    listings_provider_time_result = pd.read_sql(query_listings_provider_time, conn)
    st.dataframe(listings_provider_time_result)

    fig_listings_provider, ax_listings_provider = plt.subplots(figsize=(15, 6))
    sns.lineplot(x='Date', y='Number_of_Listings', hue='Provider_Type', data=listings_provider_time_result, ax=ax_listings_provider)
    plt.title('Number of Food Listings by Provider Type Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Listings')
    plt.xticks(rotation=90)
    ax_listings_provider.legend(title='Provider Type')
    st.pyplot(fig_listings_provider)


elif analysis_option == 'Total Quantity Donated by Provider (Top 20)':
    st.subheader('Total Quantity Donated by Provider (Top 20)')
    query_18 = """
    SELECT T1.Name, SUM(T2.Quantity) AS Total_Quantity
    FROM provider_data AS T1
    JOIN food_listings_data AS T2 ON T1.Provider_ID = T2.Provider_ID
    WHERE 1=1
    """
    if selected_provider_type != 'All':
        query_18 += f" AND T1.Type = '{selected_provider_type}'"
    if selected_food_type != 'All':
        query_18 += f" AND T2.Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_18 += f" AND T2.Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_18 += f" AND T2.Location = '{selected_location}'"
    query_18 += """
    GROUP BY T1.Name ORDER BY Total_Quantity DESC LIMIT 20;
    """
    result_18 = pd.read_sql(query_18, conn)
    st.dataframe(result_18)

    fig18, ax18 = plt.subplots(figsize=(12, 7))
    sns.barplot(x='Name', y='Total_Quantity', data=result_18, ax=ax18)
    plt.title('Top 20 Providers by Total Quantity Donated')
    plt.xlabel('Provider Name')
    plt.ylabel('Total Quantity')
    plt.xticks(rotation=90)
    plt.tight_layout()
    st.pyplot(fig18)

elif analysis_option == 'Total Quantity Claimed by Receiver (Top 20)':
    st.subheader('Total Quantity Claimed by Receiver (Top 20)')
    query_19 = """
    SELECT
        T2.Name AS Receiver_Name,
        SUM(T3.Quantity) AS Total_Quantity
    FROM claims_data AS T1
    JOIN receivers_data AS T2 ON T1.Receiver_ID = T2.Receiver_ID
    JOIN food_listings_data AS T3 ON T1.Food_ID = T3.Food_ID
    WHERE 1=1
    """
    if selected_status != 'All':
        query_19 += f" AND T1.Status = '{selected_status}'"
    if selected_receiver_type != 'All':
        query_19 += f" AND T2.Type = '{selected_receiver_type}'"
    if selected_food_type != 'All':
        query_19 += f" AND T3.Food_type = '{selected_food_type}'"
    if selected_meal_type != 'All':
        query_19 += f" AND T3.Meal_Type = '{selected_meal_type}'"
    if selected_location != 'All':
        query_19 += f" AND T3.Location = '{selected_location}'"
    query_19 += """
    GROUP BY T2.Name
    ORDER BY Total_Quantity DESC
    LIMIT 20;
    """
    result_19 = pd.read_sql(query_19, conn)
    st.dataframe(result_19)

    fig19, ax19 = plt.subplots(figsize=(12, 7))
    sns.barplot(x='Receiver_Name', y='Total_Quantity', data=result_19, ax=ax19)
    plt.title('Top 20 Receivers by Total Quantity Claimed')
    plt.xlabel('Receiver Name')
    plt.ylabel('Total Quantity')
    plt.xticks(rotation=90)
    plt.tight_layout()
    st.pyplot(fig19)


# Close the connection
conn.close()
