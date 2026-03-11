import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.0.4", layout="wide")
st.markdown("<style>.stApp { background: #010101; color: #ffffff; }</style>", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
def get_market_data(ticker, interval="5m"):
    try:
        df = yf.download(ticker, period="5d", interval=interval, progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        # Technical Indicators
        df['RSI'] = ta.rsi(df.Close, length=14)
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        
        # Fair Value Gaps (FVG) Detection
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) 
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1))
        
        return df
    except:
        return None

# --- 3. SIDEBAR CONTROLS ---
st.title("🌌 PATRO AI PRO V12.0.4 | SMC ULTIMATE")

with st.sidebar:
    st.header("🏢 COMMAND CENTER")
    asset = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset]
    
    st.divider()
    mode = st.toggle("🚀 AGGRESSIVE MODE", value=False)
    
    st.divider()
    st.subheader("📡 LIVE NEWS ALERTS")
    # Updated News for March 11, 2026
    st.error("🚨 CPI DATA: US Inflation report out at 8:30 AM ET today. Markets will spike!")
    st.warning("⚔️ GEOPOLITICS: Pentagon promises 'intense' strikes despite Trump comments.")
    st.info("📉 OIL: Below $90/bbl, pulling some safe-haven premium from Gold.")

# --- 4. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    df_5m = get_market_data(target_ticker, "5m")
    df_1h = get_market_data(target_ticker, "1h")
    
    if df_5m is None or len(df_5m) < 20:
        st.error("Searching for Bank Liquidity...")
        return

    # --- LOGIC CALCULATIONS (Combined) ---
    bias_1h = "BULLISH" if df_1h.Close.iloc[-1] > df_1h.VWAP.iloc[-1] else "BEARISH"
    curr_sig = "BUY" if df_5m.Close.iloc[-1] > df_5m.VWAP.iloc[-1] else "SELL"
    
    # 2-Minute Confirmation (Checks if the last 2 candles held above/below VWAP)
    confirmed = False
    if curr_sig == "BUY":
        confirmed = df_5m.Close.iloc[-1] > df_5m.VWAP.iloc[-1] and df_5m.Close.iloc[-2] > df_5m.VWAP.iloc[-2]
    else:
        confirmed = df_5m.Close.iloc[-1] < df_5m.VWAP.iloc[-1] and df_5m.Close.iloc[-2] < df_5m.VWAP.iloc[-2]

    bank_vol = df_5m.Volume.iloc[-1] > (df_5m.Volume.tail(20).mean() * 1.5)
    
    # Trend Strength Calculation (Updated with 2-Min Confirmation)
    strength = 0
    if (curr_sig == "BUY" and df_5m.RSI.iloc[-1] > 50) or (curr_sig == "SELL" and df_5m.RSI.iloc[-1] < 50): strength += 20
    if (curr_sig == "BUY" and bias_1h == "BULLISH") or (curr_sig == "SELL" and bias_1h == "BEARISH"): strength += 30
    if bank_vol: strength += 20
    if confirmed: strength += 30 # Added 30% for 2-minute consistency

    # SIGNAL UI
    if mode:
        status, col = f"🚀 SCALP {curr_sig}", ("#00FF88" if curr_sig == "BUY" else "#FF3366")
    else:
        is_sure = (bias_1h == curr_sig.replace("BUY","BULLISH").replace("SELL","BEARISH")) and confirmed
        status = f"🏦 BANK {curr_sig} (SURE)" if is_sure else "⌛ WAIT (RETAIL TRAP)"
        col = ("#00FF88" if curr_sig == "BUY" else "#FF3366") if is_sure else "#FFA500"

    # Top Metrics
    m1, m2, m3 = st.columns([2, 1, 1])
    m1.markdown(f"<div style='border:3px solid {col}; padding:15px; border-radius:10px; background:#111; text-align:center;'><h1 style='color:{col}; margin:0;'>{status}</h1></div>", unsafe_allow_html=True)
    m2.metric("PRICE", f"{df_5m.Close.iloc[-1]:,.2f}")
    m3.metric("STRENGTH", f"{strength}%")

    st.progress(strength / 100)
    
    if strength < 60: 
        st.warning("⚠️ Low Strength: Market is currently 'sideways' or filling gaps. Avoid large lots.")
    elif strength >= 80:
        st.success("🔥 HIGH CONVICTION: Institutions are moving. Look for entry in the Boxes.")

    # --- THE CHART ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df_5m.index, open=df_5m.Open, high=df_5m.High, low=df_5m.Low, close=df_5m.Close, name="Price"))
    fig.add_trace(go.Scatter(x=df_5m.index, y=df_5m.VWAP, line=dict(color='cyan', dash='dot', width=1), name="VWAP"))

    # BOX DETECTION (FVG)
    boxes = 0
    for i in range(1, len(df_5m) - 1):
        if df_5m['FVG_Up'].iloc[i]: # Bullish Box
            fig.add_shape(type="rect", x0=df_5m.index[i-1], x1=df_5m.index[i+1], y0=df_5m['High'].iloc[i-1], y1=df_5m['Low'].iloc[i+1],
                          fillcolor="rgba(0, 255, 136, 0.4)", line=dict(color="#00FF88", width=1))
            boxes += 1
        if df_5m['FVG_Down'].iloc[i]: # Bearish Box
            fig.add_shape(type="rect", x0=df_5m.index[i-1], x1=df_5m.index[i+1], y0=df_5m['Low'].iloc[i-1], y1=df_5m['High'].iloc[i+1],
                          fillcolor="rgba(255, 51, 102, 0.4)", line=dict(color="#FF3366", width=1))
            boxes += 1

    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    if boxes > 0:
        st.success(f"🎯 {boxes} Safety Boxes found. Only enter if price touches these zones.")
    else:
        st.info("💡 Efficiency Mode: No gaps found. Price is moving smoothly.")

render_app()
