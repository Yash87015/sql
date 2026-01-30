import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
import numpy as np

# Databricks connector - optional for production
# If you want to use Databricks, uncomment below and add to requirements.txt:
# from databricks.sql import connect
# DATABRICKS_AVAILABLE = True
DATABRICKS_AVAILABLE = False

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SafeFlow | Fraud Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS STYLING ---
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 24px;
    }
    .stAlert {
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- CONNECT TO DATABRICKS (SECURELY) ---
# This uses Streamlit Secrets. DO NOT hardcode keys here.
@st.cache_data(ttl=3600) # Cache data for 1 hour to speed up app
def get_data(query):
    if DATABRICKS_AVAILABLE and "DATABRICKS_SERVER" in st.secrets:
        try:
            connection = connect(
                server_hostname = st.secrets["DATABRICKS_SERVER"],
                http_path       = st.secrets["DATABRICKS_HTTP_PATH"],
                access_token    = st.secrets["DATABRICKS_TOKEN"]
            )
            cursor = connection.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
            connection.close()
            return df
        except Exception as e:
            st.error(f"⚠️ Connection Error: {e}")
            return get_sample_data(query)
    else:
        return get_sample_data(query)

def get_sample_data(query):
    """Return sample data for testing/demo purposes"""
    
    # Sample daily fraud data
    if "gold_daily_fraud" in query:
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        df = pd.DataFrame({
            'Date': dates,
            'Total_Transactions': np.random.randint(8000, 15000, len(dates)),
            'Fraud_Cases': np.random.randint(100, 500, len(dates))
        })
        return df
    
    # Sample A/B test results
    elif "gold_ab_test" in query:
        return pd.DataFrame({
            'Experiment_Group': ['Control', 'Variant'],
            'Fraud_Rate_Percent': [2.45, 2.38]
        })
    
    # Sample fraud by category
    elif "gold_fraud_by_category" in query:
        return pd.DataFrame({
            'Merchant_Category': ['Electronics', 'Jewelry', 'Travel', 'Groceries', 'Entertainment'],
            'Fraud_Rate': [12.5, 11.3, 8.7, 2.1, 3.4],
            'Fraud_Cases': [450, 380, 290, 70, 115]
        })
    
    # Sample fraud by city
    elif "gold_fraud_by_city" in query:
        return pd.DataFrame({
            'User_City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'],
            'Fraud_Cases': [250, 210, 190, 160, 140, 130, 120, 110, 105, 95],
            'Fraud_Rate': [3.2, 2.8, 2.5, 2.1, 1.9, 1.8, 1.7, 1.6, 1.5, 1.4]
        })
    
    return pd.DataFrame()

# --- SIDEBAR INFO ---
with st.sidebar:
    st.title("🛡️ SafeFlow")
    st.markdown("End-to-End Banking Fraud Detection System")
    st.divider()
    st.info("**Project Status:** Live")
    st.caption("Last Updated: Just Now")
    st.caption("Data Source: Databricks Delta Lake (Gold Layer)")
    
    st.divider()
    st.markdown("[View Source Code](https://github.com/your-username/your-repo)")

# --- MAIN DASHBOARD LOGIC ---
st.title("🛡️ Executive Fraud Monitor")
st.markdown("Real-time monitoring of transaction anomalies and ML model performance.")

# 1. LOAD DATA
with st.spinner("Fetching Analytics from Databricks..."):
    # We fetch all necessary tables at once
    df_daily = get_data("SELECT * FROM gold_daily_fraud ORDER BY Date")
    df_ab = get_data("SELECT * FROM gold_ab_test_results")
    df_cat = get_data("SELECT * FROM gold_fraud_by_category ORDER BY Fraud_Rate DESC LIMIT 5")
    df_city = get_data("SELECT * FROM gold_fraud_by_city ORDER BY Fraud_Rate DESC LIMIT 10")

# 2. KPI METRICS ROW
if not df_daily.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    total_txns = df_daily['Total_Transactions'].sum()
    total_fraud = df_daily['Fraud_Cases'].sum()
    avg_fraud_rate = (total_fraud / total_txns) * 100
    last_date = pd.to_datetime(df_daily['Date']).max().strftime('%b %d, %Y')
    
    col1.metric("Total Transactions", f"{total_txns:,.0f}")
    col2.metric("Fraud Cases Detected", f"{total_fraud:,.0f}", delta_color="inverse")
    col3.metric("Global Fraud Rate", f"{avg_fraud_rate:.2f}%")
    col4.metric("Last Sync", last_date)

    st.divider()

    # 3. TABS FOR DETAILED ANALYSIS
    tab_overview, tab_ml, tab_ab, tab_geo = st.tabs(["📊 Business Overview", "🤖 ML Model Insights", "🧪 A/B Testing", "🌍 Geospatial Risk"])

    # --- TAB 1: BUSINESS OVERVIEW ---
    with tab_overview:
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("Daily Fraud Trends")
            # Using Plotly for interactive charts
            fig_trend = px.line(df_daily, x='Date', y='Fraud_Cases', title='Fraud Volume Over Time', markers=True)
            fig_trend.update_layout(xaxis_title="Date", yaxis_title="Fraud Cases")
            st.plotly_chart(fig_trend, use_container_width=True)
            
        with c2:
            st.subheader("High-Risk Sectors")
            if not df_cat.empty:
                st.dataframe(
                    df_cat[['Merchant_Category', 'Fraud_Rate']],
                    column_config={
                        "Fraud_Rate": st.column_config.ProgressColumn(
                            "Risk Level",
                            format="%.2f%%",
                            min_value=0,
                            max_value=15, # Based on your logic (Electronics ~15%)
                        )
                    },
                    hide_index=True,
                )
            else:
                st.warning("No category data found.")

    # --- TAB 2: ML MODEL INSIGHTS ---
    with tab_ml:
        st.subheader("XGBoost Classifier Performance")
        st.markdown("Model trained on **500,000+** records using **SMOTE** for class imbalance.")
        
        # Hardcoded metrics from your Databricks run (Notebook 05)
        # This keeps the dashboard fast without loading the heavy model file
        m1, m2, m3 = st.columns(3)
        m1.metric("ROC-AUC Score", "0.78", "Good Baseline")
        m2.metric("Recall (Fraud Catch Rate)", "71%", "High Impact")
        m3.metric("Precision", "24%", "Optimization Target")
        
        st.divider()
        
        st.subheader("What drives fraud?")
        st.caption("Top predictors identified by the model (Feature Importance)")
        
        # Hardcoded from your Notebook 05 result
        feature_data = {
            "Feature": ["Electronics (Category)", "Jewelry (Category)", "Travel (Category)", "Transaction Amount", "Age"],
            "Importance": [0.38, 0.37, 0.14, 0.05, 0.03]
        }
        df_feat = pd.DataFrame(feature_data)
        fig_feat = px.bar(df_feat, x="Importance", y="Feature", orientation='h', title="Top Fraud Predictors")
        st.plotly_chart(fig_feat, use_container_width=True)

    # --- TAB 3: A/B TESTING ---
    with tab_ab:
        st.subheader("Experiment: New Fraud Rules (Variant) vs Baseline (Control)")
        
        if not df_ab.empty:
            # Calculate Rates
            control_data = df_ab[df_ab['Experiment_Group'] == 'Control']
            variant_data = df_ab[df_ab['Experiment_Group'] == 'Variant']
            
            c_rate = control_data['Fraud_Rate_Percent'].values[0] if not control_data.empty else 0
            v_rate = variant_data['Fraud_Rate_Percent'].values[0] if not variant_data.empty else 0
            
            # Display Result
            col_a, col_b = st.columns(2)
            col_a.metric("Control Group Fraud Rate", f"{c_rate:.2f}%")
            col_b.metric("Variant Group Fraud Rate", f"{v_rate:.2f}%", f"{(c_rate-v_rate):.2f}% Diff")
            
            # The "Senior Engineer" Insight
            st.info("""
            **Recommendation: DO NOT ROLL OUT** Although the Variant group shows a slight difference, statistical analysis (Chi-Square) returned a **P-Value of 0.85**, 
            indicating the result is **Not Statistically Significant**. 
            
            *Action Item:* Gather more data or refine the rule logic before production deployment.
            """)
        else:
            st.warning("A/B Test data not available.")

    # --- TAB 4: GEOSPATIAL RISK ---
    with tab_geo:
        st.subheader("Geographic Risk Hotspots")
        if not df_city.empty:
            st.markdown("Cities with the highest fraud frequency.")
            
            # Bar chart for cities
            fig_city = px.bar(
                df_city, 
                x="User_City", 
                y="Fraud_Cases", 
                color="Fraud_Rate",
                title="Fraud Volume by City (Color = Risk Rate)"
            )
            st.plotly_chart(fig_city, use_container_width=True)
            
            with st.expander("View Raw City Data"):
                st.dataframe(df_city)

else:
    st.error("""
    **Connection Failed or No Data Found.** 1. Check your Streamlit Secrets configuration.
    2. Ensure the Databricks cluster is RUNNING.
    3. Verify Gold Tables exist in Databricks.
    """)
