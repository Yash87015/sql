import streamlit as st
import pandas as pd
import sqlite3 as sql
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
