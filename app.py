import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="Velocity Market Decoder", layout="wide")

# --- Data Loading ---
@st.cache_data
def load_all_data():
    if not pd.io.common.file_exists('market_data.csv'):
        return pd.DataFrame()
    df = pd.read_csv('market_data.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df_raw = load_all_data()

# --- Level Calculation Engine ---
def get_market_levels():
    nifty = yf.Ticker("^NSEI")
    hist = nifty.history(period="2d")
    current_price = hist['Close'].iloc[-1]
    prev_close = hist['Close'].iloc[-2]
    # Simple ATR-based volatility levels for levels
    range_val = (hist['High'].iloc[-1] - hist['Low'].iloc[-1])
    return round(current_price), round(prev_close), round(range_val)

spot, prev_close, mkt_range = get_market_levels()

# --- UI Header ---
st.title("🏹 Velocity Market Decoder")
st.subheader(f"Nifty Spot: {spot} | Trend Bias: {'BULLISH' if spot > prev_close else 'BEARISH'}")

# --- Analysis Logic ---
if not df_raw.empty:
    latest_date = df_raw['Date'].max()
    today_data = df_raw[df_raw['Date'] == latest_date]
    
    fii = today_data[today_data['Client Type'] == 'FII'].iloc[0]
    pro = today_data[today_data['Client Type'] == 'Pro'].iloc[0]
    retail = today_data[today_data['Client Type'] == 'Client'].iloc[0]

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("FII Call Positioning", f"{fii['Net Index Call']:,}", delta="Smart Money")
        st.write("Bias: Strong Sell" if fii['Net Index Call'] < 0 else "Bias: Accumulation")

    with col2:
        st.metric("Retail Put Exposure", f"{retail['Net Index Put']:,}", delta="Dumb Money", delta_color="inverse")
        st.write("Trap Alert!" if retail['Net Index Put'] > 50000 else "Neutral")

    # --- Prediction Chart ---
    st.markdown("### 📈 Tomorrow's Movement Prediction")
    
    # Logic: If FII Net Call is -ve and Retail is +ve = SELL ON RISE
    if fii['Net Index Call'] < 0 and retail['Net Index Call'] > 0:
        prediction = "Sell on Rise"
        levels = [spot + (mkt_range*0.5), spot - mkt_range]
        color = "red"
    else:
        prediction = "Buy on Dip"
        levels = [spot - (mkt_range*0.5), spot + mkt_range]
        color = "green"

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1, 2, 3], y=[prev_close, levels[0], levels[1], levels[1]-50], 
                             line=dict(color=color, width=4, dash='dot'), name="Projected Path"))
    fig.update_layout(title=f"Predicted Movement: {prediction}", xaxis_title="Market Hours", yaxis_title="Nifty Level")
    st.plotly_chart(fig, use_container_width=True)

    # --- Support & Resistance Levels ---
    st.markdown("### 🛡️ Critical Decision Levels")
    c1, c2, c3, c4 = st.columns(4)
    c1.error(f"Resistance 2: {spot + mkt_range}")
    c2.warning(f"Resistance 1: {spot + (mkt_range*0.5)}")
    c3.success(f"Support 1: {spot - (mkt_range*0.5)}")
    c4.info(f"Support 2: {spot - mkt_range}")

else:
    st.error("Please run the GitHub Harvester to populate data.")
