import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Velocity Market Decoder", layout="wide")

# --- 1. Data Loading ---
def load_data():
    file_path = 'market_data.csv'
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'])
    return df.sort_values(by='Date', ascending=False)

df = load_data()

# --- 2. UI Header ---
st.title("🏹 Velocity Market Decoder")

if not df.empty:
    latest_date = df['Date'].iloc[0]
    st.info(f"📅 Showing Analysis for Last Working Day: **{latest_date.strftime('%A, %b %d, %Y')}**")
    
    # Filter for just the latest day's data
    day_data = df[df['Date'] == latest_date]
    
    # Extract Specific Participants
    try:
        fii = day_data[day_data['Client Type'] == 'FII'].iloc[0]
        retail = day_data[day_data['Client Type'] == 'Client'].iloc[0]
        pro = day_data[day_data['Client Type'] == 'Pro'].iloc[0]
        
        # --- 3. Key Metrics Rows ---
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("FII Net Index Fut", f"{int(fii['Net Index Fut']):,}")
            st.caption("Institutions: Positive is Bullish")
            
        with col2:
            st.metric("Retail Net Calls", f"{int(retail['Net Index Call']):,}")
            st.caption("Retail: High Positive is often a Trap")
            
        with col3:
            # Simple Sentiment Logic
            sentiment = "BULLISH" if fii['Net Index Fut'] > 0 else "BEARISH"
            color = "green" if sentiment == "BULLISH" else "red"
            st.markdown(f"**Trend Bias:** :{color}[{sentiment}]")

        # --- 4. Prediction Visualization ---
        st.subheader("📈 Projected Market Momentum")
        
        # Logic: If FIIs are Short and Retail is Long, predict a dip
        is_bearish = fii['Net Index Fut'] < 0
        path = [100, 90, 70] if is_bearish else [100, 110, 130]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=['Open', 'Mid-Day', 'Close'], 
            y=path,
            line=dict(color='red' if is_bearish else 'green', width=4, dash='dot'),
            mode='lines+markers'
        ))
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20), yaxis_title="Momentum %")
        st.plotly_chart(fig, use_container_width=True)
        
        # --- 5. Data Table ---
        with st.expander("View Raw Decoded Data"):
            st.dataframe(day_data[['Client Type', 'Net Index Fut', 'Net Index Call', 'Net Index Put']])

    except Exception as e:
        st.error(f"Error parsing participant data: {e}")
        st.write("Current CSV Content:", day_data)

else:
    st.warning("⚠️ No data found in market_data.csv. Please run the GitHub Action.")
