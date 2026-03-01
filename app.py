import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. Page Config
st.set_page_config(page_title="PATRO AI PRO | Terminal", layout="wide")
st_autorefresh(interval=30000, key="patroupdate")

# Custom CSS for that Pro Sidebar look
st.markdown("""
    <style>
    .trend-box { padding: 10px; border-radius: 5px; border: 1px solid #4CAF50; color: #4CAF50; font-weight: bold; margin-bottom: 8px; text-align: center; }
    .buy-mode { background: linear-gradient(90deg, #00c853 0%, #b2ff59 100%); padding: 15px; border-radius: 10px; color: black; font-weight: bold; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

st.sidebar.divider()
st.sidebar.subheader("📊 TREND MATRIX")
st.sidebar.markdown('<div class="trend-box">1M: UP</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="trend-box">5M: UP</div>', unsafe_allow_html=True)

if st.sidebar.button("🔄 FULL SYSTEM REFRESH"):
    st.rerun()

# 3. Main Dashboard Data
st.markdown('<div class="buy-mode">🛡️ PATRO AI PRO | INSTITUTIONAL TERMINAL</div>', unsafe_allow_html=True)

df = yf.download("^DJI", period="1d", interval=tf, group_by='column')

if not df.empty:
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Indicators
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    
    # RSI Fix
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))

    # Create Subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])

    # Add Candles
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='Trend', line=dict(color='orange', width=1)), row=1, col=1)

    # --- THE SIGNAL LOOP (Every Candle) ---
    # This loop checks every row and adds a BUY or SELL label
    for i in range(len(df)):
        current_close = df['Close'].iloc[i]
        current_sma = df['SMA_20'].iloc[i]
        
        if not pd.isna(current_sma): # Only add signals if we have enough data
            if current_close > current_sma:
                # Add BUY Signal above candle
                fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="BUY", showarrow=False, 
                                   font=dict(color="#00FF00", size=8), yshift=10, row=1, col=1)
            else:
                # Add SELL Signal below candle
                fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="SELL", showarrow=False, 
                                   font=dict(color="#FF4B4B", size=8), yshift=-10, row=1, col=1)

    # RSI Line
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple', width=2)), row=2, col=1)
    
    fig.update_layout(template="plotly_dark", height=800, xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Market Data Offline")
