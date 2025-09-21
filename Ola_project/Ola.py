import streamlit as st
import pandas as pd
import sqlite3 as sql
import matplotlib.pyplot as plt
import seaborn as sns
import os # Import the os module

# Function to connect to the database and run queries
def run_query(query):
    conn = sql.connect('ola_database.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Load the data (assuming the database is already created and populated)
try:
    # Check if the database file exists
    db_file = 'ola_database.db'
    if not os.path.exists(db_file):
        st.error(f"Database file '{db_file}' not found. Please ensure the database is created and in the same directory as the Streamlit app.")
    else:
        conn = sql.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ola_data';")
        table_exists = cursor.fetchone() is not None
        conn.close()

        if not table_exists:
            st.error("Database table 'ola_data' not found within the database file. Please run the notebook cells to create and populate the database.")
        else:
            st.title('OLA Data Analysis Dashboard')

            # 1. Overall
            with st.expander("1. Overall Analysis"):
                st.subheader('Ride Volume Over Time (Daily)')
                ride_volume_query = "SELECT DATE(Date) as Ride_Date, COUNT(*) as Ride_Count FROM ola_data GROUP BY Ride_Date ORDER BY Ride_Date"
                ride_volume_df = run_query(ride_volume_query)
                st.line_chart(ride_volume_df.set_index('Ride_Date'))

                st.subheader('Booking Status Breakdown')
                booking_status_query = "SELECT Booking_Status, COUNT(*) as Count FROM ola_data GROUP BY Booking_Status"
                booking_status_df = run_query(booking_status_query)
                fig, ax = plt.subplots()
                ax.pie(booking_status_df['Count'], labels=booking_status_df['Booking_Status'], autopct='%1.1f%%', startangle=90)
                ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
                st.pyplot(fig)


            # 2. Vehicle Type
            with st.expander("2. Vehicle Type Analysis"):
                st.subheader('Average Ride Distance by Vehicle Type')
                avg_ride_distance_query = "SELECT Vehicle_Type, AVG(Ride_Distance) AS Avg_Ride_Distance FROM ola_data GROUP BY Vehicle_Type"
                avg_ride_distance_df = run_query(avg_ride_distance_query)
                st.bar_chart(avg_ride_distance_df.set_index('Vehicle_Type'))

            # 3. Revenue
            with st.expander("3. Revenue Analysis"):
                st.subheader('Total Booking Value of Successful Rides')
                total_booking_value_query = "SELECT SUM(Booking_Value) AS Total_Booking_Value FROM ola_data WHERE Booking_Status = 'Success'"
                total_booking_value_df = run_query(total_booking_value_query)
                st.write(f"Total Booking Value for Successful Rides: ₹{total_booking_value_df['Total_Booking_Value'].iloc[0]:,.2f}")

                st.subheader('Revenue by Payment Method (for Successful Rides)')
                revenue_by_payment_query = "SELECT Payment_Method, SUM(Booking_Value) AS Total_Revenue FROM ola_data WHERE Booking_Status = 'Success' GROUP BY Payment_Method"
                revenue_by_payment_df = run_query(revenue_by_payment_query)
                st.bar_chart(revenue_by_payment_df.set_index('Payment_Method'))

                st.subheader('Top 5 Customers by Ride Count')
                top_customers_query = "SELECT Customer_ID, COUNT(*) AS Ride_Count FROM ola_data GROUP BY Customer_ID ORDER BY Ride_Count DESC LIMIT 5"
                top_customers_df = run_query(top_customers_query)
                st.dataframe(top_customers_df)


            # 4. Cancellation
            with st.expander("4. Cancellation Analysis"):
                st.subheader('Total Cancelled Rides by Customer')
                total_cancelled_customer_query = "SELECT COUNT(*) AS Total_Cancelled_Rides FROM ola_data WHERE Booking_Status = 'Canceled by Customer'"
                total_cancelled_customer_df = run_query(total_cancelled_customer_query)
                st.write(f"Total Rides Cancelled by Customer: {total_cancelled_customer_df['Total_Cancelled_Rides'].iloc[0]}")

                st.subheader('Cancellation Reasons by Customer')
                cancelled_reasons_customer_query = "SELECT Canceled_Rides_by_Customer, COUNT(*) as Count FROM ola_data WHERE Booking_Status = 'Canceled by Customer' GROUP BY Canceled_Rides_by_Customer"
                cancelled_reasons_customer_df = run_query(cancelled_reasons_customer_query)
                st.dataframe(cancelled_reasons_customer_df)


                st.subheader('Total Cancelled Rides by Driver')
                total_cancelled_driver_query = "SELECT COUNT(*) AS Total_Cancelled_Rides FROM ola_data WHERE Booking_Status = 'Canceled by Driver'"
                total_cancelled_driver_df = run_query(total_cancelled_driver_query)
                st.write(f"Total Rides Cancelled by Driver: {total_cancelled_driver_df['Total_Cancelled_Rides'].iloc[0]}")


                st.subheader('Cancellation Reasons by Driver')
                cancelled_reasons_driver_query = "SELECT Canceled_Rides_by_Driver, COUNT(*) as Count FROM ola_data WHERE Booking_Status = 'Canceled by Driver' GROUP BY Canceled_Rides_by_Driver"
                cancelled_reasons_driver_df = run_query(cancelled_reasons_driver_query)
                st.dataframe(cancelled_reasons_driver_df)


            # 5. Ratings
            with st.expander("5. Ratings Analysis"):
                st.subheader('Average Driver Rating by Vehicle Type')
                avg_driver_rating_query = "SELECT Vehicle_Type, AVG(Driver_Ratings) AS Avg_Driver_Rating FROM ola_data GROUP BY Vehicle_Type"
                avg_driver_rating_df = run_query(avg_driver_rating_query)
                st.bar_chart(avg_driver_rating_df.set_index('Vehicle_Type'))


                st.subheader('Average Customer Rating by Vehicle Type')
                avg_customer_rating_query = "SELECT Vehicle_Type, AVG(Customer_Rating) AS Avg_Customer_Rating FROM ola_data GROUP BY Vehicle_Type"
                avg_customer_rating_df = run_query(avg_customer_rating_query)
                st.bar_chart(avg_customer_rating_df.set_index('Vehicle_Type'))


except Exception as e:
    st.error(f"An error occurred: {e}")
