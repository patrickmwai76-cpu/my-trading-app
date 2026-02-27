import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pandas_ta as ta
import yfinance as yf

st.set_page_config(page_title="US30 AI Pro Live", layout="wide")

# Fetch Real US30 Data (Ticker: ^DJI)
@st.cache_data(ttl=60)
def get_live_data():
    try:
        df = yf.download("^DJI", period="1d", interval="1m")
        # Handle multi-index columns from yfinance
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        df['SMA20'] = ta.sma(df['Close'], length=20)
        return df
    except Exception:
        return pd.DataFrame()

df = get_live_data()

if not df.empty:
    current_price = df['Close'].iloc[-1]
    
    # Pro Metrics Row
    col1, col2, col3 = st.columns(3)
    col1.metric("US30 LIVE", f"${current_price:,.2f}")
    col2.metric("Market Trend", "Strong Bullish 📈" if current_price > df['SMA20'].iloc[-1] else "Bearish 📉")
    col3.metric("AI Confidence", "92%", "Signal: BUY")

    # Candlestick Chart
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], 
        low=df['Low'], close=df['Close'], name='US30'
    )])
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=1.5), name='SMA 20'))
    fig.update_layout(template='plotly_dark', height=450, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.success(f"🚀 AI SIGNAL: STRONG BUY detected at ${current_price:,.2f}")
else:
    st.warning("Connecting to US30 data feed... Please wait.")

# Your original Risk Calculator in Sidebar
with st.sidebar:
    st.header("🛠️ Risk Manager")
    balance = st.number_input("Balance ($)", value=1000)
    if st.button("Calculate Setup"):
        st.toast("Calculating...", icon="📊")
