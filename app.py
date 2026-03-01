import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

# 1. Page Config
st.set_page_config(page_title="PATRO AI PRO | Terminal", layout="wide")
st_autorefresh(interval=30000, key="patroupdate")

# 2. Sidebar Controls
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

if st.sidebar.button("🔄 REFRESH SYSTEM"):
    st.rerun()

# 3. Fetch Data
df = yf.download("^DJI", period="1d", interval=tf, group_by='column')

if not df.empty:
    # Fix Multi-Index Column Names
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Indicators
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    
    # RSI Calculation
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))

    # 4. Create Subplots (Price on Row 1, RSI on Row 2)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])

    # ADD CANDLESTICKS FIRST (This makes them the base layer)
    fig.add_trace(go.Candlestick(
        x=df.index, 
        open=df['Open'], 
        high=df['High'], 
        low=df['Low'], 
        close=df['Close'], 
        name='US30'
    ), row=1, col=1)

    # ADD TREND LINE
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='Trend', line=dict(color='orange', width=1.5)), row=1, col=1)

    # --- ADD LABELS WITHOUT HIDING CANDLES ---
    # We only add labels for the last 50 candles to keep the chart fast and visible
    recent_df = df.tail(50) 
    for i in range(len(recent_df)):
        curr_price = recent_df['Close'].iloc[i]
        curr_sma = recent_df['SMA_20'].iloc[i]
        
        if not pd.isna(curr_sma):
            if curr_price > curr_sma:
                fig.add_annotation(x=recent_df.index[i], y=recent_df['High'].iloc[i], text="B", showarrow=False, 
                                   font=dict(color="#00FF00", size=10), yshift=15, row=1, col=1)
            else:
                fig.add_annotation(x=recent_df.index[i], y=recent_df['Low'].iloc[i], text="S", showarrow=False, 
                                   font=dict(color="#FF4B4B", size=10), yshift=-15, row=1, col=1)

    # RSI Line (Bottom Row)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#a020f0', width=2)), row=2, col=1)
    
    # Layout Fixes
    fig.update_layout(
        template="plotly_dark", 
        height=800, 
        xaxis_rangeslider_visible=False, 
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Market data is currently unavailable.")
