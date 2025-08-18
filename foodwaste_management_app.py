
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

st.subheader('Provider Data')
st.dataframe(pd.read_sql("SELECT * FROM provider_data LIMIT 5", conn))
st.write(pd.read_sql("SELECT sql FROM sqlite_master WHERE name='provider_data'", conn).iloc[0, 0])


st.subheader('Receivers Data')
st.dataframe(pd.read_sql("SELECT * FROM receivers_data LIMIT 5", conn))
st.write(pd.read_sql("SELECT sql FROM sqlite_master WHERE name='receivers_data'", conn).iloc[0, 0])


st.subheader('Food Listings Data')
st.dataframe(pd.read_sql("SELECT * FROM food_listings_data LIMIT 5", conn))
st.write(pd.read_sql("SELECT sql FROM sqlite_master WHERE name='food_listings_data'", conn).iloc[0, 0])


st.subheader('Claims Data')
st.dataframe(pd.read_sql("SELECT * FROM claims_data LIMIT 5", conn))
st.write(pd.read_sql("SELECT sql FROM sqlite_master WHERE name='claims_data'", conn).iloc[0, 0])


# --- Analysis and Visualizations ---
st.header('Analysis and Visualizations')

# Q1 How many food providers and receivers are there in each city?
st.subheader('Q1: Number of Food Providers and Receivers in Each City')
query_1 = """
SELECT
    T1.City,
    COUNT(DISTINCT T1.Provider_ID) AS Number_of_Providers,
    COUNT(DISTINCT T2.Receiver_ID) AS Number_of_Receivers
FROM provider_data AS T1
LEFT JOIN receivers_data AS T2 ON T1.City = T2.City
GROUP BY T1.City;
"""
result_1 = pd.read_sql(query_1, conn)
st.dataframe(result_1)

# Visualize the top 20 cities
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


# Q2 Which type of food provider (restaurant, grocery store, etc.) contributes the most food?
st.subheader('Q2: Percentage of Food Providers by Type')
query_2 = """
SELECT
    Type,
    COUNT(*) AS Number_of_Providers
FROM provider_data
GROUP BY Type
ORDER BY Number_of_Providers DESC;
"""
result_2 = pd.read_sql(query_2, conn)
st.dataframe(result_2)

fig2, ax2 = plt.subplots(figsize=(6, 6))
ax2.pie(result_2['Number_of_Providers'], labels=result_2['Type'], autopct='%1.1f%%', startangle=90)
ax2.set_title('Percentage of Food Providers by Type')
st.pyplot(fig2)

# Q3 What is the contact information of food providers in a specific city?
st.subheader('Q3: Contact Information of Food Providers in a Specific City')
city_query = "SELECT DISTINCT City FROM provider_data ORDER BY City;"
cities = pd.read_sql(city_query, conn)['City'].tolist()
selected_city = st.selectbox('Select a city for Provider Contact Information:', cities)

query_3 = f"""
SELECT
    Name,
    Contact,
    Type
FROM provider_data
WHERE City = '{selected_city}';
"""
result_3 = pd.read_sql(query_3, conn)
st.write(f"Food Providers in {selected_city}:")
st.dataframe(result_3)


# Q4 Which receivers have claimed the most food?
st.subheader('Q4: Receivers with the Most Claims')
query_4 = """
SELECT Name, COUNT(*) AS Number_of_Claims
FROM receivers_data
JOIN claims_data ON receivers_data.Receiver_ID = claims_data.Receiver_ID
GROUP BY Name
ORDER BY Number_of_Claims DESC;
"""
result_4 = pd.read_sql(query_4, conn)
st.dataframe(result_4)

st.subheader('Top 20 Receivers by Number of Claims')
fig4, ax4 = plt.subplots(figsize=(12, 7)) # Adjusted figsize
sns.barplot(x='Name', y='Number_of_Claims', data=result_4.head(20), ax=ax4) # Limiting to top 20 for better visualization
plt.title('Top 20 Receivers by Number of Claims')
plt.xlabel('Receiver Name')
plt.ylabel('Number of Claims')
plt.xticks(rotation=90)
plt.tight_layout()
st.pyplot(fig4)

# Receivers with highest quantity claimed status = completed
st.subheader('Receivers with the Most Completed Claims')
extra_query2 = """
SELECT Name, COUNT(*) AS Number_of_Claims
FROM receivers_data
JOIN claims_data ON receivers_data.Receiver_ID = claims_data.Receiver_ID
WHERE Status = 'Completed'
GROUP BY Name
ORDER BY Number_of_Claims DESC;
"""
extra_result2 = pd.read_sql(extra_query2, conn)
st.dataframe(extra_result2)

st.subheader('Top 20 Receivers by Number of Completed Claims')
fig_extra2, ax_extra2 = plt.subplots(figsize=(12, 7)) # Adjusted figsize
sns.barplot(x='Name', y='Number_of_Claims', data=extra_result2.head(20), ax=ax_extra2) # Limiting to top 20
plt.title('Top 20 Receivers by Number of Completed Claims')
plt.xlabel('Receiver Name')
plt.ylabel('Number of Completed Claims')
plt.xticks(rotation=90)
plt.tight_layout()
st.pyplot(fig_extra2)

# Q5 What is the total quantity of food available from all providers?
st.subheader('Q5: Total Quantity of Food Available from All Providers')
query_5 = """
SELECT SUM(Quantity) AS Total_Quantity
FROM food_listings_data;
"""
result_5 = pd.read_sql(query_5, conn)
st.dataframe(result_5)

# Q6 Which location has the highest number of food listings?
st.subheader('Q6: Location with the Highest Number of Food Listings')
query_6 = """
SELECT Location, COUNT(*) AS Number_of_Listings
FROM food_listings_data
GROUP BY Location
ORDER BY Number_of_Listings DESC
LIMIT 1;
"""
result_6 = pd.read_sql(query_6, conn)
st.dataframe(result_6)

# Which city has the highest number of food listings ?
st.subheader('Cities with the Highest Number of Food Listings (Top 20)')
query_Extra = """
SELECT City, COUNT(*) AS Number_of_Listings
FROM provider_data
GROUP BY City
ORDER BY Number_of_Listings DESC
LIMIT 20;
"""
result_Extra = pd.read_sql(query_Extra, conn)
st.dataframe(result_Extra)

# Q7 What are the most commonly available food types?
st.subheader('Q7: Most Commonly Available Food Types')
query_7 = """
SELECT Food_type, COUNT(*) AS Number_of_Listings
FROM food_listings_data
GROUP BY Food_type
ORDER BY Number_of_Listings DESC;
"""
result_7 = pd.read_sql(query_7, conn)
st.dataframe(result_7)

# Q8 How many food claims have been made for each food item?
st.subheader('Q8: Number of Food Claims for Each Food Item')
query_8 = """
SELECT
    T1.Food_ID,
    T2.Food_Name,
    COUNT(T1.Claim_ID) AS Number_of_Claims
FROM claims_data AS T1
JOIN food_listings_data AS T2 ON T1.Food_ID = T2.Food_ID
GROUP BY T1.Food_ID, T2.Food_Name
ORDER BY Number_of_Claims DESC;
"""
result_8 = pd.read_sql(query_8, conn)
st.dataframe(result_8)

st.subheader('Top 20 Food Items by Number of Claims')
fig8, ax8 = plt.subplots(figsize=(12, 7)) # Adjusted figsize
sns.barplot(x='Food_Name', y='Number_of_Claims', data=result_8.head(20), ax=ax8) # Limiting to top 20
plt.title('Top 20 Food Items by Number of Claims')
plt.xlabel('Food Item')
plt.ylabel('Number of Claims')
plt.xticks(rotation=90)
plt.tight_layout()
st.pyplot(fig8)


# Q9 Which provider has had the highest number of successful food claims?
st.subheader('Q9: Providers with the Highest Number of Successful Food Claims (Top 20)')
query_9 = """
SELECT T2.Name, COUNT(T1.Claim_ID) AS Number_of_Claims
FROM claims_data AS T1
JOIN food_listings_data AS T3 ON T1.Food_ID = T3.Food_ID
JOIN provider_data AS T2 ON T3.Provider_ID = T2.Provider_ID
WHERE T1.Status = 'Completed'
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


# Q10 What percentage of food claims are completed vs. pending vs. canceled?
st.subheader('Q10: Percentage of Food Claims by Status')
query_10 = """
SELECT
    Status,
    COUNT(*) AS Number_of_Claims,
    (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims_data)) AS Percentage
FROM claims_data
GROUP BY Status;
"""
result_10 = pd.read_sql(query_10, conn)
st.dataframe(result_10)

fig10, ax10 = plt.subplots(figsize=(6, 6))
ax10.pie(result_10['Number_of_Claims'], labels=result_10['Status'], autopct='%1.1f%%', startangle=90)
ax10.set_title('Percentage of Food Claims by Status')
st.pyplot(fig10)

# Q11 What is the average quantity of food claimed per receiver?
st.subheader('Q11: Average Quantity of Food Claimed per Receiver')
query_11 = """
SELECT
    T2.Name AS Receiver_Name,
    AVG(T3.Quantity) AS Average_Quantity
FROM claims_data AS T1
JOIN receivers_data AS T2 ON T1.Receiver_ID = T2.Receiver_ID
JOIN food_listings_data AS T3 ON T1.Food_ID = T3.Food_ID
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


# Q12 Which meal type (breakfast, lunch, dinner, snacks) is claimed the most?
st.subheader('Q12: Percentage of Food Claims by Meal Type')
query_12 = """
SELECT Meal_Type, COUNT(*) AS Number_of_Claims
FROM food_listings_data
JOIN claims_data ON food_listings_data.Food_ID = claims_data.Food_ID
GROUP BY Meal_Type
ORDER BY Number_of_Claims DESC;
"""
result_12 = pd.read_sql(query_12, conn)
st.dataframe(result_12)

fig12, ax12 = plt.subplots(figsize=(6, 6))
ax12.pie(result_12['Number_of_Claims'], labels=result_12['Meal_Type'], autopct='%1.1f%%', startangle=90)
ax12.set_title('Percentage of Food Claims by Meal Type')
st.pyplot(fig12)

# Q13 What is the total quantity of food donated by each provider?
st.subheader('Q13: Total Quantity of Food Donated by Each Provider')
query_13 = """
SELECT T1.Name, SUM(T2.Quantity) AS Total_Quantity
FROM provider_data AS T1
JOIN food_listings_data AS T2 ON T1.Provider_ID = T2.Provider_ID
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

# Q14 Examine how the number of food listings and claims changes over time.
st.subheader('Q14: Number of Food Listings and Claims Over Time')
query_14 = """
SELECT
    strftime('%Y-%m-%d', Timestamp) AS Date,
    COUNT(Claim_ID) AS Number_of_Claims,
    0 AS Number_of_Listings
FROM claims_data
GROUP BY Date

UNION ALL

SELECT
    strftime('%Y-%m-%d', Expiry_Date) AS Date,
    0 AS Number_of_Claims,
    COUNT(Food_ID) AS Number_of_Listings
FROM food_listings_data
GROUP BY Date
ORDER BY Date;
"""
result_14 = pd.read_sql(query_14, conn)
st.dataframe(result_14)

fig15, ax15 = plt.subplots(figsize=(15, 6))
sns.lineplot(x='Date', y='Number_of_Claims', data=result_14, label='Number of Claims', ax=ax15)
sns.lineplot(x='Date', y='Number_of_Listings', data=result_14, label='Number of Listings', ax=ax15)
plt.title('Number of Food Listings and Claims Over Time')
plt.xlabel('Date')
plt.ylabel('Number of Listings/Claims')
plt.xticks(rotation=90)
ax15.legend()
st.pyplot(fig15)

# Analyze the status of claims over time
st.subheader('Number of Food Claims by Status Over Time')
query_claims_status_time = """
SELECT
    strftime('%Y-%m-%d', Timestamp) AS Date,
    Status,
    COUNT(Claim_ID) AS Number_of_Claims
FROM claims_data
GROUP BY Date, Status
ORDER BY Date, Status;
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

# Analyze listings by provider type over time
st.subheader('Number of Food Listings by Provider Type Over Time')
query_listings_provider_time = """
SELECT
    strftime('%Y-%m-%d', Expiry_Date) AS Date,
    Provider_Type,
    COUNT(Food_ID) AS Number_of_Listings
FROM food_listings_data
GROUP BY Date, Provider_Type
ORDER BY Date, Provider_Type;
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


# Total donated quantity by provider with highest 20
st.subheader('Total Quantity Donated by Provider (Top 20)')
query_18 = """
SELECT T1.Name, SUM(T2.Quantity) AS Total_Quantity
FROM provider_data AS T1
JOIN food_listings_data AS T2 ON T1.Provider_ID = T2.Provider_ID
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

# Q19 Receivers with highest quantity claimed
st.subheader('Total Quantity Claimed by Receiver (Top 20)')
query_19 = """
SELECT
    T2.Name AS Receiver_Name,
    SUM(T3.Quantity) AS Total_Quantity
FROM claims_data AS T1
JOIN receivers_data AS T2 ON T1.Receiver_ID = T2.Receiver_ID
JOIN food_listings_data AS T3 ON T1.Food_ID = T3.Food_ID
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
