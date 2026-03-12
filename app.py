import streamlit as st
import pandas as pd
import os

# --- Load Data Logic ---
def load_latest_data():
    file_path = 'market_data.csv'
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    df = pd.read_csv(file_path)
    if df.empty:
        return pd.DataFrame()
    
    # Ensure columns are clean
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Always sort by date so the 'latest' is truly the last working day
    df = df.sort_values(by='Date', ascending=False)
    return df

df_all = load_latest_data()

if not df_all.empty:
    # Get the single most recent date available in the CSV
    latest_date = df_all['Date'].iloc[0]
    today_display = latest_date.strftime('%A, %b %d, %Y')
    
    st.title("🏹 Velocity Market Decoder")
    st.info(f"📅 Showing Analysis for Last Working Day: **{today_display}**")
    
    # Use only data from that latest date
    latest_df = df_all[df_all['Date'] == latest_date]
    
    # ... (Rest of your Metrics and Prediction Chart code from previous app.py) ...
    # (Just ensure you are referencing 'latest_df' instead of 'today_data')
    
else:
    st.error("No data found in market_data.csv. Please run the GitHub Action.")
