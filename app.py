import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.1.14", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #fff; }</style>", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
def get_market_data(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="5m", progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # SMC & Trend Logic
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14)
        
        # FVG Detection
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) 
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1))
        return df.dropna()
    except: return None

# --- 3. SIDEBAR (Full Features Restored) ---
with st.sidebar:
    st.header("🏢 SMC COMMAND")
    asset = st.selectbox("Market", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    
    st.divider()
    st.subheader("💰 RISK MGT")
    bal = st.number_input("Balance", 1000)
    risk = st.slider("Risk %", 1, 5, 2)
    st.warning(f"Stop Loss: ${bal * (risk/100):.2f}")
    
    st.divider()
    st.subheader("📡 NEWS STREAM")
    st.error("🚨 US CPI Impact: HIGH")

# --- 4. THE CHART ---
@st.fragment(run_every="15s")
def render_app():
    df = get_market_data(ticker_map[asset])
    if df is None: return

    cp = df.Close.iloc[-1]
    vwap = df.VWAP.iloc[-1]
    atr = df.ATR.iloc[-1]
    
    # State Logic (Background & Label Sync)
    buffer = atr * 0.5
    if cp > (vwap + buffer):
        state, col, bg = "SURE BUY", "#00FF88", "rgba(0, 255, 136, 0.05)"
    elif cp < (vwap - buffer):
        state, col, bg = "SURE SELL", "#FF3366", "rgba(255, 51, 102, 0.05)"
    else:
        state, col, bg = "WAITING", "#FFA500", "rgba(255, 165, 0, 0.05)"

    # Dashboard Metric
    st.markdown(f"<div style='border:2px solid {col}; padding:15px; border-radius:15px; background:#111; text-align:center;'><h1 style='color:{col}; margin:0; font-family:monospace;'>{state} | {cp:,.2f}</h1></div>", unsafe_allow_html=True)

    fig = go.Figure()

    # 1. Background Zone (TikTok Visuals)
    fig.add_vrect(x0=df.index[0], x1=df.index[-1], fillcolor=col, opacity=0.04, layer="below", line_width=0)

    # 2. Candlesticks (High Contrast)
    fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, 
                                 increasing_line_color='#00FF88', decreasing_line_color='#FF3366', name="Price"))

    # 3. SMC Boxes (FVG Liquidity)
    for i in range(len(df)-20, len(df)-1):
        if df['FVG_Up'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df.High.iloc[i-1], y1=df.Low.iloc[i+1], 
                          fillcolor="rgba(0, 255, 136, 0.2)", line_width=1, line_color="rgba(0, 255, 136, 0.4)")
        if df['FVG_Down'].iloc[i]:
            fig.add_shape(type="rect", x0=df.index[i-1], x1=df.index[i+1], y0=df.Low.iloc[i-1], y1=df.High.iloc[i+1], 
                          fillcolor="rgba(255, 51, 102, 0.2)", line_width=1, line_color="rgba(255, 51, 102, 0.4)")

    # 4. Signal Marker (The Floating Word)
    fig.add_trace(go.Scatter(x=[df.index[-1]], y=[cp], mode="text+markers", 
                             text=[f"<b>{state}</b>"], textposition="top right",
                             marker=dict(color=col, size=15, symbol="diamond"),
                             textfont=dict(color=col, size=18), name="Signal"))

    # 5. Styling & Layout
    fig.update_layout(height=700, template="plotly_dark", paper_bgcolor="black", plot_bgcolor="black", 
                      xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    
    st.plotly_chart(fig, use_container_width=True, theme=None, key="pro_scalper_v14")

    # 6. History Table
    st.subheader("📜 SIGNAL HISTORY")
    st.table(pd.DataFrame([{"Time": datetime.now().strftime("%H:%M"), "Asset": asset, "Signal": state, "Price": cp}]))

render_app()
