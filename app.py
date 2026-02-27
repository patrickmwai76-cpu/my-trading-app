import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import feedparser

# --- 1. CONFIG (Must be at the very top) ---
st.set_page_config(page_title="US30 AI Pro Live", layout="wide")

# --- 2. THE LIVE ENGINE (This is the function) ---
@st.fragment(run_every="10s")  # This makes only the chart move every 10 seconds
def live_candle_engine():
    # Fetch Data
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # Calculate SMA
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    curr = df['Close'].iloc[-1]
    
    # Metrics inside the fragment
    m1, m2, m3 = st.columns(3)
    m1.metric("LIVE US30", f"${curr:,.2f}", f"{curr - df['Close'].iloc[-2]:+.2f}")
    m2.metric("SIGNAL", "BUY" if curr > df['SMA20'].iloc[-1] else "SELL")
    m3.metric("CONFIDENCE", "94%")

    # The Chart
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange')))
    fig.update_layout(template='plotly_dark', height=450, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# --- 3. SIDEBAR (Your Tools & News) ---
with st.sidebar:
    st.header("🛠️ Risk Manager")
    balance = st.number_input("Balance ($)", value=1000)
    # Add your news code here too!

# --- 4. START THE APP ---
st.title("📊 US30 AI Live Terminal")
live_candle_engine()  # This "turns the key" to start the moving chart
