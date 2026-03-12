import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime
import os

st.set_page_config(page_title="Velocity Market Decoder", layout="wide")

# --- 1. Robust Data Loading ---
def load_data():
    # Use direct filename since it's in the same root folder
    file_path = 'market_data.csv'
    
    if not os.path.exists(file_path):
        st.error(f"❌ '{file_path}' not found in the repository.")
        return pd.DataFrame()

    df = pd.read_csv(file_path)
    
    # Check if file is empty (only headers)
    if df.empty or len(df) < 2:
        st.warning("⚠️ Data file found but it's empty. Run the GitHub Action to fetch today's data.")
        return pd.DataFrame()

    # Clean up Column Names (NSE often adds extra spaces)
    df.columns = df.columns.str.strip()
    
    # Fix Date Column
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    
    return df

df_raw = load_data()

# --- 2. Market Context Engine ---
def get_live_context():
    try:
        nifty = yf.Ticker("^NSEI")
        hist = nifty.history(period="2d")
        if not hist.empty:
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2]
            rng = (hist['High'].iloc[-1] - hist['Low'].iloc[-1])
            return round(current), round(prev), round(rng)
    except:
        return 24000, 23900, 200 # Fallback values
    return 24000, 23900, 200

spot, prev_close, mkt_range = get_live_context()

# --- 3. The Dashboard Interface ---
st.title("🏹 Velocity Market Decoder")
st.write(f"**Last Analysis Sync:** {datetime.now().strftime('%Y-%m-%d %H:%M')} IST")

if not df_raw.empty:
    # Filter for the most recent data entry
    latest_date = df_raw['Date'].max()
    today_data = df_raw[df_raw['Date'] == latest_date]
    
    # Participant Extraction
    try:
        fii = today_data[today_data['Client Type'] == 'FII'].iloc[0]
        pro = today_data[today_data['Client Type'] == 'Pro'].iloc[0]
        retail = today_data[today_data['Client Type'] == 'Client'].iloc[0]
    except IndexError:
        st.error("Could not find FII/Retail rows. Check CSV format.")
        st.stop()

    # Metrics Display
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("FII Net Index Fut", f"{int(fii['Net Index Fut']):,}")
        st.caption("Positive = Bullish Conviction")
    with c2:
        st.metric("Retail Net Calls", f"{int(retail['Net Index Call']):,}")
        st.caption("High Positive = Potential Trap")
    with c3:
        st.metric("Nifty Spot", f"{spot}", delta=f"{round(spot-prev_close, 2)}")

    # --- Prediction Chart ---
    st.markdown("### 📈 Tomorrow's Projected Movement")
    
    # Logic: Decode if Smart Money is against Retail
    # If FII is Short and Retail is Long = Bearish
    is_bearish = fii['Net Index Fut'] < 0 or fii['Net Index Call'] < 0
    pred_path = [spot, spot - (mkt_range*0.3), spot - (mkt_range*0.8)] if is_bearish else [spot, spot + (mkt_range*0.3), spot + (mkt_range*0.8)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=['Open', 'Mid-Day', 'Closing'], y=pred_path, 
                             line=dict(color='red' if is_bearish else 'green', width=4, dash='dot'),
                             mode='lines+markers+text', text=[f"Start: {spot}", "Pivot", "Target"], textposition="top center"))
    
    fig.update_layout(yaxis=dict(range=[spot-mkt_range, spot+mkt_range]))
    st.plotly_chart(fig, use_container_width=True)

    # --- Historical Trend (The part that caused the error) ---
    st.markdown("### 📊 FII Momentum Trend")
    # We create a specific dataframe for the chart so there are no KeyErrors
    trend_df = df_raw[df_raw['Client Type'] == 'FII'][['Date', 'Net Index Fut']].copy()
    if not trend_df.empty:
        st.line_chart(trend_df.set_index('Date'))

else:
    st.info("Waiting for data. Please ensure 'market_data.csv' in GitHub has at least 2 rows of data.")
