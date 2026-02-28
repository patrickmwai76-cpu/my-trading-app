import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. SETUP ---
st.set_page_config(page_title="US30 AI Pro Terminal", layout="wide")

st.markdown("""
    <style>
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .live-dot { height: 12px; width: 12px; background-color: #00ff00; border-radius: 50%; display: inline-block; animation: pulse 1.5s infinite; margin-right: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_pro_data():
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # SMA Calculation
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    
    # RSI Calculation (The 14-minute Scale)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Signal Logic
    df['Signal'] = 0
    df.loc[df['Close'] > df['SMA20'], 'Signal'] = 1
    df.loc[df['Close'] < df['SMA20'], 'Signal'] = -1
    df['Entry'] = df['Signal'].diff()
    return df

# --- 3. MAIN DASHBOARD ---
try:
    df = get_pro_data()
    curr_price = df['Close'].iloc[-1]
    curr_rsi = df['RSI'].iloc[-1]
    last_sig = "BUY" if df['Signal'].iloc[-1] == 1 else "SELL"

    st.markdown(f'## <span class="live-dot"></span> US30 AI LIVE TERMINAL: {last_sig}', unsafe_allow_html=True)

    # Top Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("US30 PRICE", f"${curr_price:,.2f}")
    c2.metric("SIGNAL", last_sig)
    c3.metric("RSI (14)", f"{curr_rsi:.2f}", "Overbought" if curr_rsi > 70 else "Oversold" if curr_rsi < 30 else "Neutral")

    # --- 4. MULTI-SCALE CHART (Candles + RSI) ---
    # This creates the two rows: top for candles, bottom for RSI
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_heights=[0.7, 0.3])

    # Row 1: Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], 
        low=df['Low'], close=df['Close'], name='Price'
    ), row=1, col=1)
    
    # Add SMA 20
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='SMA 20', line=dict(color='orange', width=1)), row=1, col=1)

    # Row 2: RSI Scale
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=2, col=1)
    # Add RSI Overbought/Oversold levels
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)

    # Add Buy/Sell Labels on Candles
    for i in range(1, len(df)):
        if df['Entry'].iloc[i] == 2:
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", font=dict(color="white"), ay=20, row=1, col=1)
        elif df['Entry'].iloc[i] == -2:
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", font=dict(color="white"), ay=-20, row=1, col=1)

    fig.update_layout(template='plotly_dark', height=700, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Waiting for market data... {e}")

# Sidebar Controls
with st.sidebar:
    st.header("Controls")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
