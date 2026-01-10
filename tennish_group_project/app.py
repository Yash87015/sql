import streamlit as st
import pandas as pd
import sqlite3 as sql
import os
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

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
