import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. THE "NO-TRAP" ENGINE ---
def get_safe_data(ticker, tf="1m"):
    try:
        df = yf.download(ticker, period="5d", interval=tf, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index)
        return df
    except:
        return pd.DataFrame()

# --- 2. INTERFACE SETUP ---
st.set_page_config(page_title="PATRO AI PRO V11.6", layout="wide")
st.markdown("<style>.stApp { background: #050505; color: white; }</style>", unsafe_allow_html=True)

with st.sidebar:
    st.title("🌌 PATRO V11.6")
    asset_map = {"GOLD": "GC=F", "GBPUSD": "GBPUSD=X", "US30": "^DJI"}
    choice = st.selectbox("Asset", list(asset_map.keys()))
    ticker = asset_map[choice]
    
    st.divider()
    st.write("🛡️ **ANTI-FAKE FILTERS**")
    vol_mult = st.slider("Volume Multiplier", 1.0, 3.0, 1.5)
    atr_filter = st.checkbox("Volatility Gate (ATR)", value=True)

# --- 3. MAIN LOGIC ---
@st.fragment(run_every="7s")
def patro_engine():
    df = get_safe_data(ticker)
    if not df.empty and len(df) > 30:
        # Calculate Base Indicators
        df['VWAP'] = ta.vwap(high=df['High'], low=df['Low'], close=df['Close'], volume=df['Volume'])
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
        df['VOL_SMA'] = df['Volume'].rolling(20).mean()
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 🛡️ FILTER 1: Volume Confirmation (Institutional Footprint)
        has_volume = last['Volume'] > (last['VOL_SMA'] * vol_mult)
        
        # 🛡️ FILTER 2: Volatility Gate (Prevent Choppy Trades)
        is_volatile = last['ATR'] > df['ATR'].rolling(20).mean().iloc[-1] if atr_filter else True
        
        # 🛡️ FILTER 3: Momentum Direction (RSI Trend)
        is_bullish = last['Close'] > last['VWAP'] and last['RSI'] > 55
        is_bearish = last['Close'] < last['VWAP'] and last['RSI'] < 45

        # --- FINAL SIGNAL DECISION ---
        signal = "⌛ SCANNING..."
        status_color = "gray"

        if is_bullish and has_volume and is_volatile:
            signal = "🚀 STRONG BUY"
            status_color = "#00FF88"
        elif is_bearish and has_volume and is_volatile:
            signal = "📉 STRONG SELL"
            status_color = "#FF3366"
        elif (is_bullish or is_bearish) and not has_volume:
            signal = "⚠️ FAKE OUT (LOW VOL)"
            status_color = "#FFA500"

        # UI DASHBOARD
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div style="text-align:center; padding:10px; border:2px solid {status_color}; border-radius:10px;">SIGNAL<br><h2 style="color:{status_color};">{signal}</h2></div>', unsafe_allow_html=True)
        m2.metric("VOL STRENGTH", f"{round(last['Volume']/last['VOL_SMA'], 1)}x")
        m3.metric("RSI", int(last['RSI']))

        # CHARTING
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2])
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='orange', width=2), name="VWAP"), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color=status_color), row=2, col=1)
        fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

patro_engine()
