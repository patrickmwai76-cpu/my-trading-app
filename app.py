import streamlit as st
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CORE CONFIG ---
st.set_page_config(page_title="PATRO AI PRO V12.0.5", layout="wide")
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
        df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=14) # Added for TP/SL math
        
        # Fair Value Gaps (FVG) Detection - Fixed Logic
        df['FVG_Up'] = (df['Low'].shift(-1) > df['High'].shift(1)) 
        df['FVG_Down'] = (df['High'].shift(-1) < df['Low'].shift(1))
        
        return df
    except:
        return None

# --- 3. SIDEBAR CONTROLS ---
st.title("🌌 PATRO AI PRO V12.0.5 | SMC ULTIMATE")

with st.sidebar:
    st.header("🏢 COMMAND CENTER")
    asset = st.selectbox("Market Target", ["GOLD", "GBPUSD", "US30"])
    ticker_map = {"GOLD":"GC=F", "GBPUSD":"GBPUSD=X", "US30":"^DJI"}
    target_ticker = ticker_map[asset]
    
    st.divider()
    mode = st.toggle("🚀 AGGRESSIVE MODE", value=False)
    
    st.divider()
    st.subheader("📡 LIVE NEWS ALERTS")
    st.error("🚨 CPI DATA: US Inflation report out at 8:30 AM ET today. Markets will spike!")
    st.warning("⚔️ GEOPOLITICS: Pentagon confirms intense strikes. Watch Gold volatility.")
    st.info("📉 OIL: Pulling back, providing a floor for Gold at $5,180.")

# --- 4. LIVE DASHBOARD ---
@st.fragment(run_every="15s")
def render_app():
    df_5m = get_market_data(target_ticker, "5m")
    df_1h = get_market_data(target_ticker, "1h")
    
    if df_5m is None or len(df_5m) < 20:
        st.error("Searching for Bank Liquidity...")
        return

    # --- LOGIC CALCULATIONS ---
    cp = df_5m.Close.iloc[-1]
    atr = df_5m.ATR.iloc[-1]
    bias_1h = "BULLISH" if df_1h.Close.iloc[-1] > df_1h.VWAP.iloc[-1] else "BEARISH"
    curr_sig = "BUY" if cp > df_5m.VWAP.iloc[-1] else "SELL"
    
    # 2-Minute Confirmation
    confirmed = df_5m.Close.iloc[-1] > df_5m.VWAP.iloc[-1] and df_5m.Close.iloc[-2] > df_5m.VWAP.iloc[-2] if curr_sig == "BUY" else df_5m.Close.iloc[-1] < df_5m.VWAP.iloc[-1] and df_5m.Close.iloc[-2] < df_5m.VWAP.iloc[-2]

    # Institutional TP/SL Calculation
    sl_dist = atr * 1.5
    tp_dist = sl_dist * 2.0
    bank_tp = cp + tp_dist if curr_sig == "BUY" else cp - tp_dist
    bank_sl = cp - sl_dist if curr_sig == "BUY" else cp + sl_dist

    # Trend Strength
    strength = 0
    if (curr_sig == "BUY" and df_5m.RSI.iloc[-1] > 50) or (curr_sig == "SELL" and df_5m.RSI.iloc[-1] < 50): strength += 30
    if (curr_sig == "BUY" and bias_1h == "BULLISH") or (curr_sig == "SELL" and bias_1h == "BEARISH"): strength += 40
    if confirmed: strength += 30

    # SIGNAL UI
    is_sure = (bias_1h == curr_sig.replace("BUY","BULLISH").replace("SELL","BEARISH")) and confirmed
    status = f"🏦 BANK {curr_sig} (SURE)" if is_sure else "⌛ WAIT (RETAIL TRAP)"
    col = ("#00FF88" if curr_sig == "BUY" else "#FF3366") if is_sure else "#FFA500"

    # Top Metrics
    m1, m2, m3 = st.columns([2, 1, 1])
    m1.markdown(f"<div style='border:3px solid {col}; padding:15px; border-radius:10px; background:#111; text-align:center;'><h1 style='color:{col}; margin:0;'>{status}</h1></div>", unsafe_allow_html=True)
    m2.metric("PRICE", f"{cp:,.2f}")
    m3.metric("STRENGTH", f"{strength}%")

    st.progress(strength / 100)

    # --- THE CHART ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df_5m.index, open=df_5m.Open, high=df_5m.High, low=df_5m.Low, close=df_5m.Close, name="Price"))
    fig.add_trace(go.Scatter(x=df_5m.index, y=df_5m.VWAP, line=dict(color='cyan', dash='dot', width=1), name="VWAP"))

    # BANK ENTRY & TP/SL LINES
    fig.add_hline(y=bank_tp, line_dash="dash", line_color="#00FF88", annotation_text="INSTITUTIONAL TP", annotation_position="top right")
    fig.add_hline(y=bank_sl, line_dash="dash", line_color="#FF3366", annotation_text="BANK STOP LOSS", annotation_position="bottom right")

    # FIXING BOX DETECTION (FVG)
    boxes = 0
    # We look back at the last 50 candles to find the most recent "Safety Boxes"
    for i in range(len(df_5m)-50, len(df_5m)-2):
        if df_5m['FVG_Up'].iloc[i]: # Bullish Box
            fig.add_shape(type="rect", x0=df_5m.index[i-1], x1=df_5m.index[i+1], y0=df_5m['High'].iloc[i-1], y1=df_5m['Low'].iloc[i+1],
                          fillcolor="rgba(0, 255, 136, 0.2)", line=dict(width=0))
            boxes += 1
        if df_5m['FVG_Down'].iloc[i]: # Bearish Box
            fig.add_shape(type="rect", x0=df_5m.index[i-1], x1=df_5m.index[i+1], y0=df_5m['Low'].iloc[i-1], y1=df_5m['High'].iloc[i+1],
                          fillcolor="rgba(255, 51, 102, 0.2)", line=dict(width=0))
            boxes += 1

    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    # Bottom Guidance
    c1, c2 = st.columns(2)
    with c1:
        st.success(f"🎯 BANK TARGET: {bank_tp:.2f}")
    with c2:
        st.error(f"🛑 PROTECTIVE SL: {bank_sl:.2f}")

    if boxes > 0:
        st.info(f"🔍 {boxes} Market Gaps detected. Banks usually return to these boxes before a big move.")

render_app()
