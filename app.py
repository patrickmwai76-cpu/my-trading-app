import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Setup & Auto-Refresh (Updates every 30 seconds)
st.set_page_config(page_title="PATRO AI PRO", layout="wide")
st_autorefresh(interval=30000, key="patro_live")

# 2. Main Terminal Header
st.markdown('<h1 style="text-align:center; color:#00ffcc;">🛡️ PATRO AI | SIGNAL TERMINAL</h1>', unsafe_allow_html=True)

# 3. Fetching Data (Fixing the Yahoo Finance Error)
df = yf.download("^DJI", period="1d", interval="1m")

# Clean the data columns (Important fix for the 'Error' you had)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

if not df.empty:
    # Calculate the Signal Baseline (20-period Moving Average)
    df['MA20'] = df['Close'].rolling(window=20).mean()
    
    current_price = df['Close'].iloc[-1]
    current_ma = df['MA20'].iloc[-1]

    # --- THE CHART ---
    fig = go.Figure()

    # Add Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='US30'
    ))

    # Add the Signal Line (Moving Average)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='AI Trend', line=dict(color='orange', width=1)))

    # 4. Logic for the Buy (B) and Sell (S) Signals
    if current_price > current_ma:
        # BUY SIGNAL: Place a Green 'B' below the candle
        fig.add_annotation(
            x=df.index[-1], y=df['Low'].iloc[-1],
            text="B", showarrow=True, arrowhead=1,
            arrowcolor="#00ff00", bgcolor="#00ff00",
            font=dict(color="black", size=14), ay=40
        )
        st.success(f"🚀 AI SIGNAL: BUY MODE | Price: ${current_price:,.2f}")
    else:
        # SELL SIGNAL: Place a Red 'S' above the candle
        fig.add_annotation(
            x=df.index[-1], y=df['High'].iloc[-1],
            text="S", showarrow=True, arrowhead=1,
            arrowcolor="#ff0000", bgcolor="#ff0000",
            font=dict(color="white", size=14), ay=-40
        )
        st.error(f"📉 AI SIGNAL: SELL MODE | Price: ${current_price:,.2f}")

    # Chart Styling
    fig.update_layout(
        template="plotly_dark",
        height=600,
        xaxis_rangeslider_visible=False,
        yaxis=dict(side="right"),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 5. Sidebar Tools (SOP & Risk)
    st.sidebar.title("🛠️ OPERATOR SOP")
    st.sidebar.checkbox("Is the 'B' or 'S' showing?")
    st.sidebar.checkbox("Is the News Clear?")
    
    st.sidebar.divider()
    st.sidebar.subheader("📉 LOT CALCULATOR")
    bal = st.sidebar.number_input("Balance", value=1000)
    risk = st.sidebar.slider("Risk %", 1, 5, 1)
    st.sidebar.info(f"Recommended Lot: {(bal * (risk/100)) / 50:.2f}")

else:
    st.error("Market Data Connection Lost. Retrying...")
